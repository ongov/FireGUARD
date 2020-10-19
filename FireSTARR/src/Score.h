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
#include "stdafx.h"
#include "Database.h"
namespace firestarr
{
namespace wx
{
/**
 * \brief The WeatherSHIELD score for a specific year.
 */
class Score
{
public:
  /**
   * \brief Average match percentage for the year
   * \return Average match percentage for the year
   */
  [[nodiscard]] constexpr double average() const noexcept { return average_; }
  /**
   * \brief Grade for this year
   * \return Grade for this year
   */
  [[nodiscard]] constexpr double grade() const noexcept { return grade_; }
  /**
   * \brief Year this Score is for
   * \return Year this Score is for
   */
  [[nodiscard]] constexpr int year() const noexcept { return year_; }
  /**
   * \brief Constructor
   * \param year Year Score is from
   * \param average Average match percentage
   * \param grade Calculated grade
   */
  constexpr Score(const int year, const double average, const double grade) noexcept
    : average_(average), grade_(grade), year_(year)
  {
  }
  /**
   * \brief Construct a Score by reading from Database
   * \param db Database to read from
   * \return Score that has been read
   */
  [[nodiscard]] static Score readScore(util::Database* db) noexcept
  {
    // HACK: do it this way so that we know database calls are in this order
    const auto yr = db->getInteger();
    const auto avg = db->getDouble();
    const auto grd = db->getDouble<4>();
    return {yr, avg, grd};
  }
#pragma warning(suppress: 26495)
  /**
   * \brief Construct by reading from Database
   * \param db Database to read from
   */
  explicit Score(util::Database* db) noexcept
    : Score(readScore(db))
  {
  }
private:
  /**
   * \brief Average match percentage for the year
   */
  double average_;
  /**
   * \brief Grade for this year
   */
  double grade_;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Year this Score is for
   */
  int year_;
};
#pragma warning (pop)
}
}
