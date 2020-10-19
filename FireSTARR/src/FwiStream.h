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
namespace wx
{
class FwiWeather;
class Weather;
class Startup;
using FwiVector = vector<FwiWeather>;
/**
 * \brief A stream of FwiWeather values used for a Scenario.
 */
class FwiStream
{
public:
  /**
   * \brief Construct from a series of FwiWeather
   * \param wx FwiVector to use for stream
   */
  explicit FwiStream(FwiVector&& wx) noexcept;
  /**
   * \brief Calculate based on weather and dates using startup/shutdown criteria
   * \param dates Dates that apply to Weather vector
   * \param startup Startup values to use
   * \param latitude Latitude to use for calculations
   * \param cur_member vector of Weather to use for calculations
   */
  FwiStream(const vector<TIMESTAMP_STRUCT>& dates,
            Startup* startup,
            double latitude,
            vector<Weather> cur_member);
  /**
   * \brief Weather stream as a vector of FwiWeather
   * \return Weather stream as a vector of FwiWeather
   */
  [[nodiscard]] const FwiVector& wx() const noexcept { return wx_; }
private:
  /**
   * \brief Weather stream as a vector of FwiWeather
   */
  FwiVector wx_;
};
}
}
