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
#include <vector>
namespace firestarr
{
namespace util
{
class Statistics;
/**
 * \brief A vector with added thread safety.
 */
class SafeVector
{
  /**
   * \brief Vector of stored values
   */
  vector<double> values_{};
  /**
   * \brief Mutex for parallel access
   */
  mutable mutex mutex_{};
public:
  /**
   * \brief Destructor
   */
  ~SafeVector() = default;
  /**
   * \brief Construct empty SafeVector
   */
  SafeVector() = default;
  /**
   * \brief Copy constructor
   * \param rhs SafeVector to copy from
   */
  SafeVector(const SafeVector& rhs);
  /**
   * \brief Move constructor
   * \param rhs SafeVector to move from
   */
  SafeVector(SafeVector&& rhs) noexcept;
  /**
   * \brief Copy assignment operator
   * \param rhs SafeVector to copy from
   * \return This, after assignment
   */
  SafeVector& operator=(const SafeVector& rhs) noexcept;
  /**
   * \brief Move assignment operator
   * \param rhs SafeVector to move from
   * \return This, after assignment
   */
  SafeVector& operator=(SafeVector&& rhs) noexcept;
  /**
   * \brief Add a value to the SafeVector
   * \param value Value to add
   */
  void addValue(double value);
  /**
   * \brief Get a vector with the stored values
   * \return A vector with the stored values
   */
  [[nodiscard]] vector<double> getValues() const;
  /**
   * \brief Calculate Statistics for values in this SafeVector
   * \return Statistics for values in this SafeVector
   */
  [[nodiscard]] Statistics getStatistics() const;
  /**
   * \brief Number of values in the SafeVector
   * \return Size of the SafeVector
   */
  [[nodiscard]] size_t size() const noexcept;
};
}
}
