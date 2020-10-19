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
#include <map>
#include <string>
#include <tuple>
#include <vector>
#include "FwiStream.h"
#include "Startup.h"
#include "WeatherModel.h"
namespace firestarr
{
namespace wx
{
class Score;
/**
 * \brief Implements the WeatherSHIELD method of creating long-range weather forecasts.
 */
class WxShield
{
public:
  /**
   * \brief Initialize a WeatherSHIELD ensemble.
   * \param start_date Start date for ensemble
   * \param point Point to retrieve weather data for
   * \param num_days Number of days to generate ensemble for
   * \param save_to File to save generated weather to
   * \param ffmc Fine Fuel Moisture Code to override Startup value with
   * \param dmc Duff Moisture Code to override Startup value with
   * \param dc Drought Code to override Startup value with
   * \param apcp_0800 Accumulated Precipitation at 0800 to override Startup value with
   * \param full_wx Whether or not to include all reanalysis weather years in output
   */
  WxShield(const TIMESTAMP_STRUCT& start_date,
           const topo::Point& point,
           size_t num_days,
           const string& save_to,
           Ffmc* ffmc,
           Dmc* dmc,
           Dc* dc,
           AccumulatedPrecipitation* apcp_0800,
           bool full_wx);
  /**
   * \brief Destructor
   */
  ~WxShield() = default;
  /**
   * \brief Move constructor
   * \param rhs WxShield to move from
   */
  WxShield(WxShield&& rhs) = default;
  /**
   * \brief Copy constructor
   * \param rhs WxShield to copy from
   */
  WxShield(const WxShield& rhs);
  /**
   * \brief Move assignment
   * \param rhs WxShield to move into this one
   * \return This, after assignment
   */
  WxShield& operator=(WxShield&& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs WxShield to copy into this one
   * \return This, after assignment
   */
  WxShield& operator=(const WxShield& rhs);
  /**
   * \brief Find Scores for a date that is offset days away from the current date.
   * \param offset Number of days to offset current day by
   * \return vector of Scores for years at date given by offset
   */
  [[nodiscard]] static vector<Score> readScoreByOffset(int offset);
  /**
   * \brief Read weather data for the day before the given offset.
   * \param point Point to get weather data for
   * \param start_date Start date for ensemble used
   * \param offset Offset from current day to get data for
   * \return FwiWeather for the day before the given offset
   */
  [[nodiscard]] static unique_ptr<FwiWeather> readYesterday(const topo::Point& point,
                                                            const TIMESTAMP_STRUCT&
                                                            start_date,
                                                            int offset);
  /**
   * \brief Read weather data for the day before the WxSHIELD ensemble.
   * \return FwiWeather for the day before the start of the ensemble
   */
  [[nodiscard]] unique_ptr<FwiWeather> readYesterday() const;
  /**
   * \brief Reads forecast weather for the given period
   * \param point Point to get weather data for
   * \param start_date Start date for ensemble used
   * \param offset Offset from current day to get data for
   * \param num_days Number of days to generate output for
   * \return Forecast Weather by date by WeatherModel
   */
  [[nodiscard]] static map<WeatherModel, map<int, vector<Weather>>, ModelCompare>
  readForecastByOffset(const topo::Point& point,
                       const TIMESTAMP_STRUCT& start_date,
                       int offset,
                       size_t num_days);
  /**
   * \brief Read reanalysis data for the given period
   * \param point Point to get weather data for
   * \param offset Offset from current day to get data for
   * \param num_days Number of days to generate output for
   * \return Forecast Weather by date by WeatherModel
   */
  [[nodiscard]] static map<WeatherModel, map<int, vector<Weather>>, ModelCompare>
  readHindcastByOffset(const topo::Point& point, int offset, size_t num_days);
  /**
   * \brief Get observed weather data for the given period
   * \param point Point to get weather data for
   * \param start_date Start date for ensemble used
   * \param offset Offset from current day to get data for
   * \param num_days Number of days to generate output for
   * \return vector of Weather covering the given period
   */
  [[nodiscard]] static vector<Weather> readActualsByOffset(const topo::Point& point,
                                                           const TIMESTAMP_STRUCT&
                                                           start_date,
                                                           int offset,
                                                           size_t num_days);
  /**
   * \brief Read startup values for the given date
   * \param point Point to get weather data for
   * \param start_date Start date for ensemble used
   * \param offset Offset from current day to get data for
   * \return Startup values for given date
   */
  [[nodiscard]] static unique_ptr<Startup> readStartupByOffset(const topo::Point& point,
                                                               const TIMESTAMP_STRUCT&
                                                               start_date,
                                                               int offset);
private:
  /**
   * \brief Initialize a WeatherSHIELD ensemble.
   * \param start_date Start date for ensemble
   * \param point Point to retrieve weather data for
   * \param num_days Number of days to generate ensemble for
   * \param save_to File to save generated weather to
   * \param offset Offset from today to start from (days)
   * \param ffmc Fine Fuel Moisture Code to override Startup value with
   * \param dmc Duff Moisture Code to override Startup value with
   * \param dc Drought Code to override Startup value with
   * \param apcp_0800 Accumulated Precipitation at 0800 to override Startup value with
   * \param full_wx Whether or not to include all reanalysis weather years in output
   */
  WxShield(const TIMESTAMP_STRUCT& start_date,
           const topo::Point& point,
           size_t num_days,
           const string& save_to,
           int offset,
           Ffmc* ffmc,
           Dmc* dmc,
           Dc* dc,
           AccumulatedPrecipitation* apcp_0800,
           bool full_wx);
  /**
	 * \brief Initialize a WeatherSHIELD ensemble.
	 * \param start_date Start date for ensemble
	 * \param point Point to retrieve weather data for
	 * \param num_days Number of days to generate ensemble for
	 * \param save_to File to save generated weather to
	 * \param offset Offset from today to start from (days)
	 * \param years List of years to use for streams
	 * \param ffmc Fine Fuel Moisture Code to override Startup value with
	 * \param dmc Duff Moisture Code to override Startup value with
	 * \param dc Drought Code to override Startup value with
	 * \param apcp_0800 Accumulated Precipitation at 0800 to override Startup value with
	 * \param full_wx Whether or not to include all reanalysis weather years in output
   */
  WxShield(const TIMESTAMP_STRUCT& start_date,
           const topo::Point& point,
           size_t num_days,
           string save_to,
           int offset,
           vector<int>&& years,
           Ffmc* ffmc,
           Dmc* dmc,
           Dc* dc,
           AccumulatedPrecipitation* apcp_0800,
           bool full_wx);
  /**
   * \brief Open database connection for DFOSS database that contains data for given date
   * \param start_date Date to open database for
   * \return Connection for DFOSS database that contains data for given date
   */
  [[nodiscard]] static util::Database getDfossDb(const TIMESTAMP_STRUCT& start_date);
  /**
   * \brief Open database connection for weather database that contains data for given date
   * \param start_date Date to open database for
   * \return Connection for weather database that contains data for given date
   */
  [[nodiscard]] static util::Database getWxDb(const TIMESTAMP_STRUCT& start_date);
  /**
   * \brief Map of WeatherModel to the Weather in it by date
   */
  using ModelMap = map<WeatherModel, map<int, vector<Weather>>, ModelCompare>;
  /**
   * \brief Generate weather streams based on input data
   * \param actuals Actual weather observations for period, if available
   * \param hindcasts Hindcasts to select historic years from
   * \param forecasts Forecasts to splice hindcast data onto the end of
   * \param years Years to use from hindcast data
   * \param end_of_ensemble How many days the ensemble portion of the forecast is
   */
  void processEnsembles(const vector<Weather>& actuals,
                        ModelMap& hindcasts,
                        ModelMap& forecasts,
                        vector<int>& years,
                        size_t end_of_ensemble);
  /**
   * \brief Remove unused years from hindcast data and ensure required years are present
   * \param hindcasts Hindcasts to select historic years from
   * \param years Years to use from hindcast data
   */
  void preProcessEnsembles(ModelMap& hindcasts, vector<int>& years) const;
  /**
   * \brief Process a member of the WeatherModel
   * \param startup Startup values to use
   * \param latitude Latitude to use for calculations
   * \param cur_member vector of Weather to use for calculations
   * \return FwiStream created from Startup and given Weather
   */
  [[nodiscard]] FwiStream processMember(Startup* startup,
                                        double latitude,
                                        vector<Weather> cur_member) const;
  /**
   * \brief Dates that correspond to the Weather in the streams
   */
  vector<TIMESTAMP_STRUCT> dates_;
  /**
   * \brief Point to retrieve weather data for
   */
  topo::Point point_;
  /**
   * \brief Start date for ensemble
   */
  TIMESTAMP_STRUCT start_date_;
  /**
   * \brief File to save generated weather to
   */
  string save_to_;
  /**
   * \brief Startup values to use for streams
   */
  unique_ptr<Startup> startup_;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Offset from today to start from (days)
   */
  int offset_;
  /**
   * \brief Whether or not to include all reanalysis weather years in output
   */
  bool full_wx_;
};
#pragma warning (pop)
ostream& operator<<(ostream& os, const FwiWeather& w);
ostream& operator<<(ostream& os,
                    const tuple<wstring, FwiStream, vector<TIMESTAMP_STRUCT>>& member);
}
}
