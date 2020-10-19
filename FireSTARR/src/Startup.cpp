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
#include "Startup.h"
#include "Database.h"
#include "Time.h"
namespace firestarr
{
namespace wx
{
Startup::Startup(wstring station,
                 const TIMESTAMP_STRUCT& generated,
                 const topo::Point& point,
                 const double distance_from,
                 const Ffmc& ffmc,
                 const Dmc& dmc,
                 const Dc& dc,
                 const AccumulatedPrecipitation& apcp_0800,
                 const bool overridden) noexcept
  : station_(std::move(station)),
    generated_(generated),
    point_(point),
    distance_from_(distance_from),
    ffmc_(ffmc),
    dmc_(dmc),
    dc_(dc),
    apcp_0800_(apcp_0800),
    is_overridden_(overridden)
{
}
Startup read_startup(util::Database* db)
{
  // HACK: do it this way so that we know database calls are in this order
  const auto station = db->getString();
  const auto gen_utc = db->getTimestamp();
  tm utc{};
  util::to_tm_gm(gen_utc, &utc);
  const auto local_t = mktime(&utc);
  tm local{};
  localtime_s(&local, &local_t);
  TIMESTAMP_STRUCT result;
  util::to_ts(local, &result);
  const auto generated = result;
  const auto latitude = db->getDouble();
  const auto longitude = db->getDouble();
  const auto distance_from = db->getDouble<0>();
  const Ffmc ffmc(db->getDouble<2>());
  const Dmc dmc(db->getDouble<2>());
  const Dc dc(db->getDouble<2>());
  const AccumulatedPrecipitation apcp_0800(db->getDouble<2>());
  return Startup(station,
                 generated,
                 topo::Point(latitude, longitude),
                 distance_from,
                 ffmc,
                 dmc,
                 dc,
                 apcp_0800,
                 false);
}
#pragma warning(suppress: 26495)
Startup::Startup(util::Database* db)
  : Startup(read_startup(db))
{
}
}
}
