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
#include "ProbabilityMap.h"
#include "FBP45.h"
#include "IntensityMap.h"
#include "Model.h"
#include "Statistics.h"
#include "Time.h"
#include "Util.h"
namespace firestarr
{
namespace sim
{
ProbabilityMap::ProbabilityMap(const char* const for_what,
                               const double time,
                               const double start_time,
                               const int min_value,
                               const int low_max,
                               const int med_max,
                               const int max_value,
                               const data::GridBase& grid_info)
  : all_(data::GridMap<size_t>(grid_info, 0)),
    high_(data::GridMap<size_t>(grid_info, 0)),
    med_(data::GridMap<size_t>(grid_info, 0)),
    low_(data::GridMap<size_t>(grid_info, 0)),
    for_what_(for_what),
    time_(time),
    start_time_(start_time),
    min_value_(min_value),
    max_value_(max_value),
    low_max_(low_max),
    med_max_(med_max)
{
}
ProbabilityMap* ProbabilityMap::copyEmpty() const
{
  return new ProbabilityMap(for_what_,
                            time_,
                            start_time_,
                            min_value_,
                            low_max_,
                            med_max_,
                            max_value_,
                            all_);
}
void ProbabilityMap::addProbabilities(const ProbabilityMap& rhs)
{
  logging::check_fatal(rhs.time_ != time_, "Wrong time");
  logging::check_fatal(rhs.start_time_ != start_time_, "Wrong start time");
  logging::check_fatal(rhs.min_value_ != min_value_, "Wrong min value");
  logging::check_fatal(rhs.max_value_ != max_value_, "Wrong max value");
  logging::check_fatal(rhs.low_max_ != low_max_, "Wrong low max value");
  logging::check_fatal(rhs.med_max_ != med_max_, "Wrong med max value");
  lock_guard<mutex> lock(mutex_);
  for (auto&& kv : rhs.low_.data)
  {
    low_.data[kv.first] += kv.second;
  }
  for (auto&& kv : rhs.med_.data)
  {
    med_.data[kv.first] += kv.second;
  }
  for (auto&& kv : rhs.high_.data)
  {
    high_.data[kv.first] += kv.second;
  }
  for (auto&& kv : rhs.all_.data)
  {
    all_.data[kv.first] += kv.second;
  }
  for (auto size : rhs.sizes_)
  {
    static_cast<void>(util::insert_sorted(&sizes_, size));
  }
}
void ProbabilityMap::addProbability(const IntensityMap& for_time)
{
  lock_guard<mutex> lock(mutex_);
  std::for_each(
    for_time.cbegin(),
    for_time.cend(),
    [this](auto&& kv)
    {
      all_.data[kv.first] += 1;
      if (kv.second > min_value_ && kv.second <= low_max_)
      {
        low_.data[kv.first] += 1;
      }
      else if (kv.second > low_max_ && kv.second <= med_max_)
      {
        med_.data[kv.first] += 1;
      }
      else if (kv.second > med_max_ && kv.second <= max_value_)
      {
        high_.data[kv.first] += 1;
      }
      else
      {
        logging::fatal("Value %d doesn't fit into any range", kv.second);
      }
    });
  const auto size = for_time.fireSize();
  static_cast<void>(util::insert_sorted(&sizes_, size));
}
vector<double> ProbabilityMap::getSizes() const
{
  return sizes_;
}
util::Statistics ProbabilityMap::getStatistics() const
{
  return util::Statistics{getSizes()};
}
size_t ProbabilityMap::numSizes() const noexcept
{
  return sizes_.size();
}
void ProbabilityMap::show() const
{
  // even if we only ran the actuals we'll still have multiple scenarios
  // with different randomThreshold values
  const auto day = static_cast<int>(time_ - floor(start_time_));
  const auto s = getStatistics();
  logging::note(
    "%s size at end of day %d: %0.1f ha - %0.1f ha (mean %0.1f ha, median %0.1f ha)",
    for_what_,
    day,
    s.min(),
    s.max(),
    s.mean(),
    s.median());
}
void ProbabilityMap::saveSizes(const string& dir, const string& base_name) const
{
  ofstream out;
  out.open(dir + base_name + ".csv");
  auto sizes = getSizes();
  if (!sizes.empty())
  {
    // don't want to modify original array so we can still lookup in correct order
    sort(sizes.begin(), sizes.end());
  }
  for (const auto& s : sizes)
  {
    out << s << "\n";
  }
  out.close();
}
void ProbabilityMap::saveAll(const Model& model,
                             const tm& start_time,
                             const bool for_actuals,
                             const double time,
                             const double start_day) const
{
  auto t = start_time;
  auto ticks = mktime(&t);
  const auto day = static_cast<int>(round(time));
  ticks += (static_cast<size_t>(day) - t.tm_yday - 1) * DAY_SECONDS;
  localtime_s(&t, &ticks);
  // t.tm_yday = day + 1;
  TIMESTAMP_STRUCT for_time{};
  util::to_ts(t, &for_time);
  const auto make_string = [&for_time, &day](const char* name)
  {
    constexpr auto mask = "%s_%03d_%04d-%02d-%02d";
    static constexpr size_t OutLength = 100;
    char tmp[OutLength];
    sprintf_s(tmp,
              OutLength,
              mask,
              name,
              day,
              for_time.year,
              for_time.month,
              for_time.day);
    return string(tmp);
  };
  vector<std::future<void>> results{};
  results.push_back(async(launch::async,
                          &ProbabilityMap::saveTotal,
                          this,
                          model.outputDirectory(),
                          make_string(for_actuals ? "actuals" : "wxshield")));
  results.push_back(async(launch::async,
                          &ProbabilityMap::saveLow,
                          this,
                          model.outputDirectory(),
                          make_string("intensity_L")));
  results.push_back(async(launch::async,
                          &ProbabilityMap::saveModerate,
                          this,
                          model.outputDirectory(),
                          make_string("intensity_M")));
  results.push_back(async(launch::async,
                          &ProbabilityMap::saveHigh,
                          this,
                          model.outputDirectory(),
                          make_string("intensity_H")));
  results.push_back(async(launch::async,
                          &ProbabilityMap::saveSizes,
                          this,
                          model.outputDirectory(),
                          make_string("sizes")));
  for (auto& result : results)
  {
    result.wait();
  }
  const auto nd = model.nd(day);
  logging::note("Fuels for day %d are %s green-up and grass has %d%% curing",
                day - static_cast<int>(start_day),
                fuel::calculate_is_green(nd) ? "after" : "before",
                fuel::calculate_grass_curing(nd));
}
void ProbabilityMap::saveTotal(const string& dir, const string& base_name) const
{
  all_.saveToProbabilityFile(dir, base_name, static_cast<double>(numSizes()));
}
void ProbabilityMap::saveHigh(const string& dir, const string& base_name) const
{
  high_.saveToProbabilityFile(dir, base_name, static_cast<double>(numSizes()));
}
void ProbabilityMap::saveModerate(const string& dir, const string& base_name) const
{
  med_.saveToProbabilityFile(dir, base_name, static_cast<double>(numSizes()));
}
void ProbabilityMap::saveLow(const string& dir, const string& base_name) const
{
  low_.saveToProbabilityFile(dir, base_name, static_cast<double>(numSizes()));
}
}
}
