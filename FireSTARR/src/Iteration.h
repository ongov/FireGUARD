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
#include <random>
#include <vector>
#include "SafeVector.h"
namespace firestarr
{
namespace sim
{
class ProbabilityMap;
class Scenario;
/**
 * \brief Represents a full set of simulations using all available weather streams.
 */
class Iteration
{
public:
  ~Iteration();
  /**
   * \brief Constructor
   * \param scenarios List of Scenarios to wrap into Iteration
   */
  explicit Iteration(vector<Scenario*> scenarios) noexcept;
  /**
   * \brief Copy constructor
   * \param rhs Iteration to copy form
   */
  Iteration(const Iteration& rhs) = default;
  /**
   * \brief Move constructor
   * \param rhs Iteration to move from
   */
  Iteration(Iteration&& rhs) = default;
  /**
   * \brief Copy assignment
   * \param rhs Iteration to copy from
   * \return This, after assignment
   */
  Iteration& operator=(const Iteration& rhs) = default;
  /**
   * \brief Move assignment
   * \param rhs Iteration to move from
   * \return This, after assignment
   */
  Iteration& operator=(Iteration&& rhs) = default;
  /**
   * \brief Create new thresholds for use in each Scenario
   * \param mt_extinction Extinction thresholds
   * \param mt_spread Spread thresholds
   * \return This
   */
  Iteration* reset(mt19937* mt_extinction, mt19937* mt_spread);
  /**
   * \brief List of Scenarios this Iteration contains
   * \return List of Scenarios this Iteration contains
   */
  const vector<Scenario*>& getScenarios() const noexcept { return scenarios_; }
  /**
   * \brief Points in time that ProbabilityMaps get saved for
   * \return Points in time that ProbabilityMaps get saved for
   */
  [[nodiscard]] vector<double> savePoints() const;
  /**
   * \brief Time that simulations start
   * \return Time that simulations start
   */
  [[nodiscard]] double startTime() const;
  /**
   * \brief Number of Scenarios in this Iteration
   * \return Number of Scenarios in this Iteration
   */
  [[nodiscard]] size_t size() const noexcept;
  /**
   * \brief SafeVector of sizes that Scenarios have resulted in
   * \return SafeVector of sizes that Scenarios have resulted in
   */
  [[nodiscard]] util::SafeVector finalSizes() const;
private:
  /**
   * \brief List of Scenarios this Iteration contains
   */
  vector<Scenario*> scenarios_;
  /**
   * \brief SafeVector of sizes that Scenarios have resulted in
   */
  util::SafeVector final_sizes_{};
};
}
}
