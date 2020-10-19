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
#include "Util.h"
namespace firestarr
{
namespace util
{
/**
 * \brief A table initialized using the given function ranging over the number of digits and precision.
 * \tparam Fct Function to apply over the range of values
 * \tparam IndexDigits Number of digits to use for range of values
 * \tparam Precision Precision in decimal places to use for range of values
 */
template <double(*Fct)(double), int IndexDigits = 3, int Precision = 1>
class LookupTable
{
  /**
   * \brief Array with enough space for function called with specific number of digits and precision
   */
  using ValuesArray = array<double, pow_int<IndexDigits>(10) * pow_int<Precision>(10)>;
  /**
   * \brief Array of values from calling function
   */
  const ValuesArray values_;
  /**
   * \brief Call function with range of values with given precision
   * \return Results of function with range of values with given precision
   */
  [[nodiscard]] constexpr ValuesArray makeValues()
  {
    ValuesArray values{};
    for (size_t i = 0; i < values.size(); ++i)
    {
      const auto value = i / static_cast<double>(pow_int<Precision>(10));
      values[i] = Fct(value);
    }
    return values;
  }
public:
  constexpr explicit LookupTable() noexcept
    : values_(makeValues())
  {
  }
  ~LookupTable() = default;
  LookupTable(LookupTable&& rhs) noexcept = delete;
  LookupTable(const LookupTable& rhs) noexcept = delete;
  LookupTable& operator=(LookupTable&& rhs) noexcept = delete;
  LookupTable& operator=(const LookupTable& rhs) noexcept = delete;
  /**
   * \brief Get result of function lookup table was initialized with for given value
   * \param value value to get lookup result for
   * \return result of lookup for function at value
   */
  [[nodiscard]] constexpr double operator()(const double value) const
  {
    return values_.at(static_cast<size_t>(value * pow_int<Precision>(10)));
  }
};
}
}
