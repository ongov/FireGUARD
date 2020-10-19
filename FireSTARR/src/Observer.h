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
#include <memory>
#include <string>
#include "Event.h"
#include "GridMap.h"
#include "Scenario.h"
namespace firestarr
{
namespace sim
{
class Event;
class Scenario;
/**
 * \brief Interface for observers that get notified when cells burn so they can track things.
 */
class IObserver
{
public:
  virtual ~IObserver() = default;
  IObserver(const IObserver& rhs) = delete;
  IObserver(IObserver&& rhs) = delete;
  IObserver& operator=(const IObserver& rhs) = delete;
  IObserver& operator=(IObserver&& rhs) = delete;
  /**
   * \brief Handle given event
   * \param event Event to handle
   * \return None
   */
  virtual void handleEvent(const Event& event) = NULL;
  /**
   * \brief Save observations
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   * \return None
   */
  virtual void save(const string& dir, const string& base_name) const = NULL;
  /**
   * \brief Clear all observations
   * \return None
   */
  virtual void reset() = NULL;
  /**
   * \brief Make name to save file as
   * \param base_name Base file name
   * \param suffix Suffix to append
   * \return File name to use based on inputs
   */
  static string makeName(const string& base_name, const string& suffix);
protected:
  IObserver() = default;
};
/**
 * \brief An IObserver that tracks notification data using a GridMap.
 * \tparam T Type of map that is being tracked
 */
template <typename T>
class MapObserver
  : public IObserver
{
public:
  ~MapObserver() = default;
  MapObserver(const MapObserver& rhs) = delete;
  MapObserver(MapObserver&& rhs) = delete;
  MapObserver& operator=(const MapObserver& rhs) = delete;
  MapObserver& operator=(MapObserver&& rhs) = delete;
  /**
   * \brief Keeps observations in a map
   * \param scenario Scenario to observe
   * \param nodata Value to use for no data
   * \param suffix Suffix to use on saved file
   */
  MapObserver(const Scenario& scenario, T nodata, string suffix)
    : map_(scenario.model().environment().makeMap<T>(nodata)), suffix_(std::move(suffix))
  {
  }
  /**
   * \brief Function that returns the value we care about regarding the Event
   * \param event 
   * \return 
   */
  [[nodiscard]] virtual T getValue(const Event& event) const = NULL;
  /**
   * \brief Handle given event
   * \param event Event to handle
   */
  void handleEvent(const Event& event) override
  {
    map_->set(event.cell(), getValue(event));
  }
  /**
   * \brief Save observations
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void save(const string& dir, const string& base_name) const override
  {
    map_->saveToAsciiFile(dir, makeName(base_name, suffix_));
  }
  /**
   * \brief Clear all observations
   */
  void reset() noexcept override { map_->clear(); }
private:
  /**
   * \brief Map of observations
   */
  unique_ptr<data::GridMap<T>> map_;
  /**
   * \brief Suffix to append to file during save
   */
  string suffix_;
};
/**
 * \brief Tracks when fire initially arrives in a Cell.
 */
class ArrivalObserver final
  : public MapObserver<double>
{
public:
  ~ArrivalObserver() = default;
  ArrivalObserver(const ArrivalObserver& rhs) = delete;
  ArrivalObserver(ArrivalObserver&& rhs) = delete;
  ArrivalObserver& operator=(const ArrivalObserver& rhs) = delete;
  ArrivalObserver& operator=(ArrivalObserver&& rhs) = delete;
  /**
   * \brief Constructor
   * \param scenario Scenario to track
   */
  explicit ArrivalObserver(const Scenario& scenario);
  [[nodiscard]] double getValue(const Event& event) const noexcept override;
};
/**
 * \brief Tracks source Cell that fire arrived in Cell from.
 */
class SourceObserver final
  : public MapObserver<CellIndex>
{
public:
  ~SourceObserver() = default;
  SourceObserver(const SourceObserver& rhs) = delete;
  SourceObserver(SourceObserver&& rhs) = delete;
  SourceObserver& operator=(const SourceObserver& rhs) = delete;
  SourceObserver& operator=(SourceObserver&& rhs) = delete;
  /**
   * \brief Constructor
   * \param scenario Scenario to track
   */
  explicit SourceObserver(const Scenario& scenario);
  [[nodiscard]] CellIndex getValue(const Event& event) const noexcept override;
};
/**
 * \brief Tracks the intensity that Cells burn at.
 */
class IntensityObserver final
  : public IObserver
{
public:
  ~IntensityObserver() = default;
  IntensityObserver(const IntensityObserver& rhs) = delete;
  IntensityObserver(IntensityObserver&& rhs) = delete;
  IntensityObserver& operator=(const IntensityObserver& rhs) = delete;
  IntensityObserver& operator=(IntensityObserver&& rhs) = delete;
  /**
   * \brief Constructor
   * \param scenario Scenario to observe
   * \param suffix Suffix to append to output file
   */
  IntensityObserver(const Scenario& scenario, string suffix) noexcept;
  /**
   * \brief Handle given event
   * \param event Event to handle
   */
  void handleEvent(const Event& event) noexcept override;
  /**
   * \brief Save observations
   * \param dir Directory to save to
   * \param base_name Base file name to save to
   */
  void save(const string& dir, const string& base_name) const override;
  /**
   * \brief Clear all observations
   */
  void reset() noexcept override;
private:
  /**
   * \brief Scenario being observed
   */
  const Scenario& scenario_;
  /**
   * \brief Suffix to append to output file
   */
  string suffix_;
};
}
}
