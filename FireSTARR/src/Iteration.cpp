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
#include "Iteration.h"
#include "ProbabilityMap.h"
#include "Scenario.h"
namespace firestarr
{
namespace sim
{
Iteration::~Iteration()
{
  for (auto& s : scenarios_)
  {
    delete s;
  }
}
Iteration::Iteration(vector<Scenario*> scenarios) noexcept
  : scenarios_(std::move(scenarios))
{
}
Iteration* Iteration::reset(mt19937* mt_extinction, mt19937* mt_spread)
{
  final_sizes_ = {};
  for (auto& scenario : scenarios_)
  {
    static_cast<void>(scenario->reset(mt_extinction, mt_spread, &final_sizes_));
  }
  return this;
}
//
//Iteration* Iteration::run(map<double, ProbabilityMap*>* probabilities)
//{
//  // sort in run so that they still get the same extinction thresholds as when unsorted
//		std::sort(scenarios_.begin(),
//			scenarios_.end(),
//			[](Scenario* lhs, Scenario* rhs) noexcept
//		{
//			// sort so that scenarios with highest dsrs are at the front
//		  //return lhs->weightedDsr() > rhs->weightedDsr();
//		});
//	if (Settings::runAsync())
//  {
//    vector<future<Scenario*>> results{};
//    // make a local copy so that we don't have mutex competition with other Iterations
//    map<double, ProbabilityMap*> local_probabilities{};
//    for (auto& kv : *probabilities)
//    {
//      local_probabilities[kv.first] = kv.second->copyEmpty();
//    }
//    for (auto& scenario : scenarios_)
//    {
//      results.push_back(async(launch::async,
//                              &Scenario::run,
//                              scenario,
//                              &local_probabilities));
//    }
//    for (auto& scenario : results)
//    {
//      auto s = scenario.get();
//      s->clear();
//    }
//    for (auto& kv : *probabilities)
//    {
//      kv.second->addProbabilities(*local_probabilities[kv.first]);
//      delete local_probabilities[kv.first];
//    }
//  }
//  else
//  {
//    for (auto& scenario : scenarios_)
//    {
//      scenario->run(probabilities);
//    }
//  }
//  return this;
//}
vector<double> Iteration::savePoints() const
{
  return scenarios_.at(0)->savePoints();
}
double Iteration::startTime() const
{
  return scenarios_.at(0)->startTime();
}
size_t Iteration::size() const noexcept
{
  return scenarios_.size();
}
util::SafeVector Iteration::finalSizes() const
{
  return final_sizes_;
}
}
}
