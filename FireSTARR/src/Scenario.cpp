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
#include "Scenario.h"
#include "Event.h"
#include "Grid.h"
#include "Observer.h"
#include "Settings.h"
#include "FireSpread.h"
#include "FuelLookup.h"
#include "FuelType.h"
#include "Log.h"
#include "MemoryPool.h"
#include "Perimeter.h"
#include "ProbabilityMap.h"
#include "SafeVector.h"
namespace firestarr::sim
{
constexpr auto CELL_CENTER = 0.5555555555555555;
constexpr auto PRECISION = 0.001;
static atomic<size_t> COUNT = 0;
static atomic<size_t> COMPLETED = 0;
static util::MemoryPool<BurnedData> POOL_BURNED_DATA{};
void Scenario::clear() noexcept
{
  scheduler_.clear();
  arrival_.clear();
  points_.clear();
  point_map_.clear();
  offsets_.clear();
  extinction_thresholds_.clear();
  spread_thresholds_by_ros_.clear();
}
size_t Scenario::completed() noexcept
{
  return COMPLETED;
}
size_t Scenario::count() noexcept
{
  return COUNT;
}
Scenario::~Scenario()
{
  clear();
}
static void make_threshold(vector<double>* thresholds,
                           mt19937* mt,
                           const Day start_day,
                           const Day last_date,
                           double (*convert)(double value))
{
  const auto total_weight = Settings::thresholdScenarioWeight() +
    Settings::thresholdDailyWeight() + Settings::thresholdHourlyWeight();
  const uniform_real_distribution<double> rand(0.0, 1.0);
  const auto general = rand(*mt);
  for (size_t i = start_day; i < MAX_DAYS; ++i)
  {
    const auto daily = rand(*mt);
    for (auto h = 0; h < DAY_HOURS; ++h)
    {
      // generate no matter what so if we extend the time period the results
      // for the first days don't change
      const auto hourly = rand(*mt);
      // only save if we're going to use it
      if (i <= last_date)
      {
        // subtract from 1.0 because we want weight to make things more likely not less
        // ensure we stay between 0 and 1
        thresholds->at((i - start_day) * DAY_HOURS + h) =
          convert(
            max(0.0,
                min(1.0,
                    1.0 -
                    (Settings::thresholdScenarioWeight() * general
                      + Settings::thresholdDailyWeight() * daily
                      + Settings::thresholdHourlyWeight() * hourly) / total_weight)));
      }
    }
  }
}
constexpr double same(const double value) noexcept { return value; }
static void make_threshold(vector<double>* thresholds,
                           mt19937* mt,
                           const Day start_day,
                           const Day last_date)
{
  make_threshold(thresholds, mt, start_day, last_date, &same);
}
Scenario::Scenario(Model* model,
                   const size_t id,
                   wx::FireWeather* weather,
                   const double start_time,
                   const shared_ptr<topo::Perimeter>& perimeter,
                   const topo::StartPoint& start_point,
                   const Day start_day,
                   const Day last_date)
  : Scenario(model, id, weather, start_time, start_point, start_day, last_date)
{
  perimeter_ = perimeter;
  start_cell_ = nullptr;
}
Scenario::Scenario(Model* model,
                   const size_t id,
                   wx::FireWeather* weather,
                   const double start_time,
                   const shared_ptr<topo::Cell>& start_cell,
                   const topo::StartPoint& start_point,
                   const Day start_day,
                   const Day last_date)
  : Scenario(model, id, weather, start_time, start_point, start_day, last_date)
{
  perimeter_ = nullptr;
  start_cell_ = start_cell;
}
Scenario* Scenario::reset(mt19937* mt_extinction,
                          mt19937* mt_spread,
                          util::SafeVector* final_sizes)
{
  ++simulation_;
  clear();
  const auto num = (static_cast<size_t>(last_date_) - start_day_ + 1) * DAY_HOURS;
  extinction_thresholds_.resize(num);
  spread_thresholds_by_ros_.resize(num);
  make_threshold(&extinction_thresholds_, mt_extinction, start_day_, last_date_);
  make_threshold(&spread_thresholds_by_ros_,
                 mt_spread,
                 start_day_,
                 last_date_,
                 &SpreadInfo::calculateRosFromThreshold);
  probabilities_ = nullptr;
  final_sizes_ = final_sizes;
  ran_ = false;
  current_time_ = start_time_;
  for (const auto& o : observers_)
  {
    o->reset();
  }
  return this;
}
void Scenario::evaluate(const Event& event)
{
  logging::check_fatal(event.time() < current_time_,
                       "Expected time to be > %f but got %f",
                       current_time_,
                       event.time());
  const auto& p = event.cell();
  switch (event.type())
  {
  case Event::FIRE_SPREAD:
    scheduleFireSpread(event);
    break;
  case Event::SAVE:
    saveObservers(event.time());
    saveStats(event.time());
    break;
  case Event::NEW_FIRE:
    // HACK: don't do this in constructor because scenario creates this in its constructor
    points_[p].emplace_back(easting(p), northing(p));
    if (fuel::is_null_fuel(event.cell()))
    {
      logging::fatal("Trying to start a fire in non-fuel");
    }
    logging::verbose("Starting fire in fuel type %s at time %f",
                     fuel::FuelType::safeName(fuel::check_fuel(event.cell())),
                     event.time());
    if (!survives(event.time(), event.cell(), event.timeAtLocation()))
    {
      const auto wx = weather(event.time());
      logging::info("Didn't survive ignition in %s with weather %f, %f",
                    fuel::FuelType::safeName(fuel::check_fuel(event.cell())),
                    wx->ffmc(),
                    wx->dmc());
      // HACK: we still want the fire to have existed, so set the intensity of the origin
    }
    // fires start with intensity of 1
    burn(event, 1);
    scheduleFireSpread(event);
    break;
  case Event::END_SIMULATION:
    logging::verbose("End simulation event reached at %f", event.time());
    endSimulation();
    break;
  default:
    throw runtime_error("Invalid event type");
  }
}
Scenario::Scenario(Model* model,
                   const size_t id,
                   wx::FireWeather* weather,
                   const double start_time,
                   topo::StartPoint start_point,
                   const Day start_day,
                   const Day last_date)
  : current_time_(start_time),
    unburnable_(nullptr),
    intensity_(nullptr),
    //surrounded_(nullptr),
    max_ros_(0),
    weather_(weather),
    model_(model),
    probabilities_(nullptr),
    final_sizes_(nullptr),
    start_point_(std::move(start_point)),
    id_(id),
    start_time_(start_time),
    simulation_(-1),
    start_day_(start_day),
    last_date_(last_date),
    ran_(false)
{
  ++COUNT;
  last_save_ = weather_->minDate();
}
void Scenario::saveStats(const double time) const
{
  probabilities_->at(time)->addProbability(*intensity_);
  if (time == last_save_)
  {
    final_sizes_->addValue(intensity_->fireSize());
  }
}
void Scenario::registerObserver(IObserver* observer)
{
  observers_.push_back(unique_ptr<IObserver>(observer));
}
void Scenario::notify(const Event& event) const
{
  for (const auto& o : observers_)
  {
    o->handleEvent(event);
  }
}
void Scenario::saveObservers(const string& base_name) const
{
  for (const auto& o : observers_)
  {
    o->save(outputDirectory(), base_name);
  }
}
void Scenario::saveObservers(const double time) const
{
  static const size_t BufferSize = 64;
  char buffer[BufferSize + 1] = {0};
  if (id() == ACTUALS)
  {
    sprintf_s(buffer,
              BufferSize,
              "actuals_%06lld_%03d",
              simulation(),
              static_cast<int>(time));
  }
  else
  {
    sprintf_s(buffer,
              BufferSize,
              "%03zu_%06lld_%03d",
              id(),
              simulation(),
              static_cast<int>(time));
  }
  saveObservers(string(buffer));
}
void Scenario::saveIntensity(const string& dir, const string& base_name) const
{
  intensity_->saveToAsciiFile(dir, base_name);
}
bool Scenario::ran() const noexcept
{
  return ran_;
}
Scenario::Scenario(Scenario&& rhs) noexcept
  : observers_(std::move(rhs.observers_)),
    save_points_(std::move(rhs.save_points_)),
    extinction_thresholds_(std::move(rhs.extinction_thresholds_)),
    spread_thresholds_by_ros_(std::move(rhs.spread_thresholds_by_ros_)),
    current_time_(rhs.current_time_),
    points_(std::move(rhs.points_)),
    unburnable_(rhs.unburnable_),
    scheduler_(std::move(rhs.scheduler_)),
    intensity_(std::move(rhs.intensity_)),
    perimeter_(std::move(rhs.perimeter_)),
    offsets_(std::move(rhs.offsets_)),
    arrival_(std::move(rhs.arrival_)),
    max_ros_(rhs.max_ros_),
    start_cell_(std::move(rhs.start_cell_)),
    weather_(rhs.weather_),
    model_(rhs.model_),
    probabilities_(rhs.probabilities_),
    final_sizes_(rhs.final_sizes_),
    start_point_(std::move(rhs.start_point_)),
    id_(rhs.id_),
    start_time_(rhs.start_time_),
    last_save_(rhs.last_save_),
    simulation_(rhs.simulation_),
    start_day_(rhs.start_day_),
    last_date_(rhs.last_date_),
    ran_(rhs.ran_)
{
  rhs.unburnable_ = nullptr;
}
Scenario& Scenario::operator=(Scenario&& rhs) noexcept
{
  if (this != &rhs)
  {
    observers_ = std::move(rhs.observers_);
    save_points_ = std::move(rhs.save_points_);
    extinction_thresholds_ = std::move(rhs.extinction_thresholds_);
    spread_thresholds_by_ros_ = std::move(rhs.spread_thresholds_by_ros_);
    points_ = std::move(rhs.points_);
    current_time_ = rhs.current_time_;
    scheduler_ = std::move(rhs.scheduler_);
    intensity_ = std::move(rhs.intensity_);
    perimeter_ = std::move(rhs.perimeter_);
    //surrounded_ = rhs.surrounded_;
    start_cell_ = std::move(rhs.start_cell_);
    weather_ = rhs.weather_;
    model_ = rhs.model_;
    probabilities_ = rhs.probabilities_;
    final_sizes_ = rhs.final_sizes_;
    start_point_ = std::move(rhs.start_point_);
    id_ = rhs.id_;
    start_time_ = rhs.start_time_;
    last_save_ = rhs.last_save_;
    simulation_ = rhs.simulation_;
    start_day_ = rhs.start_day_;
    last_date_ = rhs.last_date_;
    ran_ = rhs.ran_;
  }
  return *this;
}
void Scenario::burn(const Event& event, const IntensitySize burn_intensity)
{
#ifdef _DEBUG
			logging::check_fatal(intensity_->hasBurned(event.cell()), "Re-burning cell");
#endif
  // Observers only care about cells burning so do it here
  notify(event);
  intensity_->burn(event.cell(), burn_intensity);
  arrival_[event.cell()] = event.time();
  //scheduleFireSpread(event);
}
bool Scenario::isSurrounded(const Location& location) const
{
  return intensity_->isSurrounded(location);
}
double Scenario::easting(const topo::Cell& p) const noexcept
{
  return (p.column() + CELL_CENTER);
}
double Scenario::northing(const topo::Cell& p) const noexcept
{
  return (p.row() + CELL_CENTER);
}
topo::Cell Scenario::cell(const InnerPos& p) const noexcept
{
  const auto r = static_cast<Idx>(p.y);
  const auto c = static_cast<Idx>(p.x);
  return cell(r, c);
}
Scenario* Scenario::run(map<double, ProbabilityMap*>* probabilities)
{
  CriticalSection _(Model::task_limiter);
  probabilities_ = probabilities;
  unburnable_ = POOL_BURNED_DATA.acquire();
  logging::check_fatal(ran(), "Scenario has already run");
  logging::debug("Running scenario %d.%04d", id_, simulation_);
  // don't do this until we run so we don't allocate memory too soon
  intensity_ = make_unique<IntensityMap>(model());
  //surrounded_ = POOL_BURNED_DATA.acquire();
  for (auto time : save_points_)
  {
    // NOTE: these happen in this order because of the way they sort based on type
    addEvent(Event::makeSave(static_cast<double>(time)));
  }
  if (nullptr == perimeter_)
  {
    addEvent(Event::makeNewFire(start_time_, cell(*start_cell_)));
  }
  else
  {
    intensity_->applyPerimeter(*perimeter_);
    const auto& env = model().environment();
    for (const auto& location : perimeter_->edge())
    {
      const auto cell = env.cell(location.hash());
      logging::check_fatal(fuel::is_null_fuel(cell), "Null fuel in perimeter");
      points_[cell].emplace_back(easting(cell), northing(cell));
    }
    addEvent(Event::makeFireSpread(start_time_));
  }
  // HACK: make a copy of the event so it still exists after it gets processed
  // NOTE: sorted so that EventSaveASCII is always just before this
  // Only run until last time we asked for a save for
  logging::verbose("Creating simulation end event for %f", last_save_);
  addEvent(Event::makeEnd(last_save_));
  // mark all original points as burned at start
  for (auto& kv : points_)
  {
    const auto& location = kv.first;
    // would be burned already if perimeter applied
    if (canBurn(location))
    {
      const auto fake_event = Event::makeFireSpread(
        start_time_,
        static_cast<IntensitySize>(1),
        location);
      burn(fake_event, static_cast<IntensitySize>(1));
    }
  }
  while (!scheduler_.empty())
  {
    evaluateNextEvent();
  }
  ++COMPLETED;
  // HACK: use + to pull value out of atomic
  logging::info("Completed scenario %d.%04d  [%d of %d] with final size %0.1f ha (%zu)",
                id_,
                simulation_,
                +COMPLETED,
                +COUNT,
                currentFireSize(),
                weightedDsr());
  ran_ = true;
  unburnable_ = check_reset(unburnable_, POOL_BURNED_DATA);
  return this;
}
[[nodiscard]] ostream& operator<<(ostream& os, const PointSet& a)
{
  for (auto pt : a)
  {
    cout << "(" << pt.x << ", " << pt.y << "), ";
  }
  return os;
}
inline void Scenario::checkCondense(vector<InnerPos>& a)
{
  if (a.size() > Settings::maxCellPoints())
  {
    size_t n_pos = 0;
    auto n = numeric_limits<double>::min();
    size_t ne_pos = 0;
    auto ne = numeric_limits<double>::min();
    size_t e_pos = 0;
    auto e = numeric_limits<double>::min();
    size_t se_pos = 0;
    auto se = numeric_limits<double>::min();
    size_t s_pos = 0;
    auto s = numeric_limits<double>::max();
    size_t sw_pos = 0;
    auto sw = numeric_limits<double>::min();
    size_t w_pos = 0;
    auto w = numeric_limits<double>::max();
    size_t nw_pos = 0;
    auto nw = numeric_limits<double>::min();
    // should always be in the same cell so do this once
    const auto cell_x = static_cast<Idx>(a[0].x);
    const auto cell_y = static_cast<Idx>(a[0].y);
    for (size_t i = 0; i < a.size(); ++i)
    {
      const auto& p = a[i];
      const auto x = p.x - cell_x;
      const auto y = p.y - cell_y;
      if (y > n)
      {
        n_pos = i;
        n = y;
      }
      else if (y < s)
      {
        s_pos = i;
        s = y;
      }
      const auto cur_ne = x + y;
      const auto cur_sw = (1 - x) + (1 - y);
      if (cur_ne > ne)
      {
        ne_pos = i;
        ne = cur_ne;
      }
      else if (cur_sw > sw)
      {
        sw_pos = i;
        sw = cur_sw;
      }
      if (x > e)
      {
        e_pos = i;
        e = x;
      }
      else if (x < w)
      {
        w_pos = i;
        w = x;
      }
      const auto cur_se = x + (1 - y);
      const auto cur_nw = (1 - x) + y;
      if (cur_se > se)
      {
        se_pos = i;
        se = cur_se;
      }
      else if (cur_nw > nw)
      {
        nw_pos = i;
        nw = cur_nw;
      }
    }
    //// NOTE: use member variable since making a set on every call really slows this down
    //// use a set so duplicates don't get added
    //condensed.insert(a[n_pos]);
    //condensed.insert(a[ne_pos]);
    //condensed.insert(a[e_pos]);
    //condensed.insert(a[se_pos]);
    //condensed.insert(a[s_pos]);
    //condensed.insert(a[sw_pos]);
    //condensed.insert(a[w_pos]);
    //condensed.insert(a[nw_pos]);
    //a.clear();
    //a.insert(a.begin(), condensed.begin(), condensed.end());
    //condensed.clear();
    // keeping points is easier and near as fast as checking for duplicates
    // but we don't need a member variable to do it
    a = {
      a[n_pos],
      a[ne_pos],
      a[e_pos],
      a[se_pos],
      a[s_pos],
      a[sw_pos],
      a[w_pos],
      a[nw_pos]
    };
  }
}
void Scenario::scheduleFireSpread(const Event& event)
{
  const auto time = event.time();
  //note("time is %f", time);
  current_time_ = time;
  const auto wx = weather(time);
  //  logging::note("%d points", points_->size());
  const auto this_time = util::time_index(time);
  const auto next_time = static_cast<double>(this_time + 1) / DAY_HOURS;
  // should be in minutes?
  const auto max_duration = (next_time - time) * DAY_MINUTES;
  //note("time is %f, next_time is %f, max_duration is %f",
  //     time,
  //     next_time,
  //     max_duration);
  const auto max_time = time + max_duration / DAY_MINUTES;
  if (wx->ffmc().asDouble() < minimumFfmcForSpread(time))
  {
    addEvent(Event::makeFireSpread(max_time));
    logging::verbose("Waiting until %f because of FFMC", max_time);
    return;
  }
  if (current_time_index_ != this_time)
  {
    current_time_index_ = this_time;
    offsets_.clear();
    max_intensity_.clear();
    max_ros_ = 0.0;
  }
  auto any_spread = false;
  for (const auto& kv : points_)
  {
    const auto& location = kv.first;
    // any cell that has the same fuel, slope, and aspect has the same spread
    const auto key = location.key();
    const auto seek_spreading = offsets_.find(key);
    if (seek_spreading == offsets_.end())
    {
      // have not calculated spread for this cell yet
      const SpreadInfo origin(*this, time, location, nd(time), wx);
      // will be empty if invalid
      offsets_.emplace(key, origin.offsets());
      if (!origin.isNotSpreading())
      {
        any_spread = true;
        max_ros_ = max(max_ros_, origin.headRos());
        max_intensity_[key] = max(max_intensity_[key], origin.maxIntensity());
      }
    }
    else
    {
      // already did the lookup so use the result
      any_spread |= !seek_spreading->second.empty();
    }
  }
  if (!any_spread || max_ros_ < Settings::minimumRos())
  {
    logging::verbose("Waiting until %f", max_time);
    addEvent(Event::makeFireSpread(max_time));
    return;
  }
  //note("Max spread is %f, max_ros is %f",
  //     Settings::maximumSpreadDistance() * cellSize(),
  //     max_ros_);
  const auto duration = ((max_ros_ > 0)
                           ? min(max_duration,
                                 Settings::maximumSpreadDistance() * cellSize() /
                                 max_ros_)
                           : max_duration);
  //note("Spreading for %f minutes", duration);
  const auto new_time = time + duration / DAY_MINUTES;
  for (auto& kv : points_)
  {
    const auto& location = kv.first;
    const auto key = location.key();
    auto& offsets = offsets_.at(key);
    if (!offsets.empty())
    {
      for (auto& o : offsets)
      {
        // offsets in meters
        const auto offset_x = o.x * duration;
        const auto offset_y = o.y * duration;
        //note("%f, %f", offset_x, offset_y);
        for (auto& p : kv.second)
        {
          const InnerPos pos(p.x + offset_x, p.y + offset_y);
          const auto for_cell = cell(pos);
          if (!(fuel::is_null_fuel(for_cell) || (*unburnable_)[for_cell.hash()]))
          {
            point_map_[for_cell].emplace_back(pos);
          }
        }
      }
    }
    else
    {
      // can't just keep existing points by swapping because something may have spread into this cell
      auto& pts = point_map_[location];
      pts.insert(pts.end(), kv.second.begin(), kv.second.end());
    }
    kv.second.clear();
  }
  vector<topo::Cell> erase_what{};
  for (auto& kv : point_map_)
  {
    if (!kv.second.empty())
    {
      auto& for_cell = kv.first;
      if (canBurn(for_cell) && max_intensity_[for_cell.key()] > 0)
      {
        // HACK: make sure it can't round down to 0
        const auto intensity = static_cast<IntensitySize>(max(
          1.0,
          max_intensity_[for_cell.key()]));
        const auto fake_event = Event::makeFireSpread(
          new_time,
          intensity,
          for_cell);
        burn(fake_event, intensity);
      }
      // check if this cell is surrounded by burned cells or non-fuels
      // if surrounded then just drop all the points inside this cell
      if (!(*unburnable_)[for_cell.hash()])
      {
        if (!isSurrounded(for_cell) &&
          survives(new_time, for_cell, new_time - arrival_[for_cell]))
        {
          checkCondense(kv.second);
          //checkHull(for_cell, kv.second);
          std::swap(points_[for_cell], kv.second);
        }
        else
        {
          // whether it went out or is surrounded just mark it as unburnable
          (*unburnable_)[for_cell.hash()] = true;
          erase_what.emplace_back(for_cell);
        }
      }
      kv.second.clear();
    }
  }
  for (auto& c : erase_what)
  {
    point_map_.erase(c);
    points_.erase(c);
  }
  logging::verbose("Spreading %d points until %f", points_.size(), new_time);
  addEvent(Event::makeFireSpread(new_time));
}
double Scenario::currentFireSize() const
{
  return intensity_->fireSize();
}
bool Scenario::canBurn(const topo::Cell& location) const
{
  return intensity_->canBurn(location);
}
bool Scenario::canBurn(const HashSize hash) const
{
  return intensity_->canBurn(hash);
}
bool Scenario::hasBurned(const Location& location) const
{
  return intensity_->hasBurned(location);
}
bool Scenario::hasBurned(const HashSize hash) const
{
  return intensity_->hasBurned(hash);
}
void Scenario::endSimulation() noexcept
{
  logging::verbose("Ending simulation");
  clear();
}
void Scenario::addSaveByOffset(const int offset)
{
  // +1 since yesterday is in here too
  addSave(weather_->minDate() + offset + 1);
}
vector<double> Scenario::savePoints() const
{
  return save_points_;
}
template <class V>
void Scenario::addSave(V time)
{
  last_save_ = max(last_save_, static_cast<double>(time));
  save_points_.push_back(time);
}
void Scenario::addEvent(Event&& event)
{
  scheduler_.insert(std::move(event));
}
void Scenario::evaluateNextEvent()
{
  // make sure to actually copy it before we erase it
  const auto& event = *scheduler_.begin();
  evaluate(event);
  scheduler_.erase(event);
}
}
