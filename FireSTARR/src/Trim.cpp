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
#include "Trim.h"
// from https://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
namespace firestarr
{
namespace util
{
// trim from start (in place)
void trim_left(string* s)
{
  s->erase(s->begin(),
           find_if(s->begin(),
                   s->end(),
                   [](const int ch) noexcept
                   {
                     return !isspace(ch);
                   }));
}
// trim from end (in place)
void trim_right(string* s)
{
  s->erase(find_if(s->rbegin(),
                   s->rend(),
                   [](const int ch) noexcept
                   {
                     return !isspace(ch);
                   }).base(),
           s->end());
}
// trim from both ends (in place)
void trim(string* s)
{
  trim_left(s);
  trim_right(s);
}
// trim from start (copying)
string trim_left_copy(string s)
{
  trim_left(&s);
  return s;
}
// trim from end (copying)
string trim_right_copy(string s)
{
  trim_right(&s);
  return s;
}
// trim from both ends (copying)
string trim_copy(string s)
{
  trim(&s);
  return s;
}
}
}
