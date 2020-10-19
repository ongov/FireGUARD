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
#include "Cell.h"
#include "FWI.h"
#include "Point.h"
#include "Settings.h"
#include "Util.h"
namespace firestarr
{
namespace sim
{
/**
 * \brief The position within a Cell that a spreading point has.
 */
struct InnerPos
{
  /**
   * \brief X coordinate
   */
  double x;
  /**
   * \brief Y coordinate
   */
  double y;
  /**
   * \brief Constructor
   * \param x X coordinate
   * \param y Y coordinate
   */
  InnerPos(const double x, const double y) noexcept
    : x(x), y(y)
  {
  }
  /**
   * \brief Less than operator
   * \param rhs InnerPos to compare to
   * \return Whether or not this is less than the other
   */
  bool operator<(const InnerPos& rhs) const noexcept
  {
    if (x == rhs.x)
    {
      return y < rhs.y;
    }
    return x < rhs.x;
  }
  /**
   * \brief Equality operator
   * \param rhs InnerPos to compare to
   * \return Whether or not this is equivalent to the other
   */
  bool operator==(const InnerPos& rhs) const noexcept
  {
    return abs(x - rhs.x) < COMPARE_LIMIT && abs(y - rhs.y) < COMPARE_LIMIT;
  }
};
class Scenario;
/**
 * \brief Possible results of an attempt to spread.
 */
enum SpreadResult
{
  SPREAD_TOO_SLOW,
  SPREAD_IMPOSSIBLE,
  SPREAD_SCHEDULED
};
int calculate_nd_for_point(int elevation, const topo::Point& point) noexcept;
/**
 * \brief Information regarding spread within a Cell for a specific Scenario and time.
 */
class SpreadInfo
{
public:
  /**
   * \brief Lookup table for Slope Factor calculated from Percent Slope
   */
  static const SlopeTableArray SlopeTable;
  ~SpreadInfo() = default;
  /**
   * \brief Calculate fire spread for time and place
   * \param scenario Scenario this is spreading in
   * \param time Time spread is occurring
   * \param cell Cell spread is occurring in
   * \param nd Difference between date and the date of minimum foliar moisture content
   * \param weather FwiWeather to use for calculations
   */
  SpreadInfo(const Scenario& scenario,
             double time,
             const topo::Cell& cell,
             int nd,
             const wx::FwiWeather* weather);
  constexpr SpreadInfo(SpreadInfo&& rhs) noexcept = delete;
  constexpr SpreadInfo(const SpreadInfo& rhs) noexcept = delete;
  SpreadInfo& operator=(SpreadInfo&& rhs) noexcept = delete;
  SpreadInfo& operator=(const SpreadInfo& rhs) noexcept = delete;
  // static double calculateSpreadProbability(double ros);
  /**
   * \brief Determine rate of spread from probability of spread threshold
   * \param threshold Probability of spread threshold
   * \return Rate of spread at given threshold (m/min)
   */
  [[nodiscard]] static constexpr double calculateRosFromThreshold(const double threshold)
  {
    // for some reason it returns -nan instead of nan if it's 1, so return this instead
    if (1.0 == threshold)
    {
      return std::numeric_limits<double>::infinity();
    }
    if (0.0 == threshold)
    {
      return 0.0;
    }
    // NOTE: based off spread event probability from wotton
    // should be the inverse of calculateSpreadProbability()
    return 25.0 / 4.0 * log(-(exp(41.0 / 25.0) * threshold) / (threshold - 1));
  }
  /**
   * \brief Maximum intensity in any direction for spread (kW/m)
   * \return Maximum intensity in any direction for spread (kW/m)
   */
  [[nodiscard]] double maxIntensity() const noexcept { return max_intensity_; }
  /**
   * \brief Offsets from origin point that represent spread under these conditions
   * \return Offsets from origin point that represent spread under these conditions
   */
  [[nodiscard]] vector<InnerPos> offsets() const { return offsets_; }
  /**
   * \brief Whether or not there is no spread
   * \return Whether or not there is no spread
   */
  [[nodiscard]] constexpr bool isNotSpreading() const { return isInvalid(); }
  /**
   * \brief Difference between date and the date of minimum foliar moisture content
   * \return Difference between date and the date of minimum foliar moisture content
   */
  [[nodiscard]] constexpr int nd() const { return nd_; }
  /**
   * \brief FwiWeather used for spread
   * \return FwiWeather used for spread
   */
  [[nodiscard]] constexpr const wx::FwiWeather* weather() const { return weather_; }
  /**
   * \brief Wind used for spread
   * \return Wind used for spread
   */
  [[nodiscard]] constexpr const wx::Wind& wind() const { return weather()->wind(); }
  /**
   * \brief Fine Fuel Moisture Code used for spread
   * \return Fine Fuel Moisture Code used for spread
   */
  [[nodiscard]] constexpr const wx::Ffmc& ffmc() const { return weather()->ffmc(); }
  /**
   * \brief Build-up Index used for spread
   * \return Build-up Index used for spread
   */
  [[nodiscard]] constexpr const wx::Bui& bui() const { return weather()->bui(); }
  /**
   * \brief Duff Moisture Code used for spread
   * \return Duff Moisture Code used for spread
   */
  [[nodiscard]] constexpr const wx::Dmc& dmc() const { return weather()->dmc(); }
  /**
   * \brief Drought Code used for spread
   * \return Drought Code used for spread
   */
  [[nodiscard]] constexpr const wx::Dc& dc() const { return weather()->dc(); }
  /**
   * \brief FFMC effect used for spread
   * \return FFMC effect used for spread
   */
  [[nodiscard]] constexpr double ffmcEffect() const { return weather()->ffmcEffect(); }
  /**
   * \brief Time used for spread
   * \return Time used for spread
   */
  [[nodiscard]] constexpr double time() const { return time_; }
  /**
   * \brief Slope used for spread (%)
   * \return Slope used for spread (%)
   */
  [[nodiscard]] constexpr SlopeSize percentSlope() const { return cell_.slope(); }
  /**
   * \brief Head fire rate of spread (m/min)
   * \return Head fire rate of spread (m/min)
   */
  [[nodiscard]] constexpr double headRos() const { return head_ros_; }
  /**
   * \brief Slope factor calculated from percent slope
   * \return Slope factor calculated from percent slope
   */
  [[nodiscard]] constexpr double slopeFactor() const
  {
    // HACK: slope can be infinite, but anything > 60 is the same as 60
    // we already capped the percent slope when making the Cells
    return SlopeTable.at(percentSlope());
  }
  /**
   * \brief Calculate foliar moisture
   * \return Calculated foliar moisture
   */
  [[nodiscard]] constexpr double foliarMoisture() const
  {
    return nd_ >= 50
             ? 120.0
             : nd_ >= 30 && nd_ < 50
             ? 32.9 + 3.17 * nd_ - 0.0288 * nd_ * nd_
             : 85.0 + 0.0189 * nd_ * nd_;
  }
  /**
   * \brief Whether or not there is no spread for given conditions
   * \return Whether or not there is no spread for given conditions
   */
  [[nodiscard]] constexpr bool isInvalid() const { return -1 == head_ros_; }
private:
  /**
   * \brief Offsets from origin point that represent spread under these conditions
   */
  vector<InnerPos> offsets_{};
  /**
   * \brief Maximum intensity in any direction for spread (kW/m)
   */
  double max_intensity_;
  /**
   * \brief Cell in which this spread is happening
   */
  topo::Cell cell_;
  /**
   * \brief FwiWeather determining spread
   */
  const wx::FwiWeather* weather_;
  /**
   * \brief Time that spread is occurring
   */
  double time_;
  /**
   * \brief Head fire rate of spread (m/min)
   */
  double head_ros_;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Difference between date and the date of minimum foliar moisture content (from ST-X-3)
   */
  int nd_;
};
#pragma warning (pop)
}
}
