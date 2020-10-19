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
#include "Weather.h"
#include "Database.h"
#include "Log.h"
#include "Time.h"
namespace firestarr
{
namespace wx
{
const Temperature Temperature::Zero = Temperature(0);
const RelativeHumidity RelativeHumidity::Zero = RelativeHumidity(0);
const Direction Direction::Zero = Direction(0, false);
const Speed Speed::Zero = Speed(0);
const Wind Wind::Zero = Wind(Direction(0, false), Speed(0));
const AccumulatedPrecipitation AccumulatedPrecipitation::Zero =
  AccumulatedPrecipitation(0);
static bool WARNED_ABOUT_BAD_TIME_ZONE = false;
TIMESTAMP_STRUCT read_timestamp(util::Database* db) noexcept
{
  // HACK: do it this way so that we know database calls are in this order
  const auto db_utc = db->getTimestamp();
  tm utc{};
  util::to_tm_gm(db_utc, &utc);
  const auto utc_t = _mkgmtime(&utc);
  tm local{};
  localtime_s(&local, &utc_t);
  TIMESTAMP_STRUCT result;
  util::to_ts(local, &result);
  if (result.hour != 13)
  {
    // HACK: not sure what to do with time zones yet, so just set it as 13:00
    if (!WARNED_ABOUT_BAD_TIME_ZONE)
    {
      logging::warning(
        "Overriding hour to be 13:00 even though it's being converted to %02d:00",
        result.hour);
      WARNED_ABOUT_BAD_TIME_ZONE = true;
    }
    result.hour = 13;
  }
  return result;
}
Weather read_weather(util::Database* db) noexcept
{
  // HACK: read and throw out the date
  /* const auto for_time = */
  read_timestamp(db);
  const Temperature tmp(db->getDouble<2>());
  const RelativeHumidity rh(db->getDouble<2>());
  const Speed ws(db->getDouble<2>());
  const Direction wd(db->getDouble<2>(), false);
  const Wind wind(wd, ws);
  const AccumulatedPrecipitation apcp(db->getDouble<2>());
  return Weather(tmp, rh, wind, apcp);
}
#pragma warning(suppress: 26495)
Weather::Weather(util::Database* db) noexcept
  : Weather(read_weather(db))
{
}
}
}
