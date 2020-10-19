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

#pragma once
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include "Grid.h"
#include "Util.h"
namespace firestarr
{
namespace data
{
/**
 * \brief A GridData<T, V, const vector<T>> that cannot change once initialized.
 * \tparam T The initialization value type.
 * \tparam V The initialized value type.
 */
template <class T, class V = T>
class ConstantGrid
  : public GridData<T, V, const vector<T>>
{
public:
  /**
   * \brief Value for grid at given Location.
   * \param location Location to get value for.
   * \return Value at grid Location.
   */
  [[nodiscard]] constexpr T at(const Location& location) const noexcept override
  {
    return at(location.hash());
  }
  /**
   * \brief Value for grid at given Location.
   * \param hash HashSize hash for Location to get value for.
   * \return Value at grid Location.
   */
  [[nodiscard]] constexpr T at(const HashSize hash) const noexcept
  {
    return this->data.at(hash);
  }
  /**
   * \brief Throw an error because ConstantGrid can't change values.
   */
  // ! @cond Doxygen_Suppress
  void set(const Location&, const T) override
  // ! @endcond
  {
    throw runtime_error("Cannot change ConstantGrid");
  }
  ~ConstantGrid() = default;
  ConstantGrid(const ConstantGrid& rhs) noexcept = delete;
  ConstantGrid(ConstantGrid&& rhs) noexcept = delete;
  ConstantGrid& operator=(const ConstantGrid& rhs) noexcept = delete;
  ConstantGrid& operator=(ConstantGrid&& rhs) noexcept = delete;
  /**
   * \brief Constructor
   * \param cell_size Cell width and height (m)
   * \param rows Number of rows
   * \param columns Number of columns
   * \param no_data Value to use for no data
   * \param nodata Integer value that represents no data
   * \param xllcorner Lower left corner X coordinate (m)
   * \param yllcorner Lower left corner Y coordinate (m)
   * \param proj4 Proj4 projection definition 
   * \param data Data to set as grid data
   */
  ConstantGrid(const double cell_size,
               const Idx rows,
               const Idx columns,
               const T no_data,
               const int nodata,
               const double xllcorner,
               const double yllcorner,
               string&& proj4,
               vector<T>&& data)
    : GridData(cell_size,
               rows,
               columns,
               no_data,
               nodata,
               xllcorner,
               yllcorner,
               std::forward<string>(proj4),
               std::move(data))
  {
  }
  /**
   * \brief Constructor
   * \param cell_size Cell width and height (m)
   * \param rows Number of rows
   * \param columns Number of columns
   * \param no_data Value to use for no data
   * \param nodata Integer value that represents no data
   * \param xllcorner Lower left corner X coordinate (m)
   * \param yllcorner Lower left corner Y coordinate (m)
   * \param proj4 Proj4 projection definition
   * \param initialization_value Value to initialize entire grid with
   */
  ConstantGrid(const double cell_size,
               const Idx rows,
               const Idx columns,
               const T& no_data,
               const int nodata,
               const double xllcorner,
               const double yllcorner,
               const string& proj4,
               const T& initialization_value) noexcept
    : ConstantGrid(cell_size,
                   rows,
                   columns,
                   no_data,
                   nodata,
                   xllcorner,
                   yllcorner,
                   proj4,
                   std::move(vector<T>(static_cast<size_t>(rows) * MAX_COLUMNS,
                                       initialization_value)))
  {
  }
  /**
   * \brief Read a section of a TIFF into a ConstantGrid
   * \param filename File name to read from
   * \param tif Pointer to open TIFF denoted by filename
   * \param gtif Pointer to open geotiff denoted by filename
   * \param point Point to center ConstantGrid on
   * \param convert Function taking int and nodata int value that returns T
   * \return ConstantGrid containing clipped data for TIFF
   */
  [[nodiscard]] static ConstantGrid<T, V>* readTiff(const string& filename,
                                                    TIFF* tif,
                                                    GTIF* gtif,
                                                    const topo::Point& point,
                                                    std::function<T(int, int)> convert)
  {
    V min_value = std::numeric_limits<V>::max();
    V max_value = std::numeric_limits<V>::min();
    const GridBase grid_info = read_header<T>(tif, gtif);
    const auto coordinates = grid_info.findCoordinates(point, false);
    auto min_column = max(static_cast<Idx>(0),
                          static_cast<Idx>(std::get<1>(*coordinates) - MAX_COLUMNS /
                            static_cast<Idx>(2)));
    if (min_column + MAX_COLUMNS >= grid_info.columns())
    {
      min_column = grid_info.columns() - MAX_COLUMNS;
    }
    const auto max_column = min_column + MAX_COLUMNS;
    auto min_row = max(static_cast<Idx>(0),
                       static_cast<Idx>(std::get<0>(*coordinates) - MAX_COLUMNS /
                         static_cast<Idx>(2)));
    if (min_row + MAX_COLUMNS >= grid_info.rows())
    {
      min_row = grid_info.rows() - MAX_COLUMNS;
    }
    const auto max_row = min_row + MAX_COLUMNS;
    const Idx offset_x = -min_column;
    const Idx offset_y = -min_row;
    T no_data = convert(grid_info.nodata(), grid_info.nodata());
    vector<T> values(MAX_COLUMNS * MAX_COLUMNS, no_data);
    int tile_width;
    int tile_length;
    TIFFGetField(tif, TIFFTAG_TILEWIDTH, &tile_width);
    TIFFGetField(tif, TIFFTAG_TILELENGTH, &tile_length);
    const auto buf = _TIFFmalloc(TIFFTileSize(tif));
    const tsample_t smp{};
    for (auto h = 0; h < grid_info.rows(); h += tile_length)
    {
      const auto y_min = static_cast<Idx>(max(0, min_row - h));
      const auto y_limit = min(tile_length,
                               min(static_cast<int>(grid_info.rows()), max_row) - h);
      for (auto w = 0; w < grid_info.columns(); w += tile_width)
      {
        TIFFReadTile(tif, buf, static_cast<uint32>(w), static_cast<uint32>(h), 0, smp);
        const auto x_min = static_cast<Idx>(max(0, min_column - w));
        const auto x_limit = min(tile_width,
                                 min(static_cast<int>(grid_info.columns()),
                                     max_column) - w);
        for (auto y = y_min; y < y_limit; ++y)
        {
          // read in so that (0, 0) has a hash of 0
          const Idx i = MAX_COLUMNS - (static_cast<Idx>(h) + y + offset_y + 1);
          for (auto x = x_min; x < x_limit; ++x)
          {
            const auto cur_hash = static_cast<HashSize>(i) * MAX_COLUMNS + w + x +
              offset_x;
            const auto offset = y * tile_length + x;
            V cur = *(static_cast<V*>(buf) + offset);
            min_value = min(cur, min_value);
            max_value = max(cur, max_value);
            values.at(cur_hash) = convert(cur, grid_info.nodata());
          }
        }
      }
    }
    _TIFFfree(buf);
    const auto new_xll = grid_info.xllcorner() - offset_x * grid_info.cellSize();
    const auto new_yll = grid_info.yllcorner() + (static_cast<double>(grid_info.rows()) -
      max_row) * grid_info.cellSize();
    logging::check_fatal(new_yll < grid_info.yllcorner(),
                         "New yllcorner is outside original grid");
    logging::note("Translated lower left is (%f, %f) from (%f, %f)",
                  new_xll,
                  new_yll,
                  grid_info.xllcorner(),
                  grid_info.yllcorner());
    auto result = new ConstantGrid<T, V>(grid_info.cellSize(),
                                         MAX_COLUMNS,
                                         MAX_COLUMNS,
                                         no_data,
                                         grid_info.nodata(),
                                         new_xll,
                                         new_yll,
                                         string(grid_info.proj4()),
                                         std::move(values));
    auto new_location = result->findCoordinates(point, true);
    logging::check_fatal(nullptr == new_location, "Invalid location after reading");
    logging::note("Coordinates are (%d, %d => %f, %f)",
                  std::get<0>(*new_location),
                  std::get<1>(*new_location),
                  std::get<0>(*new_location) + std::get<3>(*new_location) / 1000.0,
                  std::get<1>(*new_location) + std::get<2>(*new_location) / 1000.0);
    logging::note("Values for %s range from %d to %d",
                  filename.c_str(),
                  min_value,
                  max_value);
    return result;
  }
  /**
   * \brief Read a section of a TIFF into a ConstantGrid
   * \param filename File name to read from
   * \param point Point to center ConstantGrid on
   * \param convert Function taking int and nodata int value that returns T
   * \return ConstantGrid containing clipped data for TIFF
   */
  [[nodiscard]] static ConstantGrid<T, V>* readTiff(const string& filename,
                                                    const topo::Point& point,
                                                    std::function<T(int, int)> convert)
  {
    return with_tiff<ConstantGrid<T, V>*>(
      filename,
      [&filename, &convert, &point](TIFF* tif, GTIF* gtif)
      {
        return readTiff(filename, tif, gtif, point, convert);
      });
  }
  /**
   * \brief Read a section of a TIFF into a ConstantGrid
   * \param filename File name to read from
   * \param point Point to center ConstantGrid on
   * \return ConstantGrid containing clipped data for TIFF
   */
  [[nodiscard]] static ConstantGrid<T, T>* readTiff(const string& filename,
                                                    const topo::Point& point)
  {
    return readTiff(filename, point, util::no_convert<T>);
  }
private:
  /**
   * \brief Constructor
   * \param grid_info GridBase defining Grid area
   * \param no_data Value that represents no data
   * \param values Values to initialize grid with
   */
  ConstantGrid(const GridBase& grid_info, const T& no_data, vector<T>&& values)
    : ConstantGrid(grid_info.cellSize(),
                   grid_info.rows(),
                   grid_info.columns(),
                   no_data,
                   grid_info.nodata(),
                   grid_info.xllcorner(),
                   grid_info.yllcorner(),
                   string(grid_info.proj4()),
                   std::move(values))
  {
    logging::check_fatal(
      this->data.size() != static_cast<size_t>(grid_info.rows()) * MAX_COLUMNS,
      "Invalid grid size");
  }
};
}
}
