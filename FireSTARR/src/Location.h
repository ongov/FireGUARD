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
#include "Util.h"
namespace firestarr
{
namespace topo
{
/**
 * \brief A location with a row and column.
 */
class Location
{
public:
  Location() = default;
  /**
   * \brief Construct using hash of row and column
   * \param hash HashSize derived form row and column
   */
  explicit constexpr Location(const HashSize hash) noexcept
    : topo_data_(hash & HashMask)
  {
  }
  /**
   * \brief Constructor
   * \param row Row
   * \param column Column
   */
  constexpr Location(const Idx row, const Idx column) noexcept
    : Location(doHash(row, column))
  {
  }
  /**
   * \brief Row
   * \return Row
   */
  [[nodiscard]] constexpr Idx row() const noexcept
  {
    return static_cast<Idx>(hash() / MAX_COLUMNS);
  }
  /**
   * \brief Column
   * \return Column
   */
  [[nodiscard]] constexpr Idx column() const noexcept
  {
    return static_cast<Idx>(hash() % MAX_COLUMNS);
  }
  /**
   * \brief Hash derived from row and column
   * \return Hash derived from row and column
   */
  [[nodiscard]] constexpr HashSize hash() const noexcept
  {
    // can get away with just casting because all the other bits are outside this area
    return static_cast<HashSize>(topo_data_);
  }
  /**
   * \brief Equality operator
   * \param rhs Location to compare to
   * \return Whether or not these are equivalent
   */
  [[nodiscard]] constexpr bool operator==(const Location& rhs) const noexcept
  {
    return hash() == rhs.hash();
  }
  /**
   * \brief Inequality operator
   * \param rhs Location to compare to
   * \return Whether or not these are not equivalent
   */
  [[nodiscard]] constexpr bool operator!=(const Location& rhs) const noexcept
  {
    return !(*this == rhs);
  }
  /**
   * \brief Full stored hash that may contain data from subclasses
   * \return Full stored hash that may contain data from subclasses
   */
  [[nodiscard]] constexpr Topo fullHash() const { return topo_data_; }
protected:
  /**
   * \brief Stored hash that contains row and column data
   */
  Topo topo_data_;
  /**
   * \brief Number of bits to use for storing location data
   */
  static constexpr uint32 LocationBits = 22;
  /**
   * \brief Hash mask for bits being used for location data
   */
  static constexpr Topo HashMask = util::bit_mask<LocationBits, Topo>();
  static_assert(HashMask == 0x3FFFFF);
  static_assert(HashMask == MAX_COLUMNS * MAX_ROWS - 1);
  /**
   * \brief Construct with given hash that may contain data from subclasses
   * \param topo Hash to store
   */
  explicit constexpr Location(const Topo& topo) noexcept
    : topo_data_(topo)
  {
  }
  /**
   * \brief Create a hash from given values
   * \param row Row
   * \param column Column
   * \return Hash
   */
  [[nodiscard]] static constexpr HashSize doHash(
    const Idx row,
    const Idx column) noexcept
  {
    return static_cast<HashSize>(row) * static_cast<HashSize>(MAX_COLUMNS) +
      static_cast<HashSize>(column);
  }
};
}
}
