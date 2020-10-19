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
#include "Database.h"
#include "Point.h"
namespace firestarr
{
namespace wx
{
/**
 * \brief A model within the WxSHIELD ensemble set.
 */
class WeatherModel
{
public:
  /**
   * \brief Time that model data was generated
   * \return Time that model data was generated
   */
  [[nodiscard]] constexpr const TIMESTAMP_STRUCT& generated() const { return generated_; }
  /**
   * \brief Name of this model
   * \return Name of this model
   */
  [[nodiscard]] constexpr const wstring& name() const { return name_; }
  /**
   * \brief Point this model represents
   * \return Point this model represents
   */
  [[nodiscard]] constexpr const topo::Point& point() const { return point_; }
  /**
   * \brief Distance that model data is from the Point being represented (m)
   * \return Distance that model data is from the Point being represented (m)
   */
  [[nodiscard]] constexpr double distanceFrom() const { return distance_from_; }
  /**
   * \brief Constructor
   * \param generated Time model was generated for
   * \param name Name of the model
   * \param point Point model was generated for
   * \param distance_from Distance model data was from Point
   */
  WeatherModel(const TIMESTAMP_STRUCT& generated,
               wstring&& name,
               const topo::Point& point,
               double distance_from) noexcept;
  /**
   * \brief Destructor
   */
  ~WeatherModel() = default;
  /**
   * \brief Construct by reading from Database
   * \param db Database to read from
   */
  explicit WeatherModel(util::Database* db) noexcept;
  /**
   * \brief Move constructor
   * \param rhs WeatherModel to move from
   */
  WeatherModel(WeatherModel&& rhs) noexcept = default;
  /**
   * \brief Copy constructor
   * \param rhs WeatherModel to copy from
   */
  WeatherModel(const WeatherModel& rhs) = default;
  /**
   * \brief Move assignment
   * \param rhs WeatherModel to move from
   * \return This, after assignment
   */
  WeatherModel& operator=(WeatherModel&& rhs) noexcept = default;
  /**
   * \brief Copy assignment
   * \param rhs WeatherModel to copy from
   * \return This, after assignment
   */
  WeatherModel& operator=(const WeatherModel& rhs);
private:
  /**
   * \brief When this was generated
   */
  TIMESTAMP_STRUCT generated_;
  /**
   * \brief Name of this
   */
  wstring name_;
  /**
   * \brief Point this represents
   */
  topo::Point point_;
  /**
   * \brief Distance actual point for this is from represented Point (m)
   */
  double distance_from_;
};
/**
 * \brief Provides ordering for WeatherModel comparison.
 */
struct ModelCompare
{
  /**
   * \brief Provides ordering for WeatherModel comparison
   * \param x First WeatherModel to compare
   * \param y Second WeatherModel to compare
   * \return Whether or not x <= y
   */
  [[nodiscard]] bool operator()(const WeatherModel& x,
                                const WeatherModel& y) const noexcept;
};
}
}
