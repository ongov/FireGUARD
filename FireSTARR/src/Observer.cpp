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
#include "Observer.h"
#include "Event.h"
#include "Scenario.h"
namespace firestarr
{
namespace sim
{
string IObserver::makeName(const string& base_name, const string& suffix)
{
  if (base_name.length() > 0)
  {
    return base_name + "_" + suffix;
  }
  return suffix;
}
ArrivalObserver::ArrivalObserver(const Scenario& scenario)
  : MapObserver<double>(scenario, 0.0, "arrival")
{
}
double ArrivalObserver::getValue(const Event& event) const noexcept
{
  return event.time();
}
SourceObserver::SourceObserver(const Scenario& scenario)
  : MapObserver<CellIndex>(scenario, -1, "source")
{
}
CellIndex SourceObserver::getValue(const Event& event) const noexcept
{
  return event.source();
}
IntensityObserver::IntensityObserver(const Scenario& scenario, string suffix) noexcept
  : scenario_(scenario), suffix_(std::move(suffix))
{
}
void IntensityObserver::handleEvent(const Event&) noexcept
{
  // HACK: do nothing because Scenario tracks intensity
}
void IntensityObserver::save(const string& dir, const string& base_name) const
{
  scenario_.saveIntensity(dir, makeName(base_name, suffix_));
}
void IntensityObserver::reset() noexcept
{
  // HACK: do nothing because Scenario tracks intensity
}
}
}
