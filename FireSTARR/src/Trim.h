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
#include <string>
// from https://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
namespace firestarr
{
namespace util
{
/**
 * \brief Remove whitespace from left side of string
 * \param s string to trim
 */
void trim_left(string* s);
/**
 * \brief Remove whitespace from right side of string
 * \param s string to trim
 */
void trim_right(string* s);
/**
 * \brief Remove whitespace from both sides of string
 * \param s string to trim
 */
void trim(string* s);
/**
 * \brief Return new string with whitespace removed from left side
 * \param s string to trim
 * \return new string with whitespace removed from left side
 */
[[nodiscard]] string trim_left_copy(string s);
/**
 * \brief Return new string with whitespace removed from right side
 * \param s string to trim
 * \return new string with whitespace removed from right side
 */
[[nodiscard]] string trim_right_copy(string s);
/**
 * \brief Return new string with whitespace removed from both sides
 * \param s string to trim
 * \return new string with whitespace removed from both sides
 */
[[nodiscard]] string trim_copy(string s);
}
}
