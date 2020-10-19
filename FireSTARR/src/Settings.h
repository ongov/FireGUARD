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
#include <vector>
namespace firestarr
{
namespace sim
{
/**
 * \brief Value to use for actual weather observation stream
 */
const size_t ACTUALS = 0;
/**
 * \brief Difference minimum for doubles to be considered the same
 */
static const double COMPARE_LIMIT = 0.00001;
/**
 * \brief Reads and provides access to settings for the simulation.
 */
class Settings
{
public:
  /**
   * \brief Name of file to save weather to
   * \return Name of file to save weather to
   */
  [[nodiscard]] static const char* weatherFile() noexcept;
  /**
   * \brief Set name of file to save weather to
   * \param f Name of file to save weather to
   * \return None
   */
  static void setWeatherFile(string f);
  /**
   * \brief Root directory that raster inputs are stored in
   * \return Root directory that raster inputs are stored in
   */
  [[nodiscard]] static const char* rasterRoot() noexcept;
  /**
   * \brief Name of file that defines fuel lookup table
   * \return Name of file that defines fuel lookup table
   */
  [[nodiscard]] static const char* fuelLookupTable() noexcept;
  /**
   * \brief Whether or not to run things asynchronously where possible
   * \return Whether or not to run things asynchronously where possible
   */
  [[nodiscard]] static bool runAsync() noexcept;
  /**
   * \brief Set whether or not to run things asynchronously where possible
   * \param value Whether or not to run things asynchronously where possible
   * \return None
   */
  static void setRunAsync(bool value) noexcept;
  /**
   * \brief Minimum rate of spread before fire is considered to be spreading (m/min)
   * \return Minimum rate of spread before fire is considered to be spreading (m/min)
   */
  [[nodiscard]] static double minimumRos() noexcept;
  /**
   * \brief Maximum distance that the fire is allowed to spread in one step (# of cells)
   * \return Maximum distance that the fire is allowed to spread in one step (# of cells)
   */
  [[nodiscard]] static double maximumSpreadDistance() noexcept;
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the day
   * \return Minimum Fine Fuel Moisture Code required for spread during the day
   */
  [[nodiscard]] static double minimumFfmc() noexcept;
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the night
   * \return Minimum Fine Fuel Moisture Code required for spread during the night
   */
  [[nodiscard]] static double minimumFfmcAtNight() noexcept;
  /**
   * \brief Offset from sunrise at which the day is considered to start (hours)
   * \return Offset from sunrise at which the day is considered to start (hours)
   */
  [[nodiscard]] static double offsetSunrise() noexcept;
  /**
   * \brief Offset from sunrise at which the day is considered to end (hours)
   * \return Offset from sunrise at which the day is considered to end (hours)
   */
  [[nodiscard]] static double offsetSunset() noexcept;
  /**
   * \brief Default Percent Conifer to use for M1/M2 fuels where none is specified (%)
   * \return Percent of the stand that is composed of conifer (%)
   */
  [[nodiscard]] static int defaultPercentConifer() noexcept;
  /**
   * \brief Default Percent Dead Fir to use for M3/M4 fuels where none is specified (%)
   * \return Percent of the stand that is composed of dead fir (NOT percent of the fir that is dead) (%)
   */
  [[nodiscard]] static int defaultPercentDeadFir() noexcept;
  /**
   * \brief Maximum number of Iterations to run before checking if accuracy is good enough to stop
   * \return Maximum number of Iterations to run before checking if accuracy is good enough to stop
   */
  [[nodiscard]] static size_t simulationRecheckInterval() noexcept;
  /**
   * \brief Maximum number of Iterations to run at once if running async
   * \return Maximum number of Iterations to run at once if running async
   */
  [[nodiscard]] static size_t concurrentSimulationRounds() noexcept;
  /**
   * \brief Minimum number of Iterations to run before precision required to stop is considered
   * \return Minimum number of Iterations to run before precision required to stop is considered
   */
  [[nodiscard]] static size_t minimumSimulationRounds() noexcept;
  /**
   * \brief Maximum number of points in a Cell before they are condensed
   * \return 
   */
  [[nodiscard]] static size_t maxCellPoints() noexcept;
  /**
   * \brief The maximum fire intensity for the 'low' range of intensity (kW/m)
   * \return The maximum fire intensity for the 'low' range of intensity (kW/m)
   */
  [[nodiscard]] static int intensityMaxLow() noexcept;
  /**
   * \brief The maximum fire intensity for the 'moderate' range of intensity (kW/m)
   * \return The maximum fire intensity for the 'moderate' range of intensity (kW/m)
   */
  [[nodiscard]] static int intensityMaxModerate() noexcept;
  /**
   * \brief Set maximum grade target used for selecting WeatherSHIELD historic years
   * \param value Maximum grade target used for selecting WeatherSHIELD historic years
   * \return None
   */
  static void setMaxGrade(double value) noexcept;
  /**
   * \brief Maximum grade target used for selecting WeatherSHIELD historic years
   * \return Maximum grade target used for selecting WeatherSHIELD historic years
   */
  [[nodiscard]] static double maxGrade() noexcept;
  /**
   * \brief Confidence required before simulation stops (% / 100)
   * \return Confidence required before simulation stops (% / 100)
   */
  [[nodiscard]] static double confidenceLevel() noexcept;
  /**
   * \brief Maximum time simulation can run before it is ended and whatever results it has are used (s)
   * \return Maximum time simulation can run before it is ended and whatever results it has are used (s)
   */
  [[nodiscard]] static __int64 maximumTimeSeconds() noexcept;
  /**
   * \brief Weight to give to Scenario part of thresholds
   * \return Weight to give to Scenario part of thresholds
   */
  [[nodiscard]] static double thresholdScenarioWeight() noexcept;
  /**
   * \brief Weight to give to daily part of thresholds
   * \return Weight to give to daily part of thresholds
   */
  [[nodiscard]] static double thresholdDailyWeight() noexcept;
  /**
   * \brief Weight to give to hourly part of thresholds
   * \return Weight to give to hourly part of thresholds
   */
  [[nodiscard]] static double thresholdHourlyWeight() noexcept;
  /**
   * \brief Days to output probability contours for (1 is start date, 2 is day after, etc.)
   * \return Days to output probability contours for (1 is start date, 2 is day after, etc.)
   */
  [[nodiscard]] static vector<int> outputDateOffsets();
  /**
   * \brief Whatever the maximum value in the date offsets is
   * \return Whatever the maximum value in the date offsets is
   */
  [[nodiscard]] static int maxDateOffset() noexcept;
  Settings() = delete;
};
}
}
