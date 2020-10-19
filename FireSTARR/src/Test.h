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
namespace sim
{
static const double TEST_GRID_SIZE = 100.0;
static const char TEST_PROJ4[] =
  "+proj=tmerc +lat_0=0.000000000 +lon_0=-90.000000000"
  " +k=0.999600 +x_0=500000.000 +y_0=0.000 +a=6378137.000 +b=6356752.314 +units=m";
static const double TEST_XLLCORNER = 324203.990666;
static const double TEST_YLLCORNER = 12646355.311160;
/**
 * \brief Runs test cases for constant weather and fuel based on given arguments.
 * \param argc 
 * \param argv 
 * \return 
 */
int test(int argc, const char* const argv[]);
}
}
