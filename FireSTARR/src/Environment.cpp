// Copyright (C) 2020  Queen's Printer for Ontario
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
// 
// Last Updated 2020-04-07 <Evens, Jordan (MNRF)>

#include "stdafx.h"
#include "Environment.h"
#include "EnvironmentInfo.h"
#include "FuelLookup.h"
#include "ProbabilityMap.h"
#include "Scenario.h"
namespace firestarr
{
namespace topo
{
Environment::~Environment()
{
  delete cells_;
}
template <class V, class T = V>
static V read_tiff_point(TIFF* tif,
                         GTIF* gtif,
                         const Point& point,
                         std::function<T(int, int)> convert)
{
  const data::GridBase grid_info = data::read_header<T>(tif, gtif);
  const auto coordinates = grid_info.findCoordinates(point, false);
  auto min_column = max(static_cast<Idx>(0),
                        static_cast<Idx>(std::get<1>(*coordinates) - MAX_COLUMNS /
                          static_cast<Idx>(2)));
  if (min_column + MAX_COLUMNS >= grid_info.columns())
  {
    min_column = grid_info.columns() - MAX_COLUMNS;
  }
  auto min_row = max(static_cast<Idx>(0),
                     static_cast<Idx>(std::get<0>(*coordinates) - MAX_COLUMNS /
                       static_cast<Idx>(2)));
  if (min_row + MAX_COLUMNS >= grid_info.rows())
  {
    min_row = grid_info.rows() - MAX_COLUMNS;
  }
  int tile_width;
  int tile_length;
  TIFFGetField(tif, TIFFTAG_TILEWIDTH, &tile_width);
  TIFFGetField(tif, TIFFTAG_TILELENGTH, &tile_length);
  const auto buf = _TIFFmalloc(TIFFTileSize(tif));
  const tsample_t smp{};
  const auto mid = MAX_COLUMNS / 2;
  const auto h = (min_row + mid) / tile_length * tile_length;
  const auto w = (min_column + mid) / tile_width * tile_width;
  const auto f_y = h - min_row - (h - min_row) / tile_length * tile_length;
  const auto y = static_cast<Idx>(tile_length - f_y);
  const auto f_x = w - min_column - (w - min_column) / tile_width * tile_width;
  const auto x = static_cast<Idx>(tile_width - f_x);
  TIFFReadTile(tif, buf, static_cast<uint32>(w), static_cast<uint32>(h), 0, smp);
  const auto offset = y * tile_length + x;
  V cur = *(static_cast<V*>(buf) + offset);
  _TIFFfree(buf);
  return convert(cur, grid_info.nodata());
}
template <class V, class T = V>
static V read_tiff_point(const string& filename,
                         const Point& point,
                         std::function<T(int, int)> convert)
{
  return data::with_tiff<V>(filename,
                            [&convert, &point](TIFF* tif, GTIF* gtif)
                            {
                              return read_tiff_point<T, V>(tif, gtif, point, convert);
                            });
}
template <class T>
static T read_tiff_point(const string& filename,
                         const Point& point)
{
  return read_tiff_point<T, T>(filename, point, util::no_convert<T>);
}
Environment Environment::load(const fuel::FuelLookup& lookup,
                              const Point& point,
                              const string& in_fuel,
                              const string& in_slope,
                              const string& in_aspect,
                              const string& in_elevation)
{
  logging::note("Fuel raster is %s", in_fuel.c_str());
  if (sim::Settings::runAsync())
  {
    auto fuel = async(launch::async,
                      [&in_fuel, &point, lookup]()
                      {
                        return FuelGrid::readTiff(in_fuel, point, lookup);
                      });
    auto slope = async(launch::async,
                       [&in_slope, &point]()
                       {
                         return SlopeGrid::readTiff(in_slope, point);
                       });
    auto aspect = async(launch::async,
                        [&in_aspect, &point]()
                        {
                          return AspectGrid::readTiff(in_aspect, point);
                        });
    auto elevation = async(launch::async,
                           [&in_elevation, &point]()
                           {
                             return read_tiff_point<ElevationSize>(
                               in_elevation,
                               point);
                           });
    return Environment(*unique_ptr<FuelGrid>(fuel.get()),
                       *unique_ptr<SlopeGrid>(slope.get()),
                       *unique_ptr<AspectGrid>(aspect.get()),
                       elevation.get());
  }
  // HACK: need to copy strings since closures do that above
  return Environment(*unique_ptr<FuelGrid>(
                       FuelGrid::readTiff(string(in_fuel), point, lookup)),
                     *unique_ptr<SlopeGrid>(SlopeGrid::readTiff(string(in_slope), point)),
                     *unique_ptr<AspectGrid>(
                       AspectGrid::readTiff(string(in_aspect), point)),
                     read_tiff_point<ElevationSize>(string(in_elevation), point));
}
sim::ProbabilityMap* Environment::makeProbabilityMap(const char* for_what,
                                                     const double time,
                                                     const double start_time,
                                                     const int min_value,
                                                     const int low_max,
                                                     const int med_max,
                                                     const int max_value) const
{
  return new sim::ProbabilityMap(for_what,
                                 time,
                                 start_time,
                                 min_value,
                                 low_max,
                                 med_max,
                                 max_value,
                                 *cells_);
}
Environment Environment::loadEnvironment(const fuel::FuelLookup& lookup,
                                         const string& path,
                                         const Point& point,
                                         const string& perimeter,
                                         const int year)
{
  logging::note("Using ignition point (%f, %f)", point.latitude(), point.longitude());
  logging::info("Running using inputs directory '%s'", path.c_str());
  auto rasters = util::find_rasters(path, year);
  auto best_x = numeric_limits<double>::max();
  auto best_y = numeric_limits<Idx>::max();
  unique_ptr<const EnvironmentInfo> env_info = nullptr;
  unique_ptr<data::GridBase> for_info = nullptr;
  if (!perimeter.empty())
  {
    for_info = make_unique<data::GridBase>(data::read_header<unsigned char>(perimeter));
    logging::info("Perimeter projection is %s", for_info->proj4().c_str());
  }
  for (const auto& raster : rasters)
  {
    auto fuel = raster;
    // make sure we're using a consistent directory separator
    std::replace(fuel.begin(), fuel.end(), '\\', '/');
    // HACK: assume there's only one instance of 'fuel' in the file name we want to change
    const auto find_what = string("fuel");
    const auto find_len = find_what.length();
    const auto find_start = fuel.find(find_what, fuel.find_last_of('/'));
    const auto aspect = string(fuel).replace(find_start, find_len, "aspect");
    const auto slope = string(fuel).replace(find_start, find_len, "slope");
    const auto elevation = string(fuel).replace(find_start, find_len, "dem");
    unique_ptr<const EnvironmentInfo> cur_info = EnvironmentInfo::loadInfo(
      fuel,
      slope,
      aspect,
      elevation);
    const auto cur_x = abs(point.longitude() - cur_info->meridian());
    logging::verbose("Zone %0.1f meridian is %0.2f degrees from point",
                     cur_info->zone(),
                     cur_x);
    // HACK: assume floating point is going to always be exactly the same result
    if ((nullptr == for_info || cur_info->meridian() == for_info->meridian())
      && cur_x <= best_x)
    {
      if (cur_x != best_x)
      {
        // if we're switching zones then we need to reset this
        best_y = numeric_limits<Idx>::max();
      }
      best_x = cur_x;
      // overwrite should delete current pointer
      const auto coordinates = cur_info->findCoordinates(point, false);
      if (nullptr != coordinates)
      {
        const auto cur_y = static_cast<Idx>(abs(
          std::get<0>(*coordinates) - cur_info->rows() / static_cast<Idx>(2)));
        if (cur_y < best_y)
        {
          env_info = std::move(cur_info);
          best_y = cur_y;
        }
      }
    }
  }
  logging::check_fatal(nullptr == env_info,
                       "Could not find an environment to use for (%f, %f)",
                       point.latitude(),
                       point.longitude());
  logging::debug("Best match for (%f, %f) is zone %0.2f with a meridian of %0.2f",
                 point.latitude(),
                 point.longitude(),
                 env_info->zone(),
                 env_info->meridian());
  logging::note("Projection is %s", env_info->proj4().c_str());
  // envInfo should get deleted automatically because it uses unique_ptr
  return env_info->load(lookup, point);
}
unique_ptr<Coordinates> Environment::findCoordinates(const Point& point,
                                                     const bool flipped) const
{
  return cells_->findCoordinates(point, flipped);
}
}
}
