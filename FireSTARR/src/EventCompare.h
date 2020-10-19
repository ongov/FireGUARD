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
#include "Event.h"
namespace firestarr
{
namespace sim
{
/**
 * \brief Defines how Events are compared for sorting.
 */
struct EventCompare
{
  /**
   * \brief Defines ordering on Events
   * \param x First Event
   * \param y Second Event
   * \return Whether first Event is less than second Event
   */
  [[nodiscard]] constexpr bool operator()(const Event& x, const Event& y) const
  {
    if (x.time() == y.time())
    {
      if (x.type() == y.type())
      {
        return x.cell().hash() < y.cell().hash();
      }
      return x.type() < y.type();
    }
    return x.time() < y.time();
  }
};
}
}
