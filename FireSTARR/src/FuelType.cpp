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
#include "FuelType.h"
#include "FireSpread.h"
#include "Log.h"
namespace firestarr
{
namespace fuel
{
double InvalidFuel::buiEffect(double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::crownConsumption(double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::calculateRos(const int, const wx::FwiWeather&, double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::calculateIsf(const SpreadInfo&, double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::surfaceFuelConsumption(const SpreadInfo&) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::lengthToBreadth(double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::finalRos(const SpreadInfo&, double, double, double) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::criticalSurfaceIntensity(const SpreadInfo&) const
{
  throw runtime_error("Invalid fuel type in fuel map");
}
double InvalidFuel::crownFractionBurned(double, double) const noexcept
{
  return logging::fatal<double>("Invalid fuel type in fuel map");
}
double InvalidFuel::probabilityPeat(double) const noexcept
{
  return logging::fatal<double>("Invalid fuel type in fuel map");
}
double InvalidFuel::survivalProbability(const wx::FwiWeather&) const noexcept
{
  return logging::fatal<double>("Invalid fuel type in fuel map");
}
}
}
