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
namespace util
{
/**
 * \brief Keeps track of data structures so they can be reused instead of freeing and reacquiring them.
 * \tparam T Type to keep a pool of
 */
template <class T>
class MemoryPool
{
public:
  ~MemoryPool() = default;
  MemoryPool() = default;
  MemoryPool(const MemoryPool& rhs) = delete;
  MemoryPool(MemoryPool&& rhs) = delete;
  MemoryPool& operator=(const MemoryPool& rhs) = delete;
  MemoryPool& operator=(MemoryPool&& rhs) = delete;
  /**
   * \brief Acquire a new T either by returning an unused one or allocating a new one
   * \return a T*
   */
  T* acquire()
  {
    if (!assets_.empty())
    {
      lock_guard<mutex> lock(mutex_);
      // check again once we have the mutex
      if (!assets_.empty())
      {
        const auto v = std::move(assets_.back()).release();
        assets_.pop_back();
        // this is already reset before it was given back
        return v;
      }
    }
    return new T();
  }
  /**
   * \brief Add a T* to the pool of available T*s
   * \param asset T* to return to pool
   */
  void release(T* asset)
  {
    if (nullptr == asset)
    {
      return;
    }
    lock_guard<mutex> lock(mutex_);
    assets_.push_back(unique_ptr<T>(asset));
  }
private:
  /**
   * \brief Mutex for parallel access
   */
  mutable mutex mutex_{};
  /**
   * \brief Available assets that can be acquired
   */
  vector<unique_ptr<T>> assets_{};
};
/**
 * \brief Call clear on T before releasing it
 * \tparam T Type of item to release
 * \param t Item to release
 * \param pool MemoryPool to release item into
 * \return nullptr
 */
template <typename T>
T* check_clear(T* t, MemoryPool<T>& pool)
{
  if (nullptr != t)
  {
    t->clear();
    pool.release(t);
  }
  return nullptr;
}
/**
 * \brief Call reset on T before releasing it
 * \tparam T Type of item to release
 * \param t Item to release
 * \param pool MemoryPool to release item into
 * \return nullptr
 */
template <typename T>
T* check_reset(T* t, MemoryPool<T>& pool)
{
  if (nullptr != t)
  {
    t->reset();
    pool.release(t);
  }
  return nullptr;
}
}
}
