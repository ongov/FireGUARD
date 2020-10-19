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

#pragma once
namespace firestarr
{
namespace util
{
/**
 * \brief Equality operator
 * \param x First TIMESTAMP_STRUCT
 * \param y Second TIMESTAMP_STRUCT
 * \return Whether or not they are equivalent
 */
[[nodiscard]] constexpr bool operator==(const TIMESTAMP_STRUCT& x,
                                        const TIMESTAMP_STRUCT& y) noexcept
{
  return x.year == y.year
    && x.month == y.month
    && x.day == y.day
    && x.hour == y.hour
    && x.minute == y.minute
    && x.second == y.second
    && x.fraction == y.fraction;
}
/**
 * \brief Less than operator
 * \param x First TIMESTAMP_STRUCT
 * \param y Second TIMESTAMP_STRUCT
 * \return Whether or not the first is less than the second
 */
[[nodiscard]] constexpr bool operator<(const TIMESTAMP_STRUCT& x,
                                       const TIMESTAMP_STRUCT& y) noexcept
{
  if (x.year == y.year)
  {
    if (x.month == y.month)
    {
      if (x.day == y.day)
      {
        if (x.minute == y.minute)
        {
          if (x.second == y.second)
          {
            return x.fraction < y.fraction;
          }
          return x.second < y.second;
        }
        return x.minute < y.minute;
      }
      return x.day < y.day;
    }
    return x.month < y.month;
  }
  return x.year < y.year;
}
/**
 * \brief Greater than operator
 * \param x First TIMESTAMP_STRUCT
 * \param y Second TIMESTAMP_STRUCT
 * \return Whether or not the first is greater than the second
 */
[[nodiscard]] constexpr bool operator>(const TIMESTAMP_STRUCT& x,
                                       const TIMESTAMP_STRUCT& y) noexcept
{
  return !(x == y || x < y);
}
/**
 * \brief Convert to local time
 * \param s Input value
 * \param t Output value
 */
void to_tm(const TIMESTAMP_STRUCT& s, tm* t) noexcept;
/**
 * \brief Convert to GMT
 * \param s Input value
 * \param t Output value
 */
void to_tm_gm(const TIMESTAMP_STRUCT& s, tm* t) noexcept;
/**
 * \brief Convert to TIMESTAMP_STRUCT
 * \param t Input value
 * \param s Output value
 */
void to_ts(const tm& t, TIMESTAMP_STRUCT* s) noexcept;
}
}
