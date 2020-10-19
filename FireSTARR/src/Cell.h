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
#include <limits>
#include "Location.h"
#include "Util.h"
namespace firestarr
{
namespace topo
{
using SpreadKey = uint32;
/**
 * \brief A Location with a Slope, Aspect, and Fuel.
 */
class Cell
  : public Location
{
public:
  /**
   * \brief Default constructor
   */
  constexpr Cell() noexcept
    : Cell(MAX_ROWS + 1,
           MAX_COLUMNS + 1,
           numeric_limits<SlopeSize>::min(),
           numeric_limits<AspectSize>::min(),
           numeric_limits<FuelCodeSize>::min())
  {
  }
  /**
   * \brief Hash attributes into a Topo value
   * \param slope Slope
   * \param aspect Aspect
   * \param fuel Fuel
   * \return Hash
   */
  [[nodiscard]] static constexpr Topo hashCell(const SlopeSize slope,
                                               const AspectSize aspect,
                                               const FuelCodeSize& fuel) noexcept
  {
    // if slope is 0 make aspect north so less unique keys
    return static_cast<Topo>(fuel) << FuelShift
      | static_cast<Topo>(slope) << SlopeShift
      | static_cast<Topo>(0 == slope ? 0 : aspect) << AspectShift;
  }
  /**
   * \brief Construct from hash value
   * \param hash Hash defining all attributes
   */
  explicit constexpr Cell(const Topo hash) noexcept
    : Location(hash)
  {
  }
  /**
   * \brief Construct based on given attributes
   * \param hash Hash of row and column
   * \param slope Slope
   * \param aspect Aspect
   * \param fuel Fuel
   */
  constexpr Cell(const HashSize hash,
                 const SlopeSize slope,
                 const AspectSize aspect,
                 const FuelCodeSize& fuel) noexcept
    : Location(static_cast<Topo>(hash & HashMask) | hashCell(slope, aspect, fuel))
  {
  }
  /**
   * \brief Constructor
   * \param row Row
   * \param column Column
   * \param slope Slope
   * \param aspect Aspect
   * \param fuel Fuel
   */
  constexpr Cell(const Idx row,
                 const Idx column,
                 const SlopeSize slope,
                 const AspectSize aspect,
                 const FuelCodeSize& fuel) noexcept
    : Location(static_cast<Topo>(doHash(row, column))
      | hashCell(slope, aspect, fuel))
  {
  }
  /**
   * \brief A key defining Slope, Aspect, and Fuel, used for determining Cells that spread the same
   * \return A key defining Slope, Aspect, and Fuel
   */
  [[nodiscard]] constexpr SpreadKey key() const noexcept
  {
    // should be able to fit this in a uint32
    //constexpr auto key_mask = AspectMask | FuelMask | SlopeMask;
    //return static_cast<SpreadKey>((topo_data_ & key_mask) >> FuelShift);
    // can just shift since these are the only bits left after
    return static_cast<SpreadKey>(topo_data_ >> FuelShift);
  }
  /**
   * \brief Aspect (degrees)
   * \return Aspect (degrees)
   */
  [[nodiscard]] constexpr AspectSize aspect() const noexcept
  {
    return static_cast<AspectSize>((topo_data_ & AspectMask) >> AspectShift);
  }
  /**
   * \brief Fuel
   * \return Fuel
   */
  [[nodiscard]] constexpr FuelCodeSize fuelCode() const noexcept
  {
    return static_cast<FuelCodeSize>((topo_data_ & FuelMask) >> FuelShift);
  }
  /**
   * \brief Slope (degrees)
   * \return Slope (degrees)
   */
  [[nodiscard]] constexpr SlopeSize slope() const noexcept
  {
    return static_cast<SlopeSize>((topo_data_ & SlopeMask) >> SlopeShift);
  }
  /**
   * \brief Topo that contains Cell data
   * \return Topo that contains Cell data
   */
  [[nodiscard]] constexpr Topo topoHash() const noexcept
  {
    return static_cast<Topo>(topo_data_) & CellMask;
  }
protected:
  /*
   * Field                    Natural Range     Used Range      Bits    Bit Range
   * Row                      0 - 2047          0 - 2047        11      0 - 2047
   * Column                   0 - 2047          0 - 2047        11      0 - 2047
   * PADDING                                                    10
   * Fuel                     0 - 56            0 - 56          6       0 - 63
   * Aspect                   0 - 359           0 - 359         9       0 - 511
   * Slope                    0 - infinity      0 - 127         7       0 - 127
   * Extra                                                      10
   *
   * Rows and Columns are restricted to 2048 since that's what gets clipped out of
   * the GIS outputs.
   *
   * Fuel is tied to how many variations of percent conifer/dead fir we want to use, and
   * if we want to allow M1/M2/M3/M4 on their own, or just use the ones that are
   * automatically tied to the green-up.
   *
   * Aspect is calculated to be in degrees, so 0 - 359.
   *
   * Slope is truncated to 0 - 60 because that's the range that affects effective wind
   * speed for slopes, but there's an issue with this when it tries to calculate the
   * horizontal rate of spread since then the slope has been truncated and the distance
   * calculated will be wrong.
   */
  /**
   * \brief Shift for fuel bitmask
   */
  static constexpr uint32 FuelShift = LocationBits + 10;
  /**
   * \brief Number of bits in fuel bitmask
   */
  static constexpr uint32 FuelBits = 6;
  /**
   * \brief Bitmask for fuel information in Topo before shift
   */
  static constexpr Topo FuelBitMask = util::bit_mask<FuelBits, Topo>();
  static_assert(FuelBitMask == 0x3F);
  static_assert(FuelBitMask >= NUMBER_OF_FUELS);
  /**
   * \brief Bitmask for fuel information in Topo
   */
  static constexpr Topo FuelMask = FuelBitMask << FuelShift;
  /**
   * \brief Shift for aspect bitmask
   */
  static constexpr uint32 AspectShift = FuelBits + FuelShift;
  /**
   * \brief Number of bits in aspect bitmask
   */
  static constexpr uint32 AspectBits = 9;
  /**
   * \brief Bitmask for aspect in Topo before shift
   */
  static constexpr Topo AspectBitMask = util::bit_mask<AspectBits, Topo>();
  static_assert(AspectBitMask == 0x1FF);
  /**
   * \brief Bitmask for aspect in Topo
   */
  static constexpr Topo AspectMask = AspectBitMask << AspectShift;
  /**
   * \brief Shift for slope bitmask
   */
  static constexpr uint32 SlopeShift = AspectBits + AspectShift;
  /**
   * \brief Number of bits in slope bitmask
   */
  static constexpr uint32 SlopeBits = 7;
  /**
   * \brief Bitmask for slope in Topo before shift
   */
  static constexpr Topo SlopeBitMask = util::bit_mask<SlopeBits, Topo>();
  static_assert(SlopeBitMask == 0x7F);
  static_assert(SlopeBitMask >= MAX_SLOPE_FOR_FACTOR);
  /**
   * \brief Bitmask for slope in Topo
   */
  static constexpr Topo SlopeMask = SlopeBitMask << SlopeShift;
  /**
   * \brief Bitmask for Cell information in Topo
   */
  static constexpr Topo CellMask = HashMask | FuelMask | AspectMask | SlopeMask;
  static_assert(CellMask == 0x3FFFFF003FFFFF);
};
/**
 * \brief Less than operator
 * \param lhs First Cell
 * \param rhs Second Cell
 * \return Whether or not first is less than second
 */
constexpr bool operator<(const Cell& lhs, const Cell& rhs)
{
  return lhs.topoHash() < rhs.topoHash();
}
}
}
namespace std
{
/**
 * \brief Provides hashing of Cell objects
 */
template <>
struct hash<firestarr::topo::Cell>
{
  /**
   * \brief Provides hash for Cell objects
   * \param k Cell to get hash for
   * \return Hash value
   */
  std::size_t operator()(const firestarr::topo::Cell& k) const noexcept
  {
    return k.fullHash();
  }
};
}
