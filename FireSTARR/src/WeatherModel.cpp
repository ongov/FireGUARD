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
#include "WeatherModel.h"
#include "Time.h"
namespace firestarr
{
using util::operator<;
using util::operator==;
namespace wx
{
WeatherModel::WeatherModel(const TIMESTAMP_STRUCT& generated,
                           wstring&& name,
                           const topo::Point& point,
                           const double distance_from) noexcept
  : generated_(generated),
    name_(std::forward<wstring>(name)),
    point_(point),
    distance_from_(distance_from)
{
}
WeatherModel read_weather_model(util::Database* db) noexcept
{
  // HACK: do it this way so that we know database calls are in this order
  const auto generated = db->getTimestamp();
  auto name = db->getString();
  const auto latitude = db->getDouble();
  const auto longitude = db->getDouble();
  const auto distance_from = db->getDouble<0>();
  return WeatherModel(generated,
                      std::move(name),
                      topo::Point(latitude, longitude),
                      distance_from);
}
#pragma warning(suppress: 26495)
WeatherModel::WeatherModel(util::Database* db) noexcept
  : WeatherModel(read_weather_model(db))
{
}
WeatherModel& WeatherModel::operator=(const WeatherModel& rhs)
{
  if (this != &rhs)
  {
    generated_ = rhs.generated_;
    name_ = rhs.name_;
    point_ = rhs.point_;
    distance_from_ = rhs.distance_from_;
  }
  return *this;
}
bool ModelCompare::operator()(const WeatherModel& x, const WeatherModel& y) const noexcept
{
  const auto cs = x.name().compare(y.name());
  if (0 == cs)
  {
    if (x.generated() == y.generated())
    {
      // HACK: these should always be equal, so just check that they are
      assert(x.point().latitude() == y.point().latitude()
        && x.point().longitude() == y.point().longitude()
        && x.distanceFrom() == y.distanceFrom());
      if (x.point().latitude() == y.point().latitude())
      {
        if (x.point().longitude() == y.point().longitude())
        {
          return x.distanceFrom() < y.distanceFrom();
        }
        return x.point().longitude() < y.point().longitude();
      }
      return x.point().latitude() < y.point().latitude();
    }
    return x.generated() < y.generated();
  }
  return -1 == cs;
}
}
}
