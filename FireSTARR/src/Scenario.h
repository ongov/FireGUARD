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
#include <list>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <vector>
#include "EventCompare.h"
#include "FireWeather.h"
#include "IntensityMap.h"
#include "Model.h"
#include "Settings.h"
#include "StartPoint.h"
namespace firestarr
{
namespace sim
{
struct InnerPos;
class IObserver;
class Event;
using PointSet = vector<InnerPos>;
/**
 * \brief A single Scenario in an Iteration using a specific FireWeather stream.
 */
class Scenario
{
public:
  /**
   * \brief Number of Scenarios that have completed running
   * \return Number of Scenarios that have completed running
   */
  [[nodiscard]] static size_t completed() noexcept;
  /**
   * \brief Number of Scenarios that have been initialized
   * \return Number of Scenarios that have been initialized
   */
  [[nodiscard]] static size_t count() noexcept;
  /**
   * \brief Weighted Danger Severity Rating
   * \return Weighted Danger Severity Rating
   */
  [[nodiscard]] constexpr size_t weightedDsr() const noexcept
  {
    return weather_->weightedDsr();
  }
  virtual ~Scenario();
  /**
   * \brief Constructor
   * \param model Model running this Scenario
   * \param id Identifier
   * \param weather Weather stream to use
   * \param start_time Start time for simulation
   * \param perimeter Perimeter to initialize with
   * \param start_point StartPoint to use sunrise/sunset times from
   * \param start_day First day of simulation
   * \param last_date Last day of simulation
   */
  Scenario(Model* model,
           size_t id,
           wx::FireWeather* weather,
           double start_time,
           const shared_ptr<topo::Perimeter>& perimeter,
           const topo::StartPoint& start_point,
           Day start_day,
           Day last_date);
  /**
   * \brief Constructor
   * \param model Model running this Scenario
   * \param id Identifier
   * \param weather Weather stream to use
   * \param start_time Start time for simulation
   * \param start_cell Cell to start ignition in
   * \param start_point StartPoint to use sunrise/sunset times from
   * \param start_day First day of simulation
   * \param last_date Last day of simulation
   */
  Scenario(Model* model,
           size_t id,
           wx::FireWeather* weather,
           double start_time,
           const shared_ptr<topo::Cell>& start_cell,
           const topo::StartPoint& start_point,
           Day start_day,
           Day last_date);
  /**
   * \brief Move constructor
   * \param rhs Scenario to move from
   */
  Scenario(Scenario&& rhs) noexcept;
  Scenario(const Scenario& rhs) = delete;
  /**
   * \brief Move assignment
   * \param rhs Scenario to move from
   * \return This, after assignment
   */
  Scenario& operator=(Scenario&& rhs) noexcept;
  Scenario& operator=(const Scenario& rhs) const = delete;
  /**
   * \brief Reset thresholds and set SafeVector to output results to
   * \param mt_extinction Used for extinction random numbers
   * \param mt_spread Used for spread random numbers
   * \param final_sizes SafeVector to output results to
   * \return This
   */
  [[nodiscard]] Scenario* reset(mt19937* mt_extinction,
                                mt19937* mt_spread,
                                util::SafeVector* final_sizes);
  /**
   * \brief Burn cell that Event takes place in
   * \param event Event with cell location
   * \param burn_intensity Intensity to burn cell with
   */
  void burn(const Event& event, IntensitySize burn_intensity);
  /**
   * \brief Directory to output files to
   * \return Directory to output files to
   */
  [[nodiscard]] constexpr const string& outputDirectory() const
  {
    return model_->outputDirectory();
  }
  /**
   * \brief Get Cell for given row and column
   * \param row Row
   * \param column Column
   * \return Cell for given row and column
   */
  [[nodiscard]] constexpr topo::Cell cell(const Idx row, const Idx column) const
  {
    return model_->cell(row, column);
  }
  /**
   * \brief Get Cell for given Location
   * \param location Location
   * \return Cell for given Location
   */
  [[nodiscard]] constexpr topo::Cell cell(const Location& location) const
  {
    return model_->cell(location);
  }
  /**
   * \brief Get Cell for Location with given hash
   * \param hash_size Hash
   * \return Cell for Location with given hash
   */
  [[nodiscard]] constexpr topo::Cell cell(const HashSize hash_size) const
  {
    return model_->cell(hash_size);
  }
  /**
   * \brief Number of rows
   * \return Number of rows
   */
  [[nodiscard]] constexpr Idx rows() const { return model_->rows(); }
  /**
   * \brief Number of columns
   * \return Number of columns
   */
  [[nodiscard]] constexpr Idx columns() const { return model_->columns(); }
  /**
   * \brief Cell width and height (m)
   * \return Cell width and height (m)
   */
  [[nodiscard]] constexpr double cellSize() const { return model_->cellSize(); }
  /**
   * \brief Simulation number
   * \return Simulation number
   */
  [[nodiscard]] constexpr __int64 simulation() const { return simulation_; }
  /**
   * \brief StartPoint that provides sunrise/sunset times
   * \return StartPoint
   */
  [[nodiscard]] constexpr const topo::StartPoint& startPoint() const
  {
    return start_point_;
  }
  /**
   * \brief Simulation start time
   * \return Simulation start time
   */
  [[nodiscard]] constexpr double startTime() const { return start_time_; }
  /**
   * \brief Identifier
   * \return Identifier
   */
  [[nodiscard]] constexpr size_t id() const { return id_; }
  /**
   * \brief Model this Scenario is running in
   * \return Model this Scenario is running in
   */
  [[nodiscard]] constexpr const Model& model() const { return *model_; }
  /**
   * \brief Sunrise time for given day
   * \param for_day Day to get sunrise time for
   * \return Sunrise time for given day
   */
  [[nodiscard]] constexpr double dayStart(const size_t for_day) const
  {
    return start_point_.dayStart(for_day);
  }
  /**
   * \brief Sunset time for given day
   * \param for_day Day to get sunset time for
   * \return Sunset time for given day
   */
  [[nodiscard]] constexpr double dayEnd(const size_t for_day) const
  {
    return start_point_.dayEnd(for_day);
  }
  /**
   * \brief FwiWeather for given time
   * \param time Time to get weather for (decimal days)
   * \return FwiWeather for given time
   */
  [[nodiscard]] const wx::FwiWeather* weather(const double time) const
  {
    return weather_->at(time);
  }
  /**
   * \brief Difference between date and the date of minimum foliar moisture content
   * \param time Time to get value for
   * \return Difference between date and the date of minimum foliar moisture content
   */
  [[nodiscard]] constexpr int nd(const double time) const { return model().nd(time); }
  /**
   * \brief Get extinction threshold for given time
   * \param time Time to get value for
   * \return Extinction threshold for given time
   */
  [[nodiscard]] double extinctionThreshold(const double time) const
  {
    return extinction_thresholds_.at(util::time_index(time - start_day_));
  }
  /**
   * \brief Get spread threshold for given time
   * \param time Time to get value for
   * \return Spread threshold for given time
   */
  [[nodiscard]] double spreadThresholdByRos(const double time) const
  {
    return spread_thresholds_by_ros_.at(util::time_index(time - start_day_));
  }
  /**
   * \brief Whether or not time is after sunrise and before sunset
   * \param time Time to determine for
   * \return Whether or not time is after sunrise and before sunset
   */
  [[nodiscard]] constexpr bool isAtNight(const double time) const
  {
    const auto day = static_cast<Day>(time);
    const auto hour_part = 24 * (time - day);
    return hour_part < dayStart(day) || hour_part > dayEnd(day);
  }
  /**
   * \brief Minimum Fine Fuel Moisture Code for spread to be possible
   * \param time Time to determine for
   * \return Minimum Fine Fuel Moisture Code for spread to be possible
   */
  [[nodiscard]] double minimumFfmcForSpread(const double time) const noexcept
  {
    return isAtNight(time) ? Settings::minimumFfmcAtNight() : Settings::minimumFfmc();
  }
  /**
   * \brief Whether or not the given Location is surrounded by cells that are burnt
   * \param location Location to check if is surrounded
   * \return Whether or not the given Location is surrounded by cells that are burnt
   */
  [[nodiscard]] bool isSurrounded(const Location& location) const;
  /**
   * \brief Easting
   * \param p Cell
   * \return Easting
   */
  [[nodiscard]] double easting(const topo::Cell& p) const noexcept;
  /**
   * \brief Northing
   * \param p Cell
   * \return Northing
   */
  [[nodiscard]] double northing(const topo::Cell& p) const noexcept;
  /**
   * \brief Cell that InnerPos falls within
   * \param p InnerPos
   * \return Cell that InnerPos falls within
   */
  [[nodiscard]] topo::Cell cell(const InnerPos& p) const noexcept;
  /**
   * \brief Run the Scenario
   * \param probabilities map to update ProbabilityMap for times base on Scenario results
   * \return This
   */
  Scenario* run(map<double, ProbabilityMap*>* probabilities);
  /**
   * \brief Schedule a fire spread Event
   * \param event Event to schedule
   */
  void scheduleFireSpread(const Event& event);
  /**
   * \brief Current fire size (ha)
   * \return Current fire size (ha)
   */
  [[nodiscard]] double currentFireSize() const;
  /**
   * \brief Whether or not a Cell can burn
   * \param location Cell
   * \return Whether or not a Cell can burn
   */
  [[nodiscard]] bool canBurn(const topo::Cell& location) const;
  /**
   * \brief Whether or not Cell with the given hash can burn
   * \param hash Hash for Cell to check
   * \return Whether or not Cell with the given hash can burn
   */
  [[nodiscard]] bool canBurn(HashSize hash) const;
  /**
   * \brief Whether or not Location has burned already
   * \param location Location to check
   * \return Whether or not Location has burned already
   */
  [[nodiscard]] bool hasBurned(const Location& location) const;
  /**
   * \brief Whether or not Location with given hash has burned already
   * \param hash Hash of Location to check
   * \return Whether or not Location with given hash has burned already
   */
  [[nodiscard]] bool hasBurned(HashSize hash) const;
  /**
   * \brief Add an Event to the queue
   * \param event Event to add
   */
  void addEvent(Event&& event);
  /**
   * \brief Evaluate next Event in the queue
   */
  void evaluateNextEvent();
  /**
   * \brief End the simulation
   */
  void endSimulation() noexcept;
  /**
   * \brief Add a save point for simulation data at the given offset
   * \param offset Offset from start of simulation (days)
   */
  void addSaveByOffset(int offset);
  /**
   * \brief Add a save point for simulation data at given time
   * \tparam V Type to use for time
   * \param time Time to add save point at
   */
  template <class V>
  void addSave(V time);
  /**
   * \brief Tell Observers to save their data with base file name
   * \param base_name Base file name
   */
  void saveObservers(const string& base_name) const;
  /**
   * \brief Tell Observers to save their data for the given time
   * \param time Time to save data for
   */
  void saveObservers(double time) const;
  /**
   * \brief Save burn intensity information
   * \param dir Directory to save to
   * \param base_name Base file name
   */
  void saveIntensity(const string& dir, const string& base_name) const;
  /**
   * \brief Whether or not this Scenario has run already
   * \return Whether or not this Scenario has run already
   */
  [[nodiscard]] bool ran() const noexcept;
  /**
   * \brief Whether or not the fire survives the conditions
   * \param time Time to use weather from
   * \param cell Cell to use
   * \param time_at_location How long the fire has been in that Cell
   * \return Whether or not the fire survives the conditions
   */
  [[nodiscard]] bool survives(const double time,
                              const topo::Cell& cell,
                              const double time_at_location) const
  {
    const auto wx = weather_->at(time);
    // use mike's table
    const auto mc = wx->mcDmcPct();
    if (100 > mc
      || 109 >= mc && 5 > time_at_location
      || 119 >= mc && 4 > time_at_location
      || 131 >= mc && 3 > time_at_location
      || 145 >= mc && 2 > time_at_location
      || 218 >= mc && 1 > time_at_location)
    {
      return true;
    }
    // we can look by fuel type because the entire landscape shares the weather
    return extinctionThreshold(time) < weather_->survivalProbability(
      time,
      cell.fuelCode());
  }
  /**
   * \brief List of what times the simulation will save
   * \return List of what times the simulation will save
   */
  [[nodiscard]] vector<double> savePoints() const;
  /**
   * \brief Save state of Scenario at given time
   * \param time 
   */
  void saveStats(double time) const;
  /**
   * \brief Register an IObserver that will be notified when Cells burn
   * \param observer Observer to add to notification list
   */
  void registerObserver(IObserver* observer);
  /**
   * \brief Notify IObservers that a Cell has burned
   * \param event Event to notify IObservers of
   */
  void notify(const Event& event) const;
  /**
   * \brief Take whatever steps are necessary to process the given Event
   * \param event Event to process
   */
  void evaluate(const Event& event);
  /**
   * \brief Clear the Event list and all other data
   */
  void clear() noexcept;
protected:
  /**
   * \brief Constructor
   * \param model Model running this Scenario
   * \param id Identifier
   * \param weather Weather stream to use
   * \param start_time Start time for simulation
   * \param start_point StartPoint to use sunrise/sunset times from
   * \param start_day First day of simulation
   * \param last_date Last day of simulation
   */
  Scenario(Model* model,
           size_t id,
           wx::FireWeather* weather,
           double start_time,
           topo::StartPoint start_point,
           Day start_day,
           Day last_date);
  /**
   * \brief Map of Cells to the PointSets in them
   */
  unordered_map<topo::Cell, PointSet> point_map_{};
  /**
   * \brief Condense set of points down to a smaller number
   * \param a Set of points to condense
   */
  inline void checkCondense(vector<InnerPos>& a);
  /**
   * \brief Observers to be notified when cells burn
   */
  list<unique_ptr<IObserver>> observers_{};
  /**
   * \brief List of times to save simulation
   */
  vector<double> save_points_;
  /**
   * \brief Thresholds used to determine if extinction occurs
   */
  vector<double> extinction_thresholds_{};
  /**
   * \brief Thresholds used to determine if spread occurs
   */
  vector<double> spread_thresholds_by_ros_{};
  /**
   * \brief Current time for this Scenario
   */
  double current_time_;
  /**
   * \brief Map of Cells to the PointSets within them
   */
  unordered_map<topo::Cell, PointSet> points_{};
  /**
   * \brief Contains information on cells that are not burnable
   */
  BurnedData* unburnable_;
  /**
   * \brief Event scheduler used for ordering events
   */
  set<Event, EventCompare> scheduler_;
  /**
   * \brief Map of what intensity each cell has burned at
   */
  unique_ptr<IntensityMap> intensity_;
  /**
   * \brief Perimeter used to start Scenario from
   */
  shared_ptr<topo::Perimeter> perimeter_;
  /**
   * \brief Calculated offsets from origin Point for spread given SpreadKey for current time
   */
  unordered_map<topo::SpreadKey, PointSet> offsets_{};
  /**
   * \brief Calculated maximum intensity for spread given SpreadKey for current time
   */
  unordered_map<topo::SpreadKey, double> max_intensity_{};
  /**
   * \brief Map of when Cell had first Point arrive in it
   */
  unordered_map<topo::Cell, double> arrival_{};
  /**
   * \brief Maximum rate of spread for current time
   */
  double max_ros_;
  /**
   * \brief Cell that the Scenario starts from if no Perimeter
   */
  shared_ptr<topo::Cell> start_cell_;
  /**
   * \brief Weather to use for this Scenario
   */
  wx::FireWeather* weather_;
  /**
   * \brief Model this Scenario is being run in
   */
  Model* model_;
  /**
   * \brief Map of ProbabilityMaps by time snapshot for them was taken
   */
  map<double, ProbabilityMap*>* probabilities_;
  /**
   * \brief Where to append the final size of this Scenario when run is complete
   */
  util::SafeVector* final_sizes_;
  /**
   * \brief Origin of fire
   */
  topo::StartPoint start_point_;
  /**
   * \brief Identifier
   */
  size_t id_;
  /**
   * \brief Start time (decimal days)
   */
  double start_time_;
  /**
   * \brief Which save point is the last one
   */
  double last_save_;
  /**
   * \brief Time index for current time
   */
  size_t current_time_index_ = numeric_limits<size_t>::max();
  /**
   * \brief Simulation number
   */
  __int64 simulation_;
  /**
   * \brief First day of simulation
   */
  Day start_day_;
  /**
   * \brief Last day of simulation
   */
  Day last_date_;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Whether or not this Scenario has completed running
   */
  bool ran_;
};
#pragma warning (pop)
}
}
