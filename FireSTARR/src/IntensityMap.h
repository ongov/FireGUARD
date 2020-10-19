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
#include <memory>
#include <string>
#include <bitset>
#include "GridMap.h"
namespace firestarr
{
namespace topo
{
class Perimeter;
class Cell;
}
namespace sim
{
class ProbabilityMap;
class Model;
using BurnedData = std::bitset<MAX_COLUMNS * MAX_COLUMNS>;
/**
 * \brief Represents a map of intensities that cells have burned at for a single Scenario.
 */
class IntensityMap
{
  /**
   * \brief Mutex for parallel access
   */
  mutable mutex mutex_{};
public:
  /**
   * \brief Constructor
   * \param model Model to use extent from
   */
  explicit IntensityMap(const Model& model) noexcept;
  ~IntensityMap() noexcept;
  IntensityMap(const IntensityMap& rhs) = delete;
  IntensityMap(IntensityMap&& rhs) = delete;
  IntensityMap& operator=(const IntensityMap& rhs) = delete;
  IntensityMap& operator=(IntensityMap&& rhs) noexcept = delete;
  /**
   * \brief Number of rows in this extent
   * \return Number of rows in this extent
   */
  [[nodiscard]] constexpr Idx rows() const { return map_->rows(); }
  /**
   * \brief Number of columns in this extent
   * \return Number of columns in this extent
   */
  [[nodiscard]] constexpr Idx columns() const { return map_->columns(); }
  /**
   * \brief Set cells in the map to be burned based on Perimeter
   * \param perimeter Perimeter to burn cells based on
   */
  void applyPerimeter(const topo::Perimeter& perimeter) noexcept;
  /**
   * \brief Whether or not the Cell can burn
   * \param location Cell to check
   * \return Whether or not the Cell can burn
   */
  [[nodiscard]] bool canBurn(const topo::Cell& location) const;
  /**
   * \brief Whether or not the Cell with the given hash can burn
   * \param hash Hash for Cell to check
   * \return Whether or not the Cell with the given hash can burn
   */
  [[nodiscard]] bool canBurn(HashSize hash) const;
  /**
   * \brief Whether or not the Location can burn
   * \param location Location to check
   * \return Whether or not the Location can burn
   */
  [[nodiscard]] bool hasBurned(const Location& location) const;
  /**
   * \brief Whether or not the Location with the given hash can burn
   * \param hash Hash for Location to check
   * \return Whether or not the Location with the given hash can burn
   */
  [[nodiscard]] bool hasBurned(HashSize hash) const;
  /**
   * \brief Whether or not all Locations surrounding the given Location are burned
   * \param location Location to check
   * \return Whether or not all Locations surrounding the given Location are burned
   */
  [[nodiscard]] bool isSurrounded(const Location& location) const;
  /**
   * \brief Burn Location with given intensity
   * \param location Location to burn
   * \param intensity Intensity to burn with (kW/m)
   */
  void burn(const Location& location, IntensitySize intensity);
  /**
   * \brief Save contents to an ASCII file
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void saveToAsciiFile(const string& dir, const string& base_name) const;
  /**
   * \brief Size of the fire represented by this
   * \return Size of the fire represented by this
   */
  [[nodiscard]] double fireSize() const;
  /**
   * \brief Iterator for underlying GridMap
   * \return Iterator for underlying GridMap
   */
  [[nodiscard]] unordered_map<Location, IntensitySize>::const_iterator
  cbegin() const noexcept;
  /**
   * \brief Iterator for underlying GridMap
   * \return Iterator for underlying GridMap
   */
  [[nodiscard]] unordered_map<Location, IntensitySize>::const_iterator
  cend() const noexcept;
private:
  /**
   * \brief Model map is for
   */
  const Model& model_;
  /**
   * \brief Map of intensity that cells have burned  at
   */
  unique_ptr<data::GridMap<IntensitySize>> map_;
  /**
   * \brief bitset denoting cells that can no longer burn
   */
  BurnedData* is_burned_;
};
}
}
