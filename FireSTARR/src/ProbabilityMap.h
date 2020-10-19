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
#include <vector>
#include "GridMap.h"
#include "Statistics.h"
namespace firestarr
{
namespace sim
{
class Model;
class IntensityMap;
/**
 * \brief Map of the percentage of simulations in which a Cell burned in each intensity category.
 */
class ProbabilityMap
{
public:
  ProbabilityMap() = delete;
  ~ProbabilityMap() = default;
  ProbabilityMap(const ProbabilityMap& rhs) noexcept = delete;
  ProbabilityMap(ProbabilityMap&& rhs) noexcept = delete;
  ProbabilityMap& operator=(const ProbabilityMap& rhs) noexcept = delete;
  ProbabilityMap& operator=(ProbabilityMap&& rhs) noexcept = delete;
  /**
   * \brief Constructor
   * \param for_what What type of fire size is being tracked (Actuals vs Fire)
   * \param time Time in simulation this ProbabilityMap represents
   * \param start_time Start time of simulation
   * \param min_value Lower bound of 'low' intensity range
   * \param low_max Upper bound of 'low' intensity range
   * \param med_max Upper bound of 'moderate' intensity range
   * \param max_value Upper bound of 'high' intensity range
   * \param grid_info GridBase to use for extent of this
   */
  ProbabilityMap(const char* for_what,
                 double time,
                 double start_time,
                 int min_value,
                 int low_max,
                 int med_max,
                 int max_value,
                 const data::GridBase& grid_info);
  /**
   * \brief Create a copy of this that is empty
   * \return New empty Probability with same range bounds and times
   */
  ProbabilityMap* copyEmpty() const;
  /**
   * \brief Combine results from another ProbabilityMap into this one
   * \param rhs ProbabilityMap to combine from
   */
  void addProbabilities(const ProbabilityMap& rhs);
  /**
   * \brief Add in an IntensityMap to the appropriate probability grid based on each cell burn intensity
   * \param for_time IntensityMap to add results from
   */
  void addProbability(const IntensityMap& for_time);
  /**
   * \brief List of sizes of IntensityMaps that have been added
   * \return List of sizes of IntensityMaps that have been added
   */
  [[nodiscard]] vector<double> getSizes() const;
  /**
   * \brief Generate Statistics on sizes of IntensityMaps that have been added
   * \return Generate Statistics on sizes of IntensityMaps that have been added
   */
  [[nodiscard]] util::Statistics getStatistics() const;
  /**
   * \brief Number of sizes that have been added
   * \return Number of sizes that have been added
   */
  [[nodiscard]] size_t numSizes() const noexcept;
  /**
   * \brief Output Statistics to log
   */
  void show() const;
  /**
   * \brief Save list of sizes
   * \param dir Directory to save to
   * \param base_name Base name of file to save into
   */
  void saveSizes(const string& dir, const string& base_name) const;
  /**
   * \brief Save total, low, moderate, and high maps, and output information to log
   * \param model Model this was derived from
   * \param start_time Start time of simulation
   * \param for_actuals Whether or not this is from actual indices
   * \param time Time for these maps
   * \param start_day Day that simulation started
   */
  void saveAll(const Model& model,
               const tm& start_time,
               bool for_actuals,
               double time,
               double start_day) const;
  /**
   * \brief Save map representing all intensities
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void saveTotal(const string& dir, const string& base_name) const;
  /**
   * \brief Save map representing high intensities
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void saveHigh(const string& dir, const string& base_name) const;
  /**
   * \brief Save map representing moderate intensities
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void saveModerate(const string& dir, const string& base_name) const;
  /**
   * \brief Save map representing low intensities
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void saveLow(const string& dir, const string& base_name) const;
private:
  /**
   * \brief Map representing all intensities
   */
  data::GridMap<size_t> all_;
  /**
   * \brief Map representing high intensities
   */
  data::GridMap<size_t> high_;
  /**
   * \brief Map representing moderate intensities
   */
  data::GridMap<size_t> med_;
  /**
   * \brief Map representing low intensities
   */
  data::GridMap<size_t> low_;
  /**
   * \brief List of sizes for perimeters that have been added
   */
  vector<double> sizes_{};
  /**
   * \brief What type of fire size is being tracked (Actuals vs Fire)
   */
  const char* const for_what_;
  /**
   * \brief Time in simulation this ProbabilityMap represents
   */
  const double time_;
  /**
   * \brief Start time of simulation
   */
  const double start_time_;
  /**
   * \brief Mutex for parallel access
   */
  mutable mutex mutex_;
  /**
   * \brief Lower bound of 'low' intensity range
   */
  int min_value_;
  /**
   * \brief Upper bound of 'high' intensity range
   */
  int max_value_;
  /**
   * \brief Upper bound of 'low' intensity range
   */
  const int low_max_;
  /**
   * \brief Upper bound of 'moderate' intensity range
   */
  const int med_max_;
};
}
}
