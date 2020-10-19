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
#include <limits>
#include <list>
#include <string>
#include <unordered_map>
#include <utility>
#include "Grid.h"
namespace firestarr
{
namespace data
{
/**
 * \brief A GridData that uses an unordered_map for storage.
 * \tparam T Type of data after conversion from initialization type.
 * \tparam V Type of data used as an input when initializing.
 */
template <class T, class V = T>
class GridMap
  : public GridData<T, V, unordered_map<Location, T>>
{
public:
  /**
   * \brief Determine if Location has a value
   * \param location Location to determine if present in GridMap
   * \return Whether or not a value is present for the Location
   */
  [[nodiscard]] bool contains(const Location& location) const
  {
    return this->data.end() != this->data.find(location);
  }
  /**
   * \brief Retrieve value at Location
   * \param location Location to get value for
   * \return Value at Location
   */
  [[nodiscard]] T at(const Location& location) const override
  {
    const auto value = this->data.find(location);
    if (value == this->data.end())
    {
      return this->noData();
    }
    return get<1>(*value);
  }
  /**
   * \brief Set value at Location
   * \param location Location to set value for
   * \param value Value to set at Location
   */
  void set(const Location& location, const T value) override
  {
    const auto seek = this->data.find(location);
    if (seek == this->data.end())
    {
      this->data.emplace(location, value);
    }
    else
    {
      this->data.at(location) = value;
    }
    assert(at(location) == value);
  }
  ~GridMap() = default;
  /**
   * \brief Constructor
   * \param cell_size Cell width and height (m)
   * \param rows Number of rows
   * \param columns Number of columns
   * \param no_data Value that represents no data
   * \param nodata Integer value that represents no data
   * \param xllcorner Lower left corner X coordinate (m)
   * \param yllcorner Lower left corner Y coordinate (m)
   * \param proj4 Proj4 projection definition
   */
  GridMap(const double cell_size,
          const Idx rows,
          const Idx columns,
          T no_data,
          const int nodata,
          const double xllcorner,
          const double yllcorner,
          string&& proj4)
    : GridData<T, V, unordered_map<Location, T>>(cell_size,
                                                 rows,
                                                 columns,
                                                 no_data,
                                                 nodata,
                                                 xllcorner,
                                                 yllcorner,
                                                 std::forward<string>(proj4),
                                                 unordered_map<Location, T>())
  {
    constexpr auto max_hash = numeric_limits<HashSize>::max();
    // HACK: we don't want overflow errors but we want to play with the hash size
    const auto max_columns = static_cast<double>(max_hash) /
      static_cast<double>(this->rows());
    logging::check_fatal(this->columns() >= max_columns,
                         "Grid is too big for cells to be hashed - "
                         "recompile with a larger HashSize value");
    // HACK: reserve space for this based on how big our Idx is because that
    // tells us how many cells there could be
    // HACK: divide because we expect most perimeters to be fairly small but we
    // want it to be reasonably large
    this->data.reserve(static_cast<size_t>(numeric_limits<Idx>::max() / 4));
  }
  /**
   * \brief Construct empty GridMap with same extent as given Grid
   * \param grid Grid to use extent from
   */
  explicit GridMap(const Grid<T, V>& grid)
    : GridMap<T, V>(grid.cellSize(),
                    grid.rows(),
                    grid.columns(),
                    grid.noData(),
                    grid.nodata(),
                    grid.xllcorner(),
                    grid.yllcorner(),
                    grid.proj4())
  {
  }
  /**
   * \brief Construct empty GridMap with same extent as given Grid 
   * \param grid_info Grid to use extent from
   * \param no_data Value to use for no data
   */
  GridMap(const GridBase& grid_info, T no_data)
    : GridMap<T, V>(grid_info.cellSize(),
                    grid_info.rows(),
                    grid_info.columns(),
                    no_data,
                    static_cast<int>(no_data),
                    grid_info.xllcorner(),
                    grid_info.yllcorner(),
                    string(grid_info.proj4()))
  {
  }
  /**
   * \brief Move constructor
   * \param rhs GridMap to move from
   */
  GridMap(GridMap&& rhs) noexcept
    : GridData(std::move(rhs))
  {
    this->data = std::move(rhs.data);
  }
  /**
   * \brief Copy constructor
   * \param rhs GridMap to copy from
   */
  explicit GridMap(const GridMap& rhs)
    : GridData(rhs)
  {
    this->data = rhs.data;
  }
  /**
   * \brief Move assignment
   * \param rhs GridMap to move from
   * \return This, after assignment
   */
  GridMap& operator=(GridMap&& rhs) noexcept
  {
    if (this != &rhs)
    {
      this->data = std::move(rhs.data);
    }
    return *this;
  }
  /**
   * \brief Copy assignment
   * \param rhs GridMap to copy from
   * \return This, after assignment
   */
  GridMap& operator=(const GridMap& rhs)
  {
    if (this != &rhs)
    {
      this->data = rhs.data;
    }
    return *this;
  }
  /**
   * \brief Clear data from GridMap
   */
  void clear() noexcept
  {
    this->data.clear();
  }
  /**
   * \brief Save GridMap contents to .asc file
   * \param dir Directory to save into
   * \param base_name File base name to use
   */
  void saveToAsciiFile(const string& dir, const string& base_name) const
  {
    saveToAsciiFile<V>(dir, base_name, [](V value) { return value; });
  }
  /**
   * \brief Save GridMap contents to .asc file
   * \tparam R Type to be written to .asc file
   * \param dir Directory to save into
   * \param base_name File base name to use
   * \param convert Function to convert from V to R
   */
  template <class R>
  void saveToAsciiFile(const string& dir,
                       const string& base_name,
                       std::function<R(V value)> convert) const
  {
    Idx min_row = this->rows();
    int16 max_row = 0;
    Idx min_column = this->columns();
    Idx max_column = 0;
    for (const auto& kv : this->data)
    {
      const Idx r = kv.first.row();
      const Idx c = kv.first.column();
      min_row = min(min_row, r);
      max_row = max(max_row, r);
      min_column = min(min_column, c);
      max_column = max(max_column, c);
    }
    // do this so that we take the center point when there's no data since it should
    // stay the same if the grid is centered on the fire
    if (min_row > max_row)
    {
      min_row = max_row = this->rows() / 2;
    }
    if (min_column > max_column)
    {
      min_column = max_column = this->columns() / 2;
    }
    logging::verbose("Lower left corner is (%d, %d)", min_column, min_row);
    logging::verbose("Upper right corner is (%d, %d)", max_column, max_row);
    const double xll = this->xllcorner() + min_column * this->cellSize();
    // offset is different for y since it's flipped
    const double yll = this->yllcorner() + (min_row) * this->
      cellSize();
    logging::verbose("Lower left corner is (%f, %f)", xll, yll);
    // HACK: make sure it's always at least 1
    const auto num_rows = static_cast<double>(max_row) - min_row + 1;
    const auto num_columns = static_cast<double>(max_column) - min_column + 1;
    ofstream out;
    out.open(dir + base_name + ".asc");
    write_ascii_header(out,
                       num_columns,
                       num_rows,
                       xll,
                       yll,
                       this->cellSize(),
                       static_cast<double>(this->noData()));
    for (Idx ro = 0; ro < num_rows; ++ro)
    {
      // HACK: do this so we always get at least one pixel in output
      // need to output in reverse order since (0,0) is bottom left
      const Idx r = static_cast<Idx>(max_row) - ro;
      for (Idx co = 0; co < num_columns; ++co)
      {
        const Location idx(static_cast<Idx>(r), static_cast<Idx>(min_column + co));
        // HACK: use + here so that it gets promoted to a printable number
        //       prevents char type being output as characters
        out << +((this->data.find(idx) != this->data.end())
                   ? convert(this->data.at(idx))
                   : this->noData()) << " ";
      }
      out << "\n";
    }
    out.close();
    this->createPrj(dir, base_name);
  }
  /**
   * \brief Save GridMap contents to .asc file as probability
   * \param dir Directory to save into
   * \param base_name File base name to use
   * \param divisor Number of simulations to divide by to calculate probability per cell
   */
  void saveToProbabilityFile(const string& dir,
                             const string& base_name,
                             const double divisor) const
  {
    saveToAsciiFile<double>(dir,
                            base_name,
                            [divisor](V value) { return value / divisor; });
  }
  /**
   * \brief Calculate area for cells that have a value (ha)
   * \return Area for cells that have a value (ha)
   */
  [[nodiscard]] double fireSize() const noexcept
  {
    // we know that every cell is a key, so we convert that to hectares
    const double per_width = (this->cellSize() / 100.0);
    // cells might have 0 as a value, but those shouldn't affect size
    return static_cast<double>(this->data.size()) * per_width * per_width;
  }
  /**
   * \brief Make a list of all Locations that are on the edge of cells with a value
   * \return A list of all Locations that are on the edge of cells with a value
   */
  [[nodiscard]] list<Location> makeEdge() const
  {
    list<Location> edge{};
    for (const auto& kv : this->data)
    {
      auto loc = kv.first;
      auto on_edge = false;
      for (Idx r = -1; !on_edge && r <= 1; ++r)
      {
        const Idx row_index = loc.row() + r;
        if (!(row_index < 0 || row_index >= this->rows()))
        {
          for (Idx c = -1; !on_edge && c <= 1; ++c)
          {
            const Idx col_index = loc.column() + c;
            if (!(col_index < 0 || col_index >= this->columns())
              && this->data.find(Location(row_index, col_index)) == this->data.end())
            {
              on_edge = true;
            }
          }
        }
      }
      if (on_edge)
      {
        edge.push_back(loc);
      }
    }
    logging::info("Created edge for perimeter with length %lu m",
                  static_cast<size_t>(this->cellSize() * edge.size()));
    return edge;
  }
  /**
   * \brief Make a list of all Locations that have a value
   * \return A list of all Locations that have a value
   */
  [[nodiscard]] list<Location> makeList() const
  {
    list<Location> result{this->data.size()};
    std::transform(this->data.begin(),
                   this->data.end(),
                   result.begin(),
                   [](const pair<const Location, const T>& kv) { return kv.first; });
    return result;
  }
};
}
}
