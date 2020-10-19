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
// #define VLD_FORCE_ENABLE
// #include "vld.h"
// ReSharper disable CppInconsistentNaming
#define _USE_MATH_DEFINES
// ReSharper restore CppInconsistentNaming
#define NOMINMAX
#pragma warning (push)
#pragma warning (disable: 4355)
#pragma warning (disable: 4365)
#pragma warning (disable: 4514)
#pragma warning (disable: 4571)
#pragma warning (disable: 4623)
#pragma warning (disable: 4625)
#pragma warning (disable: 4626)
#pragma warning (disable: 4668)
#pragma warning (disable: 4710)
#pragma warning (disable: 4711)
#pragma warning (disable: 4774)
#pragma warning (disable: 4820)
#pragma warning (disable: 5026)
#pragma warning (disable: 5027)
#pragma warning (disable: 5039)
#pragma warning (disable: 5045)
#include <algorithm>
#include <array>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cmath>
#include <cstdarg>
#include <cstdio>
#include <execution>
#include <fstream>
#include <functional>
#include <future>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <limits>
#include <locale>
#include <map>
#include <memory>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include "geo_normalize.h"
#include "geotiff.h"
#include "geovalues.h"
#include "tiff.h"
#include "tiffio.h"
#include "xtiffio.h"
#include <Windows.h>
#include <basetsd.h>
#include <direct.h>
#include <sql.h>
#include <sqlext.h>
#include <sys/stat.h>
#pragma warning (pop)
// unreferenced inline function has been removed
#pragma warning (disable: 4514)
// Informational: catch(...) semantics changed since Visual C++ 7.1; structured exceptions (SEH) are no longer caught
#pragma warning (disable: 4571)
// function 'X' selected for automatic inline expansion
#pragma warning (disable: 4623)
// function not inlined
#pragma warning (disable: 4710)
// selected for automatic inline expansion
#pragma warning (disable: 4711)
// Do not assign the result of an allocation or a function call with an owner<T> return value to a raw pointer, use owner<T> instead
#pragma warning (disable: 26400)
// Do not delete a raw pointer that is not an owner<T>
#pragma warning (disable: 26401)
// Return a scoped object instead of a heap-allocated if it has a move constructor
#pragma warning (disable: 26402)
// Reset or explicitly delete an owner<T> pointer
#pragma warning (disable: 26403)
// Do not assign to an owner<T> which may be in valid state
#pragma warning (disable: 26405)
// Do not assign a raw pointer to an owner<T>
#pragma warning (disable: 26406)
// Prefer scoped objects, don't heap-allocate unnecessarily
#pragma warning (disable: 26407)
// Avoid calling new and delete explicitly, use std::make_unique<T> instead
#pragma warning (disable: 26409)
// Global initializer calls a non-constexpr function
#pragma warning (disable: 26426)
// Symbol is never tested for nullness, it can be marked as not_null
#pragma warning (disable: 26429)
// Function hides a non-virtual function
#pragma warning (disable: 26434)
// prefer to use gsl::at()
#pragma warning (disable: 26446)
// Don't use a static_cast for arithmetic conversions. Use brace initialization, gsl::narrow_cast or gsl::narrow
#pragma warning (disable: 26472)
// Don't use pointer arithmetic. Use span instead
#pragma warning (disable: 26481)
// Only index into arrays using constant expressions
#pragma warning (disable: 26482)
// No array to pointer decay
#pragma warning (disable: 26485)
using std::abs;
using std::array;
using std::async;
using std::atomic;
using std::cout;
using std::endl;
using std::fixed;
using std::function;
using std::future;
using std::get;
using std::getline;
using std::hash;
using std::ifstream;
using std::istringstream;
using std::launch;
using std::list;
using std::lock_guard;
using std::make_shared;
using std::make_tuple;
using std::make_unique;
using std::map;
using std::max;
using std::min;
using std::mt19937;
using std::mutex;
using std::numeric_limits;
using std::ofstream;
using std::ostream;
using std::ostringstream;
using std::pair;
using std::put_time;
using std::runtime_error;
using std::set;
using std::setprecision;
using std::shared_ptr;
using std::stod;
using std::stoi;
using std::stol;
using std::string;
using std::string_view;
using std::stringstream;
using std::to_string;
using std::to_wstring;
using std::tuple;
using std::uniform_real_distribution;
using std::unique_ptr;
using std::unordered_map;
using std::vector;
using std::wstring;
namespace firestarr
{
/**
 * \brief Size of the hash of a Cell
 */
using HashSize = unsigned __int32;
/**
 * \brief Size of the index for a Cell
 */
using CellIndex = char;
/**
 * \brief A row or column index for a grid
 */
using Idx = int16;
/**
 * \brief Type used for fuel raster
 */
using FuelSize = uint16;
/**
 * \brief Type used for aspect raster
 */
using AspectSize = uint16;
/**
 * \brief Type used for elevation raster
 */
using ElevationSize = int16;
/**
 * \brief Type used for slope raster
 */
using SlopeSize = uint8;
/**
 * \brief Type used for storing intensities
 */
using IntensitySize = uint16;
/**
 * \brief A day (0 - 366)
 */
using Day = uint16;
static constexpr Day MAX_DAYS = 366;
// HACK: make sure this is 4002 or less since that's what the geoprocessing results in
/**
 * \brief Maximum number of columns for an Environment
 */
static constexpr Idx MAX_COLUMNS = 2048;
/**
 * \brief Maximum number of rows for an Environment
 */
static constexpr Idx MAX_ROWS = MAX_COLUMNS;
/**
 * \brief Maximum slope that affects ISI - everything after this is the same factor
 */
static constexpr auto MAX_SLOPE_FOR_FACTOR = 60;
/**
 * \brief Maximum slope that can be stored - this is used in the horizontal distance calculation
 */
static constexpr auto MAX_SLOPE_FOR_DISTANCE = 127;
/**
 * \brief Number of all possible fuels in simulation
 */
static constexpr auto NUMBER_OF_FUELS = 56;
/**
 * \brief 2*pi
 */
static constexpr auto M_2_X_PI = 2.0 * M_PI;
/**
 * \brief 3/2*pi
 */
static constexpr auto M_3_X_PI_2 = 3.0 * M_PI_2;
/**
 * \brief Number of hours in a day
 */
static constexpr int DAY_HOURS = 24;
/**
 * \brief Number of minutes in an hour
 */
static constexpr int HOUR_MINUTES = 60;
/**
 * \brief Number of seconds in a minute
 */
static constexpr int MINUTE_SECONDS = 60;
/**
 * \brief Number of minutes in a day
 */
static constexpr int DAY_MINUTES = DAY_HOURS * HOUR_MINUTES;
/**
 * \brief Number of seconds in a day
 */
static constexpr int DAY_SECONDS = DAY_MINUTES * MINUTE_SECONDS;
/**
 * \brief Number of hours in a year
 */
static constexpr int YEAR_HOURS = MAX_DAYS * DAY_HOURS;
/**
 * \brief Array of results of a function for all possible integer percent slopes
 */
using SlopeTableArray = array<double, MAX_SLOPE_FOR_DISTANCE + 1>;
/**
 * \brief Array of results of a function for all possible integer angles in degrees
 */
using AngleTableArray = array<double, 361>;
/**
 * \brief A single bit set to 1
 */
static constexpr auto BIT = static_cast<uint64_t>(0x1);
/**
 * \brief Size to use for representing fuel types
 */
using FuelCodeSize = uint8;
/**
 * \brief Size to use for representing the data in a Cell
 */
using Topo = uint64_t;
/**
 * \brief Size to use for representing sub-coordinates for location within a Cell
 */
using SubSize = uint16;
/**
 * \brief Coordinates (row, column, sub-row, sub-column)
 */
using Coordinates = tuple<Idx, Idx, SubSize, SubSize>;
/**
 * \brief Type of clock to use for times
 */
using Clock = std::chrono::steady_clock;
}
