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
#include "SafeVector.h"
#include "Statistics.h"
#include "Util.h"
namespace firestarr
{
namespace util
{
SafeVector::SafeVector(const SafeVector& rhs)
  : values_(rhs.values_)
{
}
SafeVector::SafeVector(SafeVector&& rhs) noexcept
  : values_(std::move(rhs.values_))
{
}
#pragma warning (push)
#pragma warning (disable: 26447)
SafeVector& SafeVector::operator=(const SafeVector& rhs) noexcept
{
  try
  {
    lock_guard<mutex> lock(mutex_);
    values_ = rhs.values_;
    return *this;
  }
  catch (...)
  {
    std::terminate();
  }
}
#pragma warning (pop)
#pragma warning (push)
#pragma warning (disable: 26447)
SafeVector& SafeVector::operator=(SafeVector&& rhs) noexcept
{
  try
  {
    lock_guard<mutex> lock(mutex_);
    values_ = std::move(rhs.values_);
    return *this;
  }
  catch (...)
  {
    std::terminate();
  }
}
#pragma warning (pop)
void SafeVector::addValue(const double value)
{
  lock_guard<mutex> lock(mutex_);
  static_cast<void>(insert_sorted(&values_, value));
}
vector<double> SafeVector::getValues() const
{
  lock_guard<mutex> lock(mutex_);
  return values_;
}
Statistics SafeVector::getStatistics() const
{
  return Statistics{getValues()};
}
size_t SafeVector::size() const noexcept
{
  return values_.size();
}
}
}
