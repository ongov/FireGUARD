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
#include "Settings.h"
#include "Log.h"
#include "Trim.h"
namespace firestarr::sim
{
template <class T>
static vector<T> parse_list(string str, T (*convert)(const string& s))
{
  vector<int> result{};
  // static const vector<int> OUTPUT_DATE_OFFSETS = { 1, 2, 3, 7, 14, 28 };
  logging::check_fatal(str[0] != '{', "Expected list starting with '{'");
  istringstream iss(str.substr(1));
  while (getline(iss, str, ','))
  {
    // need to make sure this isn't an empty list
    if (0 != strcmp("}", str.c_str()))
    {
      result.push_back(convert(str));
    }
  }
  return result;
}
/**
 * \brief Settings implementation class
 */
class SettingsImplementation
{
public:
  ~SettingsImplementation() = default;
  SettingsImplementation(const SettingsImplementation& rhs) = delete;
  SettingsImplementation(SettingsImplementation&& rhs) = delete;
  SettingsImplementation& operator=(const SettingsImplementation& rhs) = delete;
  SettingsImplementation& operator=(SettingsImplementation&& rhs) = delete;
  static SettingsImplementation& instance() noexcept;
  /**
   * \brief Name of file to save weather to
   * \return Name of file to save weather to
   */
  [[nodiscard]] const char* weatherFile() const noexcept { return weather_file_.c_str(); }
  /**
   * \brief Set name of file to save weather to
   * \param f Name of file to save weather to
   */
  void setWeatherFile(const string f) { weather_file_ = f; }
  /**
   * \brief Root directory that raster inputs are stored in
   * \return Root directory that raster inputs are stored in
   */
  [[nodiscard]] const char* rasterRoot() const noexcept { return raster_root_.c_str(); }
  /**
   * \brief Name of file that defines fuel lookup table
   * \return Name of file that defines fuel lookup table
   */
  [[nodiscard]] const char* fuelLookupTable() const noexcept
  {
    return fuel_lookup_table_.c_str();
  }
  /**
   * \brief Minimum rate of spread before fire is considered to be spreading (m/min)
   * \return Minimum rate of spread before fire is considered to be spreading (m/min)
   */
  [[nodiscard]] constexpr double minimumRos() const noexcept { return minimum_ros_; }
  /**
   * \brief Maximum distance that the fire is allowed to spread in one step (# of cells)
   * \return Maximum distance that the fire is allowed to spread in one step (# of cells)
   */
  [[nodiscard]] constexpr double maximumSpreadDistance() const noexcept
  {
    return maximum_spread_distance_;
  }
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the day
   * \return Minimum Fine Fuel Moisture Code required for spread during the day
   */
  [[nodiscard]] constexpr double minimumFfmc() const noexcept { return minimum_ffmc_; }
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the night
   * \return Minimum Fine Fuel Moisture Code required for spread during the night
   */
  [[nodiscard]] constexpr double minimumFfmcAtNight() const noexcept
  {
    return minimum_ffmc_at_night_;
  }
  /**
   * \brief Offset from sunrise at which the day is considered to start (hours)
   * \return Offset from sunrise at which the day is considered to start (hours)
   */
  [[nodiscard]] constexpr double offsetSunrise() const noexcept
  {
    return offset_sunrise_;
  }
  /**
   * \brief Offset from sunrise at which the day is considered to end (hours)
   * \return Offset from sunrise at which the day is considered to end (hours)
   */
  [[nodiscard]] constexpr double offsetSunset() const noexcept { return offset_sunset_; }
  /**
   * \brief Default Percent Conifer to use for M1/M2 fuels where none is specified (%)
   * \return Percent of the stand that is composed of conifer (%)
   */
  [[nodiscard]] constexpr int defaultPercentConifer() const noexcept
  {
    return default_percent_conifer_;
  }
  /**
   * \brief Default Percent Dead Fir to use for M3/M4 fuels where none is specified (%)
   * \return Percent of the stand that is composed of dead fir (NOT percent of the fir that is dead) (%)
   */
  [[nodiscard]] constexpr int defaultPercentDeadFir() const noexcept
  {
    return default_percent_dead_fir_;
  }
  /**
   * \brief Maximum number of points in a Cell before they are condensed
   * \return Maximum number of points in a Cell before they are condensed
   */
  [[nodiscard]] constexpr size_t maxCellPoints() const noexcept
  {
    return max_cell_points_;
  }
  /**
   * \brief The maximum fire intensity for the 'low' range of intensity (kW/m)
   * \return The maximum fire intensity for the 'low' range of intensity (kW/m)
   */
  [[nodiscard]] constexpr int intensityMaxLow() const noexcept
  {
    return intensity_max_low_;
  }
  /**
   * \brief The maximum fire intensity for the 'moderate' range of intensity (kW/m)
   * \return The maximum fire intensity for the 'moderate' range of intensity (kW/m)
   */
  [[nodiscard]] constexpr int intensityMaxModerate() const noexcept
  {
    return intensity_max_moderate_;
  }
  /**
   * \brief Maximum number of Iterations to run before checking if accuracy is good enough to stop
   * \return Maximum number of Iterations to run before checking if accuracy is good enough to stop
   */
  [[nodiscard]] constexpr size_t simulationRecheckInterval() const noexcept
  {
    return simulation_recheck_interval_;
  }
  /**
   * \brief Maximum number of Iterations to run at once if running async
   * \return Maximum number of Iterations to run at once if running async
   */
  [[nodiscard]] constexpr size_t concurrentSimulationRounds() const noexcept
  {
    return concurrent_simulation_rounds_;
  }
  /**
   * \brief Minimum number of Iterations to run before precision required to stop is considered
   * \return Minimum number of Iterations to run before precision required to stop is considered
   */
  [[nodiscard]] constexpr size_t minimumSimulationRounds() const noexcept
  {
    return minimum_simulation_rounds_;
  }
  /**
   * \brief Set maximum grade target used for selecting WeatherSHIELD historic years
   * \param value Maximum grade target used for selecting WeatherSHIELD historic years
   */
  void setMaxGrade(const double value) noexcept
  {
    max_grade_ = value;
  }
  /**
   * \brief Maximum grade target used for selecting WeatherSHIELD historic years
   * \return Maximum grade target used for selecting WeatherSHIELD historic years
   */
  [[nodiscard]] constexpr double maxGrade() const noexcept { return max_grade_; }
  /**
   * \brief Confidence required before simulation stops (% / 100)
   * \return Confidence required before simulation stops (% / 100)
   */
  [[nodiscard]] constexpr double confidenceLevel() const noexcept
  {
    return confidence_level_;
  }
  /**
   * \brief Maximum time simulation can run before it is ended and whatever results it has are used (s)
   * \return Maximum time simulation can run before it is ended and whatever results it has are used (s)
   */
  [[nodiscard]] constexpr __int64 maximumTimeSeconds() const noexcept
  {
    return maximum_time_seconds_;
  }
  /**
   * \brief Weight to give to Scenario part of thresholds
   * \return Weight to give to Scenario part of thresholds
   */
  [[nodiscard]] constexpr double thresholdScenarioWeight() const noexcept
  {
    return threshold_scenario_weight_;
  }
  /**
   * \brief Weight to give to daily part of thresholds
   * \return Weight to give to daily part of thresholds
   */
  [[nodiscard]] constexpr double thresholdDailyWeight() const noexcept
  {
    return threshold_daily_weight_;
  }
  /**
   * \brief Weight to give to hourly part of thresholds
   * \return Weight to give to hourly part of thresholds
   */
  [[nodiscard]] constexpr double thresholdHourlyWeight() const noexcept
  {
    return threshold_hourly_weight_;
  }
  /**
   * \brief Days to output probability contours for (1 is start date, 2 is day after, etc.)
   * \return Days to output probability contours for (1 is start date, 2 is day after, etc.)
   */
  [[nodiscard]] vector<int> outputDateOffsets() const { return output_date_offsets_; }
  /**
   * \brief Whatever the maximum value in the date offsets is
   * \return Whatever the maximum value in the date offsets is
   */
  [[nodiscard]] constexpr int maxDateOffset() const noexcept { return max_date_offset_; }
private:
  /**
   * \brief Read settings from a file
   * \param filename File name to read from
   */
  explicit SettingsImplementation(const char* filename) noexcept;
  /**
   * \brief Mutex for parallel access
   */
  mutex mutex_;
  /**
   * \brief Name of file to save weather to
   */
  string weather_file_;
  /**
   * \brief Root directory that raster inputs are stored in
   */
  string raster_root_;
  /**
   * \brief Name of file that defines fuel lookup table
   */
  string fuel_lookup_table_;
  /**
   * \brief Minimum rate of spread before fire is considered to be spreading (m/min)
   */
  double minimum_ros_;
  /**
   * \brief Maximum distance that the fire is allowed to spread in one step (# of cells)
   */
  double maximum_spread_distance_;
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the day
   */
  double minimum_ffmc_;
  /**
   * \brief Minimum Fine Fuel Moisture Code required for spread during the night
   */
  double minimum_ffmc_at_night_;
  /**
   * \brief Offset from sunrise at which the day is considered to start (hours)
   */
  double offset_sunrise_;
  /**
   * \brief Offset from sunrise at which the day is considered to end (hours)
   */
  double offset_sunset_;
  /**
   * \brief Maximum grade target used for selecting WeatherSHIELD historic years
   */
  double max_grade_;
  /**
   * \brief Confidence required before simulation stops (% / 100)
   */
  double confidence_level_;
  /**
   * \brief Maximum time simulation can run before it is ended and whatever results it has are used (s)
   */
  __int64 maximum_time_seconds_;
  /**
   * \brief Weight to give to Scenario part of thresholds
   */
  double threshold_scenario_weight_;
  /**
   * \brief Weight to give to daily part of thresholds
   */
  double threshold_daily_weight_;
  /**
   * \brief Weight to give to hourly part of thresholds
   */
  double threshold_hourly_weight_;
  /**
   * \brief Days to output probability contours for (1 is start date, 2 is day after, etc.)
   */
  vector<int> output_date_offsets_;
  /**
   * \brief Default Percent Conifer to use for M1/M2 fuels where none is specified (%)
   */
  int default_percent_conifer_;
  /**
   * \brief Default Percent Dead Fir to use for M3/M4 fuels where none is specified (%)
   */
  int default_percent_dead_fir_;
  /**
   * \brief Maximum number of Iterations to run before checking if accuracy is good enough to stop
   */
  size_t simulation_recheck_interval_;
  /**
   * \brief Maximum number of Iterations to run at once if running async
   */
  size_t concurrent_simulation_rounds_;
  /**
   * \brief Minimum number of Iterations to run before precision required to stop is considered
   */
  size_t minimum_simulation_rounds_;
  /**
   * \brief Maximum number of points in a Cell before they are condensed
   */
  size_t max_cell_points_;
  /**
   * \brief Whatever the maximum value in the date offsets is
   */
  int max_date_offset_;
  /**
   * \brief The maximum fire intensity for the 'low' range of intensity (kW/m)
   */
  int intensity_max_low_;
  /**
   * \brief The maximum fire intensity for the 'moderate' range of intensity (kW/m)
   */
  int intensity_max_moderate_;
public:
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Whether or not to run things asynchronously where possible
   * \return Whether or not to run things asynchronously where possible
   */
  atomic<bool> run_async = true;
};
#pragma warning (pop)
/**
 * \brief The singleton instance for this class
 * \return The singleton instance for this class
 */
SettingsImplementation& SettingsImplementation::instance() noexcept
{
  static SettingsImplementation instance("settings.ini");
  return instance;
}
string get_value(unordered_map<string, string>& settings, const string& key)
{
  const auto found = settings.find(key);
  if (found != settings.end())
  {
    auto result = found->second;
    settings.erase(found);
    return result;
  }
  logging::fatal("Missing setting for %s", key.c_str());
  // HACK: use return to avoid compiler warning
  static const string Invalid = "INVALID";
  return Invalid;
}
#pragma warning (push)
#pragma warning (disable: 26447)
SettingsImplementation::SettingsImplementation(const char* filename) noexcept
{
  try
  {
    unordered_map<string, string> settings{};
    ifstream in;
    in.open(filename);
    if (in.is_open())
    {
      string str;
      logging::info("Reading settings from '%s'", filename);
      while (getline(in, str))
      {
        istringstream iss(str);
        if (getline(iss, str, '#'))
        {
          iss = istringstream(str);
        }
        if (getline(iss, str, '='))
        {
          const auto key = util::trim_copy(str);
          getline(iss, str, '\n');
          const auto value = util::trim_copy(str);
          settings.emplace(key, value);
        }
      }
      in.close();
    }
    weather_file_ = get_value(settings, "WEATHER_FILE");
    raster_root_ = get_value(settings, "RASTER_ROOT");
    fuel_lookup_table_ = get_value(settings, "FUEL_LOOKUP_TABLE");
    // HACK: run into fuel consumption being too low if we don't have a minimum ros
    static const auto MinRos = 0.05;
    // HACK: make sure this is always > 0 so that we don't have to check
    // specifically for 0 to avoid div error
    minimum_ros_ = max(stod(get_value(settings, "MINIMUM_ROS")), MinRos);
    maximum_spread_distance_ = stod(get_value(settings, "MAX_SPREAD_DISTANCE"));
    minimum_ffmc_ = stod(get_value(settings, "MINIMUM_FFMC"));
    minimum_ffmc_at_night_ = stod(get_value(settings, "MINIMUM_FFMC_AT_NIGHT"));
    offset_sunrise_ = stod(get_value(settings, "OFFSET_SUNRISE"));
    offset_sunset_ = stod(get_value(settings, "OFFSET_SUNSET"));
    max_grade_ = stod(get_value(settings, "MAX_GRADE"));
    confidence_level_ = stod(get_value(settings, "CONFIDENCE_LEVEL"));
    maximum_time_seconds_ = stol(get_value(settings, "MAXIMUM_TIME"));
    threshold_scenario_weight_ = stod(get_value(settings, "THRESHOLD_SCENARIO_WEIGHT"));
    threshold_daily_weight_ = stod(get_value(settings, "THRESHOLD_DAILY_WEIGHT"));
    threshold_hourly_weight_ = stod(get_value(settings, "THRESHOLD_HOURLY_WEIGHT"));
    output_date_offsets_ = parse_list<int>(get_value(settings, "OUTPUT_DATE_OFFSETS"),
                                           [](const string& s) { return stoi(s); });
    default_percent_conifer_ = stoi(get_value(settings, "DEFAULT_PERCENT_CONIFER"));
    default_percent_dead_fir_ = stoi(get_value(settings, "DEFAULT_PERCENT_DEAD_FIR"));
    intensity_max_low_ = stoi(get_value(settings, "INTENSITY_MAX_LOW"));
    intensity_max_moderate_ = stoi(get_value(settings, "INTENSITY_MAX_MODERATE"));
    simulation_recheck_interval_ = static_cast<size_t>(stoi(
      get_value(settings, "SIMULATION_RECHECK_INTERVAL")));
    concurrent_simulation_rounds_ = static_cast<size_t>(stoi(
      get_value(settings, "CONCURRENT_SIMULATION_ROUNDS")));
    minimum_simulation_rounds_ = static_cast<size_t>(stoi(
      get_value(settings, "MINIMUM_SIMULATION_ROUNDS")));
    max_cell_points_ = static_cast<size_t>(stoi(get_value(settings, "MAX_CELL_POINTS")));
    max_date_offset_ = *std::max_element(output_date_offsets_.begin(),
                                         output_date_offsets_.end());
    if (!settings.empty())
    {
      logging::warning("Unused settings in settings file %s", filename);
      for (const auto& kv : settings)
      {
        logging::warning("%s = %s", kv.first.c_str(), kv.second.c_str());
      }
    }
  }
  catch (...)
  {
    std::terminate();
  }
}
#pragma warning (pop)
const char* Settings::weatherFile() noexcept
{
  return SettingsImplementation::instance().weatherFile();
}
void Settings::setWeatherFile(const string f)
{
  SettingsImplementation::instance().setWeatherFile(f);
}
const char* Settings::rasterRoot() noexcept
{
  return SettingsImplementation::instance().rasterRoot();
}
const char* Settings::fuelLookupTable() noexcept
{
  return SettingsImplementation::instance().fuelLookupTable();
}
bool Settings::runAsync() noexcept
{
  return SettingsImplementation::instance().run_async;
}
void Settings::setRunAsync(const bool value) noexcept
{
  SettingsImplementation::instance().run_async = value;
}
double Settings::minimumRos() noexcept
{
  return SettingsImplementation::instance().minimumRos();
}
double Settings::maximumSpreadDistance() noexcept
{
  return SettingsImplementation::instance().maximumSpreadDistance();
}
double Settings::minimumFfmc() noexcept
{
  return SettingsImplementation::instance().minimumFfmc();
}
double Settings::minimumFfmcAtNight() noexcept
{
  return SettingsImplementation::instance().minimumFfmcAtNight();
}
double Settings::offsetSunrise() noexcept
{
  return SettingsImplementation::instance().offsetSunrise();
}
double Settings::offsetSunset() noexcept
{
  return SettingsImplementation::instance().offsetSunset();
}
int Settings::defaultPercentConifer() noexcept
{
  return SettingsImplementation::instance().defaultPercentConifer();
}
int Settings::defaultPercentDeadFir() noexcept
{
  return SettingsImplementation::instance().defaultPercentDeadFir();
}
size_t Settings::simulationRecheckInterval() noexcept
{
  return SettingsImplementation::instance().simulationRecheckInterval();
}
size_t Settings::concurrentSimulationRounds() noexcept
{
  return SettingsImplementation::instance().concurrentSimulationRounds();
}
size_t Settings::minimumSimulationRounds() noexcept
{
  return SettingsImplementation::instance().minimumSimulationRounds();
}
size_t Settings::maxCellPoints() noexcept
{
  return SettingsImplementation::instance().maxCellPoints();
}
int Settings::intensityMaxLow() noexcept
{
  return SettingsImplementation::instance().intensityMaxLow();
}
int Settings::intensityMaxModerate() noexcept
{
  return SettingsImplementation::instance().intensityMaxModerate();
}
void Settings::setMaxGrade(const double value) noexcept
{
  SettingsImplementation::instance().setMaxGrade(value);
}
double Settings::maxGrade() noexcept
{
  return SettingsImplementation::instance().maxGrade();
}
double Settings::confidenceLevel() noexcept
{
  return SettingsImplementation::instance().confidenceLevel();
}
__int64 Settings::maximumTimeSeconds() noexcept
{
  return SettingsImplementation::instance().maximumTimeSeconds();
}
double Settings::thresholdScenarioWeight() noexcept
{
  return SettingsImplementation::instance().thresholdScenarioWeight();
}
double Settings::thresholdDailyWeight() noexcept
{
  return SettingsImplementation::instance().thresholdDailyWeight();
}
double Settings::thresholdHourlyWeight() noexcept
{
  return SettingsImplementation::instance().thresholdHourlyWeight();
}
vector<int> Settings::outputDateOffsets()
{
  return SettingsImplementation::instance().outputDateOffsets();
}
int Settings::maxDateOffset() noexcept
{
  return SettingsImplementation::instance().maxDateOffset();
}
}
