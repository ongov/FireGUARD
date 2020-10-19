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
#include "IntensityMap.h"
#include "MemoryPool.h"
#include "Model.h"
#include "Perimeter.h"
namespace firestarr
{
namespace sim
{
static mutex MUTEX_MAPS;
static vector<unique_ptr<data::GridMap<IntensitySize>>> MAPS;
static void release_map(unique_ptr<data::GridMap<IntensitySize>> map) noexcept
{
  map->clear();
#pragma warning (push)
#pragma warning (disable: 26447)
  try
  {
    lock_guard<mutex> lock(MUTEX_MAPS);
    MAPS.push_back(std::move(map));
  }
  catch (...)
  {
    std::terminate();
  }
#pragma warning (pop)
}
static unique_ptr<data::GridMap<IntensitySize>> acquire_map(const Model& model) noexcept
{
#pragma warning (push)
#pragma warning (disable: 26447)
  try
  {
    lock_guard<mutex> lock(MUTEX_MAPS);
    if (!MAPS.empty())
    {
      auto result = std::move(MAPS.at(MAPS.size() - 1));
      MAPS.pop_back();
      return result;
    }
    return model.environment().makeMap<IntensitySize>(false);
  }
  catch (...)
  {
    std::terminate();
  }
#pragma warning (pop)
}
IntensityMap::IntensityMap(const Model& model) noexcept
  : model_(model),
    map_(acquire_map(model)),
    is_burned_(model.getBurnedVector())
{
}
IntensityMap::~IntensityMap() noexcept
{
  model_.releaseBurnedVector(is_burned_);
  release_map(std::move(map_));
}
void IntensityMap::applyPerimeter(const topo::Perimeter& perimeter) noexcept
{
  std::for_each(
    std::execution::par_unseq,
    perimeter.burned().begin(),
    perimeter.burned().end(),
    [this](const auto& location)
    {
      burn(location, 1);
    });
}
bool IntensityMap::canBurn(const HashSize hash) const
{
  return !hasBurned(hash);
}
bool IntensityMap::canBurn(const topo::Cell& location) const
{
  return !hasBurned(location);
}
bool IntensityMap::hasBurned(const Location& location) const
{
  return hasBurned(location.hash());
}
bool IntensityMap::hasBurned(const HashSize hash) const
{
  lock_guard<mutex> lock(mutex_);
  return (*is_burned_)[hash];
}
bool IntensityMap::isSurrounded(const Location& location) const
{
  // implement here so we can just lock once
  lock_guard<mutex> lock(mutex_);
  const auto x = location.column();
  const auto y = location.row();
  const auto min_row = static_cast<Idx>(max(y - 1, 0));
  const auto max_row = min(y + 1, MAX_ROWS - 1);
  const auto min_column = static_cast<Idx>(max(x - 1, 0));
  const auto max_column = min(x + 1, MAX_COLUMNS - 1);
  for (auto r = min_row; r <= max_row; ++r)
  {
    auto h = static_cast<size_t>(r) * MAX_COLUMNS + min_column;
    for (auto c = min_column; c <= max_column; ++c)
    {
      // actually check x, y too since we care if the cell itself is burned
      if (!(*is_burned_)[h])
      {
        return false;
      }
      ++h;
    }
  }
  return true;
}
// ReSharper disable once CppMemberFunctionMayBeConst
void IntensityMap::burn(const Location& location, const IntensitySize intensity)
{
  lock_guard<mutex> lock(mutex_);
  map_->set(location, intensity);
  (*is_burned_).set(location.hash());
}
void IntensityMap::saveToAsciiFile(const string& dir, const string& base_name) const
{
  lock_guard<mutex> lock(mutex_);
  map_->saveToAsciiFile(dir, base_name);
}
double IntensityMap::fireSize() const
{
  lock_guard<mutex> lock(mutex_);
  return map_->fireSize();
}
unordered_map<Location, IntensitySize>::const_iterator
IntensityMap::cend() const noexcept
{
  return map_->data.cend();
}
unordered_map<Location, IntensitySize>::const_iterator
IntensityMap::cbegin() const noexcept
{
  return map_->data.cbegin();
}
}
}
