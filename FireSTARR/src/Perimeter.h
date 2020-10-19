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
#include <list>
#include <string>
#include "Location.h"
#include "Point.h"
namespace firestarr
{
namespace wx
{
class FwiWeather;
}
namespace topo
{
class Environment;
/**
 * \brief Perimeter for an existing fire to initialize a simulation with.
 */
class Perimeter
{
public:
  /**
   * \brief Initialize perimeter from a file
   * \param perim File to read from
   * \param point Origin of fire
   * \param env Environment to apply Perimeter to
   */
  Perimeter(const string& perim, const Point& point, const Environment& env);
  /**
   * \brief Create a Perimeter of the given size at the given Location
   * \param location Location to center Perimeter on
   * \param size Size of Perimeter to create
   * \param yesterday Weather from the day before
   * \param env Environment to apply Perimeter to
   */
  Perimeter(const Location& location,
            size_t size,
            const wx::FwiWeather& yesterday,
            const Environment& env);
  /**
   * \brief List of all burned Locations
   * \return All Locations burned by this Perimeter
   */
  [[nodiscard]] const list<Location>& burned() const noexcept;
  /**
   * \brief List of all Locations along the edge of this Perimeter
   * \return All Locations along the edge of this Perimeter
   */
  [[nodiscard]] const list<Location>& edge() const noexcept;
private:
  /**
   * \brief List of all burned Locations
   */
  list<Location> burned_;
  /**
   * \brief List of all Locations along the edge of this Perimeter
   */
  list<Location> edge_;
};
}
}
