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
namespace topo
{
/**
 * \brief A geographic location in lat/long coordinates.
 */
class Point
{
public:
  /**
   * \brief Constructor
   * \param latitude Latitude (decimal degrees)
   * \param longitude Longitude (decimal degrees)
   */
  constexpr Point(const double latitude, const double longitude) noexcept
    : latitude_(latitude), longitude_(longitude)
  {
  }
  ~Point() noexcept = default;
  /**
   * \brief Copy constructor
   * \param rhs Point to copy from
   */
  Point(const Point& rhs) noexcept = default;
  /**
   * \brief Move constructor
   * \param rhs Point to move from
   */
  Point(Point&& rhs) noexcept = default;
  /**
   * \brief Copy assignment
   * \param rhs Point to copy from
   * \return This, after assignment
   */
  Point& operator=(const Point& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs Point to move from
   * \return This, after assignment
   */
  Point& operator=(Point&& rhs) noexcept = default;
  /**
   * \brief Latitude (decimal degrees)
   * \return Latitude (degrees)
   */
  [[nodiscard]] constexpr double latitude() const noexcept { return latitude_; }
  /**
   * \brief Longitude (decimal degrees)
   * \return Longitude (decimal degrees)
   */
  [[nodiscard]] constexpr double longitude() const noexcept { return longitude_; }
private:
  /**
   * \brief Latitude (decimal degrees)
   */
  double latitude_;
  /**
   * \brief Longitude (decimal degrees)
   */
  double longitude_;
};
}
}
