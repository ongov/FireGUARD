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
#include "Model.h"
#include "Scenario.h"
#include "Settings.h"
#include "FireWeather.h"
#include "FBP45.h"
#include "FireSpread.h"
#include "FuelLookup.h"
#include "Observer.h"
#include "Perimeter.h"
#include "ProbabilityMap.h"
#include "SafeVector.h"
#include "Statistics.h"
#include "UTM.h"
namespace firestarr
{
namespace sim
{
Semaphore Model::task_limiter{static_cast<int>(std::thread::hardware_concurrency())};
BurnedData* Model::getBurnedVector() const noexcept
{
#pragma warning (push)
#pragma warning (disable: 26447)
  try
  {
    if (!vectors_.empty())
    {
      lock_guard<mutex> lock(vector_mutex_);
      // check again once we have the mutex
      if (!vectors_.empty())
      {
        const auto v = std::move(vectors_.back()).release();
        vectors_.pop_back();
        // this is already reset before it was given back
        return v;
      }
    }
    return environment().makeBurnedData().release();
  }
  catch (...)
  {
    std::terminate();
  }
#pragma warning (pop)
}
void Model::releaseBurnedVector(BurnedData* has_burned) const noexcept
{
#pragma warning (push)
#pragma warning (disable: 26447)
  try
  {
    environment().resetBurnedData(has_burned);
    lock_guard<mutex> lock(vector_mutex_);
    vectors_.push_back(unique_ptr<BurnedData>(has_burned));
  }
  catch (...)
  {
    std::terminate();
  }
#pragma warning (pop)
}
Model::~Model()
{
}
Model::Model(const topo::StartPoint& start_point,
             const char* const output_directory,
             topo::Environment* env)
  : start_time_(Clock::now()),
    time_limit_(std::chrono::seconds(Settings::maximumTimeSeconds())),
    env_(env),
    output_directory_(output_directory)
{
  util::make_directory_recursive(output_directory_.c_str());
  const auto nd_for_point =
    calculate_nd_for_point(env->elevation(), start_point);
  for (auto day = 0; day < MAX_DAYS; ++day)
  {
    nd_.at(static_cast<size_t>(day)) = static_cast<int>(day - nd_for_point);
    logging::verbose("Day %d has nd %d, is%s green, %d%% curing",
                     day,
                     nd_.at(static_cast<size_t>(day)),
                     fuel::calculate_is_green(nd_.at(static_cast<size_t>(day)))
                       ? ""
                       : " not",
                     fuel::calculate_grass_curing(nd_.at(static_cast<size_t>(day))));
  }
}
void Model::readWeather(const fuel::FuelLookup& fuel_lookup,
                        const string& filename,
                        const bool for_actuals,
                        const wx::FwiWeather& yesterday)
{
  map<size_t, map<Day, wx::FwiWeather>> wx{};
  auto min_date = numeric_limits<Day>::max();
  ifstream in;
  in.open(filename);
  if (in.is_open())
  {
    string str;
    logging::info("Reading scenarios from '%s'", filename.c_str());
    // read header line
    getline(in, str);
    // get rid of spaces
    str.erase(std::remove(str.begin(), str.end(), ' '), str.end());
    constexpr auto expected_header =
      "Scenario,Date,APCP,TMP,RH,WS,WD,FFMC,DMC,DC,ISI,BUI,FWI";
    logging::check_fatal(str != expected_header,
                         "Input CSV must have columns in this order:\n%s",
                         expected_header);
    while (getline(in, str))
    {
      istringstream iss(str);
      if (getline(iss, str, ',') && !str.empty())
      {
        // HACK: ignore date and just worry about relative order??
        // Scenario
        logging::verbose("Scenario is %s", str.c_str());
        auto cur = ACTUALS;
        if (!(str == "actual"))
        {
          try
          {
            cur = static_cast<size_t>(-stoi(str));
          }
          catch (std::exception&)
          {
            // HACK: somehow stoi() is still getting empty strings
            logging::fatal("Error reading weather file %s", filename.c_str());
          }
        }
        if (for_actuals && cur != ACTUALS)
        {
          // HACK: rely on actuals always being first
          break;
        }
        if (wx.find(cur) == wx.end())
        {
          logging::debug("Loading scenario %d...", cur);
          wx.emplace(cur, map<Day, wx::FwiWeather>());
        }
        auto& s = wx.at(cur);
        struct tm t{};
        util::read_date(&iss, &str, &t);
        const auto ticks = mktime(&t);
        if (1 == cur)
        {
          logging::debug("Date '%s' is %ld and calculated jd is %d",
                         str.c_str(),
                         ticks,
                         t.tm_yday);
          if (!s.empty() && t.tm_yday < min_date)
          {
            logging::fatal(
              "Weather input file crosses year boundary or dates are not sequential");
          }
        }
        min_date = min(min_date, static_cast<Day>(t.tm_yday));
        logging::check_fatal(s.find(static_cast<Day>(t.tm_yday)) != s.end(),
                             "Day already exists");
        s.emplace(static_cast<Day>(t.tm_yday), wx::FwiWeather(&iss, &str));
      }
    }
    in.close();
  }
  if (!for_actuals)
  {
    // HACK: it's added for everything right now, but alone if just doing actuals
    const auto seek = wx.find(ACTUALS);
    if (seek != wx.end())
    {
      wx.erase(ACTUALS);
    }
  }
  // HACK: add yesterday into everything
  for (auto& kv : wx)
  {
    auto& s = kv.second;
    logging::check_fatal(s.find(static_cast<Day>(min_date - 1)) != s.end(),
                         "Day already exists");
    s.emplace(static_cast<Day>(min_date - 1), yesterday);
  }
  // loop through and try to find duplicates
  for (const auto& kv : wx)
  {
    const auto k = kv.first;
    const auto s = kv.second;
    if (wx_.find(k) == wx_.end())
    {
      const auto w = make_shared<wx::FireWeather>(fuel_lookup.usedFuels(), s);
      wx_.emplace(k, w);
    }
  }
}
void Model::findStarts(const Location location)
{
  logging::error("Trying to start a fire in non-fuel");
  Idx range = 1;
  while (starts_.empty())
  {
    for (Idx x = -range; x <= range; ++x)
    {
      for (Idx y = -range; y <= range; ++y)
      {
        // make sure we only look at the outside of the box
        if (1 == range || abs(x) == range || abs(y) == range)
        {
          const auto loc = env_->cell(location.hash() + y + (x * MAX_COLUMNS));
          if (!fuel::is_null_fuel(loc))
          {
            starts_.push_back(make_shared<topo::Cell>(cell(loc)));
          }
        }
      }
    }
    ++range;
  }
  logging::info("Using %d start locations:", starts_.size());
  for (const auto& s : starts_)
  {
    logging::info("\t%d, %d", s->row(), s->column());
  }
}
void Model::makeStarts(Coordinates coordinates,
                       const topo::Point& point,
                       const wx::FwiWeather& yesterday,
                       const string& perim,
                       const size_t size)
{
  const Location location(std::get<0>(coordinates), std::get<1>(coordinates));
  if (!perim.empty())
  {
    logging::note("Initializing from perimeter %s", perim.c_str());
    perimeter_ = make_shared<topo::Perimeter>(perim, point, *env_);
  }
  else if (size > 0)
  {
    logging::note("Initializing from size %d ha", size);
    perimeter_ = make_shared<topo::Perimeter>(
      cell(location),
      size,
      yesterday,
      *env_);
  }
  // figure out where the fire can exist
  if (nullptr != perimeter_ && !perimeter_->burned().empty())
  {
    logging::check_fatal(size != 0 && !perim.empty(), "Can't specify size and perimeter");
    // we have a perimeter to start from
    // HACK: make sure this isn't empty
    starts_.push_back(make_shared<topo::Cell>(cell(location)));
    logging::note("Fire starting with size %0.1f ha",
                  perimeter_->burned().size() * env_->cellSize() / 100.0);
  }
  else
  {
    if (nullptr != perimeter_)
    {
      logging::check_fatal(!perimeter_->burned().empty(),
                           "Not using perimeter so it should be empty");
      logging::note("Using fire perimeter results in empty fire - changing to use point");
      perimeter_ = nullptr;
    }
    logging::note("Fire starting with size %0.1f ha", env_->cellSize() / 100.0);
    if (0 == size && fuel::is_null_fuel(cell(location.hash())))
    {
      findStarts(location);
    }
    else
    {
      starts_.push_back(make_shared<topo::Cell>(cell(location)));
    }
  }
  logging::note("Creating %ld streams x %ld location%s = %ld scenarios",
                wx_.size(),
                starts_.size(),
                starts_.size() > 1 ? "s" : "",
                wx_.size() * starts_.size());
}
Iteration Model::readScenarios(const topo::StartPoint& start_point,
                               const double start,
                               const bool save_intensity,
                               const Day start_day,
                               const Day last_date)
{
  vector<Scenario*> result{};
#pragma warning (push)
#pragma warning (disable: 4820)
  auto saves = Settings::outputDateOffsets();
  const auto setup_scenario = [&result, save_intensity, &saves](Scenario* scenario)
  {
    if (save_intensity)
    {
      scenario->registerObserver(new IntensityObserver(*scenario, ""));
      scenario->registerObserver(new ArrivalObserver(*scenario));
      scenario->registerObserver(new SourceObserver(*scenario));
    }
    // FIX: this should be relative to the start date, not the weather start date
    for (const auto& i : saves)
    {
      scenario->addSaveByOffset(i);
    }
    result.push_back(scenario);
  };
#pragma warning (pop)
  for (const auto& kv : wx_)
  {
    const auto id = kv.first;
    const auto cur_wx = kv.second;
    if (nullptr != perimeter_)
    {
      setup_scenario(new Scenario(this,
                                  id,
                                  cur_wx.get(),
                                  start,
                                  perimeter_,
                                  start_point,
                                  start_day,
                                  last_date));
    }
    else
    {
      for (const auto& cur_start : starts_)
      {
        // should always have at least the day before the fire in the weather stream
        setup_scenario(new Scenario(this,
                                    id,
                                    cur_wx.get(),
                                    start,
                                    cur_start,
                                    start_point,
                                    start_day,
                                    last_date));
      }
    }
  }
  return Iteration(result);
}
bool Model::isOutOfTime() const noexcept
{
  return (Clock::now() - startTime()) > timeLimit();
}
ProbabilityMap* Model::makeProbabilityMap(const char* for_what,
                                          const double time,
                                          const double start_time,
                                          const int min_value,
                                          const int low_max,
                                          const int med_max,
                                          const int max_value) const
{
  return env_->makeProbabilityMap(for_what,
                                  time,
                                  start_time,
                                  min_value,
                                  low_max,
                                  med_max,
                                  max_value);
}
static void show_probabilities(const map<double, ProbabilityMap*>& probabilities)
{
  // do this here so actuals scenario isn't part of probability
  for (const auto& kv : probabilities)
  {
    kv.second->show();
  }
}
template <class T>
ostream& operator<<(ostream& os, const vector<T>& v)
{
  for (auto& m : v)
  {
    os << m << " ";
  }
  os << endl;
  return os;
}
map<double, ProbabilityMap*> make_prob_map(const Model& model,
                                           const vector<double>& saves,
                                           const bool for_actuals,
                                           const double started,
                                           const int min_value,
                                           const int low_max,
                                           const int med_max,
                                           const int max_value)
{
  map<double, ProbabilityMap*> result{};
  for (const auto& time : saves)
  {
    result.emplace(
      time,
      model.makeProbabilityMap(for_actuals ? "Actuals" : "Fire",
                               time,
                               started,
                               min_value,
                               low_max,
                               med_max,
                               max_value));
  }
  return result;
}
map<double, util::SafeVector*> make_size_map(const vector<double>& saves)
{
  map<double, util::SafeVector*> result{};
  for (const auto& time : saves)
  {
    result.emplace(time, new util::SafeVector());
  }
  return result;
}
bool add_statistics(const size_t i,
                    vector<double>* means,
                    vector<double>* pct,
                    const Model& model,
                    const util::SafeVector& v)
{
  const auto sizes = v.getValues();
  logging::check_fatal(sizes.empty(), "No sizes at end of simulation");
  const util::Statistics s{sizes};
  static_cast<void>(util::insert_sorted(pct, s.percentile(95)));
  static_cast<void>(util::insert_sorted(means, s.mean()));
  if (model.isOutOfTime())
  {
    logging::note(
      "Stopping after %d iterations. Time limit of %d seconds has been reached.",
      i,
      Settings::maximumTimeSeconds());
    return false;
  }
  return true;
}
size_t runs_required(const size_t i,
                     const vector<double>* means,
                     const vector<double>* pct,
                     const Model& model)
{
  if (model.isOutOfTime())
  {
    logging::note(
      "Stopping after %d iterations. Time limit of %d seconds has been reached.",
      i,
      Settings::maximumTimeSeconds());
    return 0;
  }
  const auto for_means = util::Statistics{*means};
  const auto for_pct = util::Statistics{*pct};
  if (!(i < Settings::minimumSimulationRounds()
    || !for_means.isConfident(Settings::confidenceLevel())
    || !for_pct.isConfident(Settings::confidenceLevel())))
  {
    return 0;
  }
  const auto left = max(for_means.runsRequired(i, Settings::confidenceLevel()),
                        for_pct.runsRequired(i, Settings::confidenceLevel()));
  return left;
}
map<double, ProbabilityMap*> Model::runIterations(const topo::StartPoint& start_point,
                                                  const double start,
                                                  const Day start_day,
                                                  const bool save_intensity,
                                                  const bool for_actuals)
{
  auto last_date = start_day;
  for (const auto i : Settings::outputDateOffsets())
  {
    last_date = max(static_cast<Day>(start_day + i), last_date);
  }
  const auto seed = static_cast<unsigned int>(abs(
    start * start_point.latitude() / start_point.longitude()));
  // use independent seeds so that if we remove one threshold it doesn't affect the other
  mt19937 mt_spread(seed);
  mt19937 mt_extinction(seed * 3);
  vector<double> means{};
  vector<double> pct{};
  size_t i = 0;
  auto iterations = readScenarios(start_point,
                                  start,
                                  save_intensity,
                                  start_day,
                                  last_date);
  // put probability maps into map
  const auto saves = iterations.savePoints();
  const auto started = iterations.startTime();
  auto probabilities = make_prob_map(*this,
                                     saves,
                                     for_actuals,
                                     started,
                                     0,
                                     Settings::intensityMaxLow(),
                                     Settings::intensityMaxModerate(),
                                     numeric_limits<int>::max());
  auto runs_left = Settings::minimumSimulationRounds();
  const auto recheck_interval = Settings::simulationRecheckInterval();
  if (Settings::runAsync())
  {
    vector<Iteration> all_iterations{};
    all_iterations.push_back(std::move(iterations));
    size_t runs = 0;
    const auto max_concurrent = Settings::concurrentSimulationRounds();
    while (runs_left > 0)
    {
      // run what's left, up to min rounds at a time
      const auto cur_runs = runs_left;
      const auto total_runs = i + cur_runs;
      while (min(cur_runs, max_concurrent) > all_iterations.size())
      {
        all_iterations.push_back(readScenarios(start_point,
                                               start,
                                               save_intensity,
                                               start_day,
                                               last_date));
      }
      auto threads = vector<std::thread>{};
      auto all_scenarios = vector<Scenario*>{};
      // need at least this many results
      threads.reserve(max_concurrent);
      for (size_t k = 0; k < min(cur_runs, all_iterations.size()); ++k)
      {
        logging::debug("Running iteration [%d of %d]", runs + 1, total_runs);
        all_iterations.at(k).reset(&mt_extinction, &mt_spread);
        auto& s = all_iterations.at(k).getScenarios();
        all_scenarios.insert(all_scenarios.end(), s.begin(), s.end());
        ++runs;
      }
      // sort in run so that they still get the same extinction thresholds as when unsorted
      std::sort(all_scenarios.begin(),
                all_scenarios.end(),
                [](Scenario* lhs, Scenario* rhs) noexcept
                {
                  // sort so that scenarios with highest dsrs are at the front
                  return lhs->weightedDsr() > rhs->weightedDsr();
                });
      for (auto s : all_scenarios)
      {
        threads.emplace_back(&Scenario::run,
                             s,
                             &probabilities);
      }
      for (auto& t : threads)
      {
        t.join();
      }
      for (size_t k = 0; k < min(cur_runs, all_iterations.size()); ++k)
      {
        auto& iteration = all_iterations.at(k);
        auto final_sizes = iteration.finalSizes();
        ++i;
        //note("Adding %d", i);
        if (!add_statistics(i, &means, &pct, *this, final_sizes))
        {
          // ran out of time
          return probabilities;
        }
      }
      runs_left = runs_required(i, &means, &pct, *this);
      logging::note("Need another %d iterations", runs_left);
      if (runs_left > recheck_interval)
      {
        runs_left = recheck_interval;
        logging::note("Capping at %d iterations before checking again", runs_left);
      }
    }
    // everything should be done when this section ends
  }
  else
  {
    logging::note("Running in synchronous mode");
    while (runs_left > 0)
    {
      const auto cur_runs = runs_left;
      size_t k = 0;
      while (k < cur_runs)
      {
        logging::note("Running iteration %d", i + 1);
        iterations.reset(&mt_extinction, &mt_spread);
        for (auto s : iterations.getScenarios())
        {
          s->run(&probabilities);
        }
        ++i;
        if (!add_statistics(i, &means, &pct, *this, iterations.finalSizes()))
        {
          // ran out of time
          return probabilities;
        }
        ++k;
      }
      runs_left = runs_required(i, &means, &pct, *this);
      logging::note("Need another %d iterations", runs_left);
      if (runs_left > recheck_interval)
      {
        runs_left = recheck_interval;
        logging::note("Capping at %d iterations before checking again", runs_left);
      }
    }
  }
  return probabilities;
}
int Model::runScenarios(const char* const output_directory,
                        const char* const weather_input,
                        const char* const fuels_table,
                        const char* const raster_root,
                        const wx::FwiWeather& yesterday,
                        const topo::StartPoint& start_point,
                        const tm& start_time,
                        const bool save_intensity,
                        const bool for_actuals,
                        const string& perimeter,
                        const size_t size)
{
  const fuel::FuelLookup lookup(fuels_table);
  auto env = topo::Environment::loadEnvironment(lookup,
                                                raster_root,
                                                start_point,
                                                perimeter,
                                                start_time.tm_year);
  const auto position = env.findCoordinates(start_point, true);
  logging::check_fatal(
    std::get<0>(*position) > MAX_COLUMNS || std::get<1>(*position) > MAX_COLUMNS,
    "Location loaded outside of grid at position (%d, %d)",
    std::get<0>(*position),
    std::get<1>(*position));
  logging::info("Position is (%d, %d)", std::get<0>(*position), std::get<1>(*position));
  const Location location{std::get<0>(*position), std::get<1>(*position)};
  Model model(start_point, output_directory, &env);
  auto x = 0.0;
  auto y = 0.0;
  const auto zone = lat_lon_to_utm(start_point, &x, &y);
  logging::note("UTM coordinates are: %d %d %d",
                zone,
                static_cast<int>(x),
                static_cast<int>(y));
  logging::note("Grid has size (%d, %d)", env.rows(), env.columns());
  logging::note("Fire start position is cell (%d, %d)",
                location.row(),
                location.column());
  model.readWeather(lookup, weather_input, for_actuals, yesterday);
  model.makeStarts(*position, start_point, yesterday, perimeter, size);
  auto start_hour = ((start_time.tm_hour + (static_cast<double>(start_time.tm_min) / 60))
    / DAY_HOURS);
  // HACK: round to 2 digits so we can keep test output the same
  start_hour = static_cast<double>(static_cast<int>(start_hour * 100)) / 100;
  const auto start = start_time.tm_yday + start_hour;
  const auto start_day = static_cast<Day>(start);
  auto probabilities =
    model.runIterations(start_point, start, start_day, save_intensity, for_actuals);
  logging::note("Ran %d simulations", Scenario::completed());
  show_probabilities(probabilities);
  auto final_time = numeric_limits<double>::min();
  for (const auto by_time : probabilities)
  {
    const auto time = by_time.first;
    final_time = max(final_time, time);
    const auto prob = by_time.second;
    prob->saveAll(model, start_time, for_actuals, time, start_day);
  }
  for (const auto& kv : probabilities)
  {
    delete kv.second;
  }
  return 0;
}
}
}
