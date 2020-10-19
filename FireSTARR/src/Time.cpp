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
#include "Time.h"
namespace firestarr::util
{
/**
 * \brief Convert from TIMESTAMP_STRUCT to tm
 * \param s Input value
 * \param t Output value
 */
void to_tm_no_fix(const TIMESTAMP_STRUCT& s, tm* t) noexcept
{
  t->tm_year = s.year - 1900;
  t->tm_mon = s.month - 1;
  t->tm_mday = s.day;
  t->tm_hour = s.hour;
  t->tm_min = s.minute;
  t->tm_sec = s.second;
}
void to_tm(const TIMESTAMP_STRUCT& s, tm* t) noexcept
{
  // this doesn't set yday or other things properly, so convert to time and back
  to_tm_no_fix(s, t);
  const auto t_t = mktime(t);
  localtime_s(t, &t_t);
}
void to_tm_gm(const TIMESTAMP_STRUCT& s, tm* t) noexcept
{
  // this doesn't set yday or other things properly, so convert to time and back
  to_tm_no_fix(s, t);
  const auto t_t = _mkgmtime(t);
  // HACK: use gmtime_s instead of localtime_s so it doesn't mess with hours based on DST
  gmtime_s(t, &t_t);
}
void to_ts(const tm& t, TIMESTAMP_STRUCT* s) noexcept
{
  s->year = static_cast<SQLSMALLINT>(t.tm_year + 1900);
  s->month = static_cast<SQLUSMALLINT>(t.tm_mon + 1);
  s->day = static_cast<SQLUSMALLINT>(t.tm_mday);
  s->hour = static_cast<SQLUSMALLINT>(t.tm_hour);
  s->minute = static_cast<SQLUSMALLINT>(t.tm_min);
  s->second = static_cast<SQLUSMALLINT>(t.tm_sec);
  s->fraction = 0;
}
}
