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
#include "Database.h"
#include "Index.h"
#include "Util.h"
namespace firestarr
{
using data::Index;
namespace wx
{
/**
 * \brief Temperature in degrees Celsius.
 */
class Temperature : public Index<Temperature>
{
public:
  //! @cond Doxygen_Suppress
  using Index::Index;
  //! @endcond
  /**
   * \brief 0 degrees Celcius
   */
  static const Temperature Zero;
};
/**
 * \brief Relative humidity as a percentage.
 */
class RelativeHumidity : public Index<RelativeHumidity>
{
public:
  //! @cond Doxygen_Suppress
  using Index::Index;
  //! @endcond
  /**
   * \brief 0% Relative Humidity
   */
  static const RelativeHumidity Zero;
};
/**
 * \brief Speed in kilometers per hour.
 */
class Speed : public Index<Speed>
{
public:
  //! @cond Doxygen_Suppress
  using Index::Index;
  //! @endcond
  /**
   * \brief 0 km/h
   */
  static const Speed Zero;
};
/**
 * \brief Direction with access to degrees or radians.
 */
class Direction : public Index<Direction>
{
public:
  /**
   * \brief Destructor
   */
  ~Direction() = default;
  /**
   * \brief Construct with Direction of 0 (North)
   */
  constexpr Direction() noexcept = default;
  /**
   * \brief Constructor
   * \param value Direction to use
   * \param is_radians Whether the given direction is in radians (as opposed to degrees)
   */
  constexpr Direction(const double value, const bool is_radians)
    : Index(is_radians ? util::to_degrees(value) : value)
  {
  }
  /**
   * \brief Copy constructor
   * \param rhs Direction to copy from
   */
  constexpr Direction(const Direction& rhs) noexcept = default;
  /**
   * \brief Move constructor
   * \param rhs Direction to move from
   */
  constexpr Direction(Direction&& rhs) noexcept = default;
  /**
   * \brief Copy assignment
   * \param rhs Direction to copy from
   * \return This, after assignment
   */
  Direction& operator=(const Direction& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs Direction to move from
   * \return This, after assignment
   */
  Direction& operator=(Direction&& rhs) noexcept = default;
  /**
   * \brief Direction as radians, where 0 is North and values increase clockwise
   * \return Direction as radians, where 0 is North and values increase clockwise
   */
  [[nodiscard]] constexpr double asRadians() const
  {
    return util::to_radians(asDegrees());
  }
  /**
   * \brief Direction as degrees, where 0 is North and values increase clockwise
   * \return Direction as degrees, where 0 is North and values increase clockwise
   */
  [[nodiscard]] constexpr double asDegrees() const { return asDouble(); }
  /**
   * \brief Heading (opposite of this direction)
   * \return Heading (opposite of this direction)
   */
  [[nodiscard]] constexpr double heading() const { return util::to_heading(asRadians()); }
  /**
   * \brief Direction of 0 (North)
   */
  static const Direction Zero;
};
/**
 * \brief Wind with a Speed and Direction.
 */
class Wind
{
public:
  /**
   * \brief Destructor
   */
  ~Wind() = default;
  /**
   * \brief Construct with 0 values
   */
  constexpr Wind() noexcept
    : wsv_x_(0),
      wsv_y_(0),
      direction_(0.0, false),
      speed_(0)
  {
  }
  /**
   * \brief Constructor
   * \param direction Direction wind is coming from
   * \param speed Speed of wind
   */
  Wind(const Direction& direction, const Speed speed) noexcept
    : wsv_x_(speed.asDouble() * sin(direction.heading())),
      wsv_y_(speed.asDouble() * cos(direction.heading())),
      direction_(direction),
      speed_(speed)
  {
  }
  /**
   * \brief Copy constructor
   * \param rhs Wind to copy from
   */
  constexpr Wind(const Wind& rhs) noexcept = default;
  /**
   * \brief Move constructor
   * \param rhs Wind to move from
   */
  constexpr Wind(Wind&& rhs) noexcept = default;
  /**
   * \brief Copy assignment
   * \param rhs Wind to copy into this one
   * \return This, after assignment
   */
  Wind& operator=(const Wind& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs Wind to move into this one
   * \return This, after assignment
   */
  Wind& operator=(Wind&& rhs) noexcept = default;
  /**
   * \brief Speed of wind (km/h)
   * \return Speed of wind (km/h)
   */
  [[nodiscard]] constexpr const Speed& speed() const noexcept { return speed_; }
  /**
   * \brief Direction wind is coming from.
   * \return Direction wind is coming from.
   */
  [[nodiscard]] constexpr const Direction& direction() const noexcept
  {
    return direction_;
  }
  /**
   * \brief Direction wind is going towards
   * \return Direction wind is going towards
   */
  [[nodiscard]] constexpr double heading() const noexcept { return direction_.heading(); }
  /**
   * \brief X component of wind vector (km/h)
   * \return X component of wind vector (km/h)
   */
  [[nodiscard]] constexpr double wsvX() const noexcept { return wsv_x_; }
  /**
   * \brief Y component of wind vector (km/h)
   * \return Y component of wind vector (km/h)
   */
  [[nodiscard]] constexpr double wsvY() const noexcept { return wsv_y_; }
  /**
   * \brief Not equal to operator
   * \param rhs Wind to compare to
   * \return Whether or not these are not equivalent
   */
  [[nodiscard]] constexpr bool operator!=(const Wind& rhs) const noexcept
  {
    return direction_ != rhs.direction_ || speed_ != rhs.speed_;
  }
  /**
   * \brief Equals to operator
   * \param rhs Wind to compare to
   * \return Whether or not these are equivalent
   */
  [[nodiscard]] constexpr bool operator==(const Wind& rhs) const noexcept
  {
    return direction_ == rhs.direction_ && speed_ == rhs.speed_;
  }
  /**
   * \brief Less than operator
   * \param rhs Wind to compare to
   * \return Whether or not this is less than the compared to Wind
   */
  [[nodiscard]] constexpr bool operator<(const Wind& rhs) const noexcept
  {
    if (direction_ == rhs.direction_)
    {
      return speed_ < rhs.speed_;
    }
    return direction_ < rhs.direction_;
  }
  /**
   * \brief Wind with 0 Speed from Direction 0
   */
  static const Wind Zero;
private:
  /**
   * \brief Wind speed vector in X direction (East is positive)
   */
  double wsv_x_;
  /**
   * \brief Wind speed vector in Y direction (North is positive)
   */
  double wsv_y_;
  /**
   * \brief Direction (degrees or radians, N is 0)
   */
  Direction direction_;
  /**
   * \brief Speed (km/h)
   */
  Speed speed_;
};
/**
 * \brief Accumulated precipitation in mm.
 */
class AccumulatedPrecipitation : public Index<AccumulatedPrecipitation>
{
public:
  //! @cond Doxygen_Suppress
  using Index::Index;
  //! @endcond
  /**
   * \brief Accumulated Precipitation of 0 mm
   */
  static const AccumulatedPrecipitation Zero;
};
/**
 * \brief Collection of weather indices used for calculating FwiWeather.
 */
class Weather
{
public:
  /**
   * \brief Destructor
   */
  virtual ~Weather() = default;
  /**
   * \brief Constructor with no initialization
   */
  constexpr Weather() noexcept = default;
  /**
   * \brief Construct by reading from Database
   * \param db Database to read from
   */
  explicit Weather(util::Database* db) noexcept;
  /**
   * \brief Construct with given indices
   * \param tmp Temperature (Celcius)
   * \param rh Relative Humidity (%)
   * \param wind Wind (km/h)
   * \param apcp Accumulated Precipitation (mm)
   */
  constexpr Weather(const Temperature& tmp,
                    const RelativeHumidity& rh,
                    const Wind& wind,
                    const AccumulatedPrecipitation& apcp) noexcept
    : tmp_(tmp), rh_(rh), wind_(wind), apcp_(apcp)
  {
  }
  /**
   * \brief Move constructor
   * \param rhs Weather to move from
   */
  constexpr Weather(Weather&& rhs) noexcept = default;
  /**
   * \brief Copy constructor
   * \param rhs Weather to copy from
   */
  constexpr Weather(const Weather& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs Weather to move into this one
   * \return This, after assignment
   */
  Weather& operator=(Weather&& rhs) noexcept = default;
  /**
   * \brief Move assignment
   * \param rhs Weather to copy into this one
   * \return This, after assignment
   */
  Weather& operator=(const Weather& rhs) = default;
  /**
   * \brief Temperature (Celcius)
   * \return Temperature (Celcius)
   */
  [[nodiscard]] constexpr const Temperature& tmp() const noexcept { return tmp_; }
  /**
   * \brief Relative Humidity (%)
   * \return Relative Humidity (%)
   */
  [[nodiscard]] constexpr const RelativeHumidity& rh() const noexcept { return rh_; }
  /**
   * \brief Wind (km/h)
   * \return Wind (km/h)
   */
  [[nodiscard]] constexpr const Wind& wind() const noexcept { return wind_; }
  /**
   * \brief Accumulated Precipitation (mm)
   * \return Accumulated Precipitation (mm)
   */
  [[nodiscard]] constexpr const AccumulatedPrecipitation& apcp() const noexcept
  {
    return apcp_;
  }
private:
  /**
   * \brief Temperature (Celcius)
   */
  Temperature tmp_;
  /**
   * \brief Relative Humidity (%)
   */
  RelativeHumidity rh_;
  /**
   * \brief Wind (km/h)
   */
  Wind wind_;
  /**
   * \brief Accumulated Precipitation (mm)
   */
  AccumulatedPrecipitation apcp_;
};
}
}
