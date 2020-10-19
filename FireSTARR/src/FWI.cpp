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
#include "FWI.h"
#include "Database.h"
#include "Log.h"
#include "Weather.h"
#define CHECK_CALCULATION 1
#undef CHECK_CALCULATION
// adapted from http://www.columbia.edu/~rf2426/index_files/FWI.vba
//******************************************************************************************
//
// Description: VBA module containing functions to calculate the components of
//              the Canadian Fire Weather Index system, as described in
//
//      Van Wagner, C.E. 1987. Development and structure of the Canadian Forest Fire
//      Weather Index System. Canadian Forest Service, Ottawa, Ont. For. Tech. Rep. 35.
//      37 p.
//
//      Equation numbers from VW87 are listed throughout, to the right of the equations in
//      in the code.
//
//      A more recent technical description can be found in:
//      http://www.cawcr.gov.au/publications/technicalreports/CTR_010.pdf
//
//      This module is essentially a direct C to VBA translation of Kerry Anderson's
//      fwi84.c code. The latitude adjustments were developed by Marty Alexander, and used
//      over Indonesia in the paper:
//
//      Field, R.D., Y. Wang, O. Roswintiarti, and Guswanto. A drought-based predictor of
//      recent haze events in western Indonesia. Atmospheric Environment, 38, 1869-1878,
//      2004.
//
//      A technical description of the latitude adjustments can be found in Appendix 3 of:
//      http://cfs.nrcan.gc.ca/pubwarehouse/pdfs/29152.pdf
//
//      Robert Field, robert.field@utoronto.ca
//******************************************************************************************
namespace firestarr
{
namespace wx
{
const Ffmc Ffmc::Zero = Ffmc(0);
const Dmc Dmc::Zero = Dmc(0);
const Dc Dc::Zero = Dc(0);
const Bui Bui::Zero = Bui(0);
const Isi Isi::Zero = Isi(0);
const Fwi Fwi::Zero = Fwi(0);
// HACK: can't use the ::Zero fields for these because we don't know when they initialize
const FwiWeather FwiWeather::Zero{
  Temperature(0),
  RelativeHumidity(0),
  Wind(Direction(0, false), Speed(0)),
  AccumulatedPrecipitation(0),
  Ffmc(0),
  Dmc(0),
  Dc(0),
  Isi(Speed(0), Ffmc(0)),
  Bui(Dmc(0), Dc(0)),
  Fwi(Isi(Speed(0), Ffmc(0)), Bui(Dmc(0), Dc(0)))
};
// The following two functions refer to the MEA daylength adjustment 'note'.
//
//******************************************************************************************
// Function Name: DayLengthFactor
// Description: Calculates latitude/date dependent day length factor for Drought Code
// Parameters:
//      Latitude is latitude in decimal degrees of calculation location
//      Month is integer (1..12) value of month of year for calculation
//
//******************************************************************************************
static double day_length_factor(const double latitude, const int month) noexcept
{
  static constexpr double LfN[] = {
    -1.6,
    -1.6,
    -1.6,
    0.9,
    3.8,
    5.8,
    6.4,
    5.0,
    2.4,
    0.4,
    -1.6,
    -1.6
  };
  static constexpr double LfS[] = {
    6.4,
    5.0,
    2.4,
    0.4,
    -1.6,
    -1.6,
    -1.6,
    -1.6,
    -1.6,
    0.9,
    3.8,
    5.8
  };
  //'    '/* Use Northern hemisphere numbers */
  //'   '/* something goes wrong with >= */
  if (latitude > 15.0)
  {
    return LfN[month];
  }
  //'    '/* Use Equatorial numbers */
  if ((latitude <= 15.0) && (latitude > -15.0))
  {
    return 1.39;
  }
  //'    '/* Use Southern hemisphere numbers */
  if (latitude <= -15.0)
  {
    return LfS[month];
  }
  return logging::fatal<double>("Unable to calculate DayLengthFactor");
}
using MonthArray = array<double, 12>;
static constexpr MonthArray DAY_LENGTH46_N{
  6.5,
  7.5,
  9.0,
  12.8,
  13.9,
  13.9,
  12.4,
  10.9,
  9.4,
  8.0,
  7.0,
  6.0
};
static constexpr MonthArray DAY_LENGTH20_N{
  7.9,
  8.4,
  8.9,
  9.5,
  9.9,
  10.2,
  10.1,
  9.7,
  9.1,
  8.6,
  8.1,
  7.8
};
static constexpr MonthArray DAY_LENGTH20_S{
  10.1,
  9.6,
  9.1,
  8.5,
  8.1,
  7.8,
  7.9,
  8.3,
  8.9,
  9.4,
  9.9,
  10.2
};
static constexpr MonthArray DAY_LENGTH40_S{
  11.5,
  10.5,
  9.2,
  7.9,
  6.8,
  6.2,
  6.5,
  7.4,
  8.7,
  10.0,
  11.2,
  11.8
};
//******************************************************************************************
// Function Name: DayLength
// Description: Calculates latitude/date dependent day length for DMC calculation
// Parameters:
//      Latitude is latitude in decimal degrees of calculation location
//      Month is integer (1..12) value of month of year for calculation
//
//******************************************************************************************
static constexpr double day_length(const double latitude, const int month) noexcept
{
  //'''/* Day Length Arrays for four different latitude ranges '*/
  //''/*
  //'    Use four ranges which respectively span:
  //'        - 90N to 33 N
  //'        - 33 N to 0
  //'        - 0 to -30
  //'        - -30 to -90
  ///
  if ((latitude <= 90) && (latitude > 33.0))
  {
    return DAY_LENGTH46_N.at(static_cast<size_t>(month) - 1);
  }
  if ((latitude <= 33.0) && (latitude > 15.0))
  {
    return DAY_LENGTH20_N.at(static_cast<size_t>(month) - 1);
  }
  if ((latitude <= 15.0) && (latitude > -15.0))
  {
    return 9.0;
  }
  if ((latitude <= -15.0) && (latitude > -30.0))
  {
    return DAY_LENGTH20_S.at(static_cast<size_t>(month) - 1);
  }
  if ((latitude <= -30.0) && (latitude >= -90.0))
  {
    return DAY_LENGTH40_S.at(static_cast<size_t>(month) - 1);
  }
  return logging::fatal<double>("Unable to calculate DayLength");
}
//******************************************************************************************
// Function Name: FFMC
// Description: Calculates today's Fine Fuel Moisture Code
// Parameters:
//    temperature is the 12:00 LST temperature in degrees celsius
//    rh is the 12:00 LST relative humidity in %
//    wind is the 12:00 LST wind speed in kph
//    rain is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
//    ffmc_previous is the previous day's FFMC
//******************************************************************************************
static double calculate_ffmc(const Temperature& temperature,
                             const RelativeHumidity& rh,
                             const Speed& wind,
                             const AccumulatedPrecipitation& rain,
                             const Ffmc& ffmc_previous) noexcept
{
  //'''/* 1  '*/
  auto mo = 147.2 * (101.0 - ffmc_previous.asDouble()) /
    (59.5 + ffmc_previous.asDouble());
  if (rain.asDouble() > 0.5)
  {
    //'''/* 2  '*/
    const auto rf = rain.asDouble() - 0.5;
    //'''/* 3a '*/
    auto mr = mo + 42.5 * rf * (exp(-100.0 / (251.0 - mo))) * (1 - exp(-6.93 / rf));
    if (mo > 150.0)
    {
      //'''/* 3b '*/
      mr += 0.0015 * util::pow_int<2>(mo - 150.0) * sqrt(rf);
    }
    if (mr > 250.0)
    {
      mr = 250.0;
    }
    mo = mr;
  }
  //'''/* 4  '*/
  const auto find_m = [&temperature, &rh, &wind, &mo]() noexcept
  {
    const auto ed = 0.942 * pow(rh.asDouble(), 0.679) + 11.0 * exp(
        (rh.asDouble() - 100.0) / 10.0) + 0.18 *
      (21.1 - temperature.asDouble()) * (1.0 - exp(-0.115 * rh.asDouble()));
    if (mo > ed)
    {
      //'''/* 6a '*/
      const auto ko = 0.424 * (1.0 - pow(rh.asDouble() / 100.0, 1.7)) +
        0.0694 * sqrt(wind.asDouble()) * (1.0 - util::pow_int<8>(rh.asDouble() / 100.0));
      //'''/* 6b '*/
      const auto kd = ko * 0.581 * exp(0.0365 * temperature.asDouble());
      //'''/* 8  '*/
      return ed + (mo - ed) * pow(10.0, -kd);
    }
    //'''/* 5  '*/
    const auto ew = 0.618 * pow(rh.asDouble(), 0.753) + 10.0 * exp(
        (rh.asDouble() - 100.0) / 10.0) +
      0.18 * (21.1 - temperature.asDouble()) * (1.0 - exp(-0.115 * rh.asDouble()));
    if (mo < ew)
    {
      //'''/* 7a '*/
      const auto kl = 0.424 * (1.0 - pow((100.0 - rh.asDouble()) / 100.0, 1.7)) + 0.0694 *
        sqrt(wind.asDouble()) * (1 - util::pow_int<8>((100.0 - rh.asDouble()) / 100.0));
      //'''/* 7b '*/
      const auto kw = kl * 0.581 * exp(0.0365 * temperature.asDouble());
      //'''/* 9  '*/
      return ew - (ew - mo) * pow(10.0, -kw);
    }
    return mo;
  };
  const auto m = find_m();
  //'''/* 10 '*/
  return (59.5 * (250.0 - m) / (147.2 + m));
}
Ffmc::Ffmc(const Temperature& temperature,
           const RelativeHumidity& rh,
           const Speed& wind,
           const AccumulatedPrecipitation& rain,
           const Ffmc& ffmc_previous) noexcept
  : Ffmc(calculate_ffmc(temperature, rh, wind, rain, ffmc_previous))
{
}
//******************************************************************************************
// Function Name: DMC
// Description: Calculates today's Duff Moisture Code
// Parameters:
//    temperature is the 12:00 LST temperature in degrees celsius
//    rh is the 12:00 LST relative humidity in %
//    rain is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
//    dmc_previous is the previous day's DMC
//    latitude is the latitude in decimal degrees of the location for calculation
//    month is the month of Year (1..12) for the current day's calculations.
//******************************************************************************************
static double calculate_dmc(const Temperature& temperature,
                            const RelativeHumidity& rh,
                            const AccumulatedPrecipitation& rain,
                            const Dmc& dmc_previous,
                            const int month,
                            const double latitude) noexcept
{
  auto previous = dmc_previous.asDouble();
  if (rain.asDouble() > 1.5)
  {
    //'''/* 11  '*/
    const auto re = 0.92 * rain.asDouble() - 1.27;
    //'''/* 12  '*/
    const auto mo = 20.0 + exp(5.6348 - previous / 43.43);
    const auto b = (previous <= 33.0)
                     ?  //'''/* 13a '*/
                     100.0 / (0.5 + 0.3 * previous)
                     : ((previous <= 65.0)
                          ?  //'''/* 13b '*/
                          14.0 - 1.3 * (log(previous))
                          :  //'''/* 13c '*/
                          6.2 * log(previous) - 17.2);
    //'''/* 14  '*/
    const auto mr = mo + 1000.0 * re / (48.77 + b * re);
    //'''/* 15  '*/
    const auto pr = 244.72 - 43.43 * log(mr - 20.0);
    previous = max(pr, 0.0);
  }
  const auto k = (temperature.asDouble() > -1.1)
                   ? 1.894 * (temperature.asDouble() + 1.1) * (100.0 - rh.asDouble()) *
                   day_length(latitude, month) * 0.000001
                   : 0.0;
  //'''/* 17  '*/
  return (previous + 100.0 * k);
}
Dmc::Dmc(const Temperature& temperature,
         const RelativeHumidity& rh,
         const AccumulatedPrecipitation& rain,
         const Dmc& dmc_previous,
         const int month,
         const double latitude) noexcept
  : Dmc(calculate_dmc(temperature, rh, rain, dmc_previous, month, latitude))
{
}
//******************************************************************************************
// Function Name: DC
// Description: Calculates today's Drought Code
// Parameters:
//    temperature is the 12:00 LST temperature in degrees celsius
//    rain is the 24-hour accumulated rainfall in mm, calculated at 12:00 LST
//    dc_previous is the previous day's DC
//    latitude is the latitude in decimal degrees of the location for calculation
//    month is the month of Year (1..12) for the current day's calculations.
//******************************************************************************************
static double calculate_dc(const Temperature& temperature,
                           const AccumulatedPrecipitation& rain,
                           const Dc& dc_previous,
                           const int month,
                           const double latitude) noexcept
{
  auto previous = dc_previous.asDouble();
  if (rain.asDouble() > 2.8)
  {
    //'/* 18  */
    const auto rd = 0.83 * (rain.asDouble()) - 1.27;
    //'/* 19  */
    const auto qo = 800.0 * exp(-previous / 400.0);
    //'/* 20  */
    const auto qr = qo + 3.937 * rd;
    //'/* 21  */
    const auto dr = 400.0 * log(800.0 / qr);
    previous = (dr > 0.0) ? dr : 0.0;
  }
  const auto lf = day_length_factor(latitude, month - 1);
  //'/* 22  */
  const auto v = max(0.0,
                     (temperature.asDouble() > -2.8)
                       ? 0.36 * (temperature.asDouble() + 2.8) + lf
                       : lf);
  //'/* 23  */
  const auto d = previous + 0.5 * v;
  // HACK: don't allow negative values
  return max(0.0, d);
}
Dc::Dc(const Temperature& temperature,
       const AccumulatedPrecipitation& rain,
       const Dc& dc_previous,
       const int month,
       const double latitude) noexcept
  : Dc(calculate_dc(temperature, rain, dc_previous, month, latitude))
{
}
//******************************************************************************************
// Function Name: ISI
// Description: Calculates today's Initial Spread Index
// Parameters:
//    wind is the 12:00 LST wind speed in kph
//    ffmc is the current day's FFMC
//******************************************************************************************
static double calculate_isi(const Speed& wind, const Ffmc& ffmc) noexcept
{
  //'''/* 24  '*/
  const auto f_wind = exp(0.05039 * wind.asDouble());
  //'''/* 1   '*/
  const auto m = 147.2 * (101 - ffmc.asDouble()) / (59.5 + ffmc.asDouble());
  //'''/* 25  '*/
  const auto f_f = 91.9 * exp(-0.1386 * m) * (1.0 + pow(m, 5.31) / 49300000.0);
  //'''/* 26  '*/
  return (0.208 * f_wind * f_f);
}
Isi::Isi(const Speed& wind, const Ffmc& ffmc) noexcept
  : Isi(calculate_isi(wind, ffmc))
{
}
Isi::Isi(double
#ifdef CHECK_CALCULATION
			value
#endif
         ,
         const Speed& wind,
         const Ffmc& ffmc) noexcept
  : Isi(wind, ffmc)
{
#ifdef CHECK_CALCULATION
			// check that we're not more than 10% off of the value
			logging::check_fatal(abs((*this - Isi(value)).asDouble()) >= abs(value / 10),
				"ISI is incorrect %f, %f => %f not %f",
				wind.asDouble(), ffmc.asDouble(), asDouble(), Isi(value).asDouble());
#endif
}
//******************************************************************************************
// Function Name: BUI
// Description: Calculates today's Buildup Index
// Parameters:
//    DMC is the current day's Duff Moisture Code
//    DC is the current day's Drought Code
//******************************************************************************************
static double calculate_bui(const Dmc& dmc, const Dc& dc) noexcept
{
  if (dmc.asDouble() <= 0.4 * dc.asDouble())
  {
    // HACK: this isn't normally part of it but it's division by 0 without this
    if (0 == dc.asDouble())
    {
      return 0;
    }
    //'''/* 27a '*/
    return max(0.0,
               0.8 * dmc.asDouble() * dc.asDouble() /
               (dmc.asDouble() + 0.4 * dc.asDouble()));
  }
  //'''/* 27b '*/
  return max(0.0,
             dmc.asDouble() - (1.0 - 0.8 * dc.asDouble()
               / (dmc.asDouble() + 0.4 * dc.asDouble()))
             * (0.92 + pow(0.0114 * dmc.asDouble(), 1.7)));
}
Bui::Bui(double
#ifdef CHECK_CALCULATION
			value
#endif
         ,
         const Dmc& dmc,
         const Dc& dc) noexcept
  : Bui(dmc, dc)
{
#ifdef CHECK_CALCULATION
			// check that we're not more than 10% off of the value
			logging::check_fatal(abs((*this - Bui(value)).asDouble()) >= abs(value / 10),
				"BUI is incorrect %f, %f => %f not %f",
				dmc.asDouble(), dc.asDouble(), asDouble(), Bui(value).asDouble());
#endif
}
Bui::Bui(const Dmc& dmc, const Dc& dc) noexcept
  : Bui(calculate_bui(dmc, dc))
{
}
//******************************************************************************************
// Function Name: FWI
// Description: Calculates today's Fire Weather Index
// Parameters:
//    ISI is current day's ISI
//    BUI is the current day's BUI
//******************************************************************************************
static double calculate_fwi(const Isi& isi, const Bui& bui) noexcept
{
  const auto f_d = (bui.asDouble() <= 80.0)
                     ?  //'''/* 28a '*/
                     0.626 * pow(bui.asDouble(), 0.809) + 2.0
                     :  //'''/* 28b '*/
                     1000.0 / (25.0 + 108.64 * exp(-0.023 * bui.asDouble()));
  //'''/* 29  '*/
  const auto b = 0.1 * isi.asDouble() * f_d;
  if (b > 1.0)
  {
    //'''/* 30a '*/
    return exp(2.72 * pow(0.434 * log(b), 0.647));
  }
  //'''/* 30b '*/
  return b;
}
Fwi::Fwi(double
#ifdef CHECK_CALCULATION
			value
#endif
         ,
         const Isi& isi,
         const Bui& bui) noexcept
  : Fwi(isi, bui)
{
#ifdef CHECK_CALCULATION
			// check that we're not more than 10% off of the value
			logging::check_fatal(abs((*this - Fwi(value)).asDouble()) >= abs(value / 10),
				"FWI is incorrect %f, %f => %f not %f",
				isi.asDouble(), bui.asDouble(), asDouble(), Fwi(value).asDouble());
#endif
}
Fwi::Fwi(const Isi& isi, const Bui& bui) noexcept
  : Fwi(calculate_fwi(isi, bui))
{
}
//******************************************************************************************
// Function Name: DSR
// Description: Calculates today's Daily Severity Rating
// Parameters:
//    FWI is current day's FWI
//******************************************************************************************
static double calculate_dsr(const Fwi& fwi) noexcept
{
  //'''/* 41 '*/
  return (0.0272 * pow(fwi.asDouble(), 1.77));
}
Dsr::Dsr(const Fwi& fwi) noexcept
  : Dsr(calculate_dsr(fwi))
{
}
inline double stod(const string* const str)
{
  return stod(*str);
}
FwiWeather read(istringstream* iss, string* str)
{
  // APCP
  util::getline(iss, str, ',');
  logging::extensive("APCP is %s", str->c_str());
  const AccumulatedPrecipitation apcp(stod(str));
  // TMP
  util::getline(iss, str, ',');
  logging::extensive("TMP is %s", str->c_str());
  const Temperature tmp(stod(str));
  // RH
  util::getline(iss, str, ',');
  logging::extensive("RH is %s", str->c_str());
  const RelativeHumidity rh(stod(str));
  // WS
  util::getline(iss, str, ',');
  logging::extensive("WS is %s", str->c_str());
  const Speed ws(stod(str));
  // WD
  util::getline(iss, str, ',');
  logging::extensive("WD is %s", str->c_str());
  const Direction wd(stod(str), false);
  // FFMC
  util::getline(iss, str, ',');
  logging::extensive("FFMC is %s", str->c_str());
  const Ffmc ffmc(stod(str));
  // DMC
  util::getline(iss, str, ',');
  logging::extensive("DMC is %s", str->c_str());
  const Dmc dmc(stod(str));
  // DC
  util::getline(iss, str, ',');
  logging::extensive("DC is %s", str->c_str());
  const Dc dc(stod(str));
  // ISI
  util::getline(iss, str, ',');
  logging::extensive("ISI is %s", str->c_str());
  const Isi isi(stod(str), ws, ffmc);
  // BUI
  util::getline(iss, str, ',');
  logging::extensive("BUI is %s", str->c_str());
  const Bui bui(stod(str), dmc, dc);
  // FWI
  util::getline(iss, str, ',');
  logging::extensive("FWI is %s", str->c_str());
  const Fwi fwi(stod(str), isi, bui);
  const Wind wind(wd, ws);
  return {tmp, rh, wind, apcp, ffmc, dmc, dc, isi, bui, fwi};
}
#pragma warning(suppress: 26495)
FwiWeather::FwiWeather(istringstream* iss, string* str)
  : FwiWeather(read(iss, str))
{
}
double ffmc_effect(const Ffmc& ffmc) noexcept
{
  const auto v = ffmc.asDouble();
  const auto mc = 147.2 * (101.0 - v) / (59.5 + v);
  return 91.9 * exp(-0.1386 * mc) * (1 + pow(mc, 5.31) / 49300000.0);
}
FwiWeather::FwiWeather(const Temperature& tmp,
                       const RelativeHumidity& rh,
                       const Wind& wind,
                       const AccumulatedPrecipitation& apcp,
                       const Ffmc& ffmc,
                       const Dmc& dmc,
                       const Dc& dc,
                       const Isi& isi,
                       const Bui& bui,
                       const Fwi& fwi) noexcept
  : Weather(tmp, rh, wind, apcp),
    ffmc_(ffmc),
    dmc_(dmc),
    dc_(dc),
    // HACK: recalculate so we can check that things are within tolerances
    isi_(Isi(isi.asDouble(), wind.speed(), ffmc)),
    bui_(Bui(bui.asDouble(), dmc, dc)),
    fwi_(Fwi(fwi.asDouble(), isi, bui)),
    mc_ffmc_pct_(147.2 * (101 - ffmc.asDouble()) / (59.5 + ffmc.asDouble())),
    mc_dmc_pct_(exp((dmc.asDouble() - 244.72) / -43.43) + 20),
    ffmc_effect_(ffmc_effect(ffmc))
{
}
FwiWeather::FwiWeather(const FwiWeather& wx,
                       const Wind& wind,
                       const Ffmc& ffmc,
                       const Isi& isi) noexcept
  : FwiWeather(wx.tmp(),
               wx.rh(),
               wind,
               wx.apcp(),
               ffmc,
               wx.dmc(),
               wx.dc(),
               isi,
               wx.bui(),
               Fwi(isi, wx.bui()))
{
}
FwiWeather::FwiWeather(const FwiWeather& wx, const Wind& wind, const Ffmc& ffmc) noexcept
  : FwiWeather(wx, wind, ffmc, Isi(wind.speed(), ffmc))
{
}
FwiWeather::FwiWeather(const FwiWeather& wx, const Speed& ws, const Ffmc& ffmc) noexcept
  : FwiWeather(wx, Wind(wx.wind().direction(), ws), ffmc)
{
}
FwiWeather read_fwi_weather(util::Database* db) noexcept
{
  const Weather wx(db);
  // HACK: do it this way so that we know database calls are in this order
  const Ffmc ffmc(db->getDouble<2>());
  const Dmc dmc(db->getDouble<2>());
  const Dc dc(db->getDouble<2>());
  const Isi isi(db->getDouble<2>(), wx.wind().speed(), ffmc);
  const Bui bui(db->getDouble<2>(), dmc, dc);
  const Fwi fwi(db->getDouble<2>(), isi, bui);
  return {wx.tmp(), wx.rh(), wx.wind(), wx.apcp(), ffmc, dmc, dc, isi, bui, fwi};
}
FwiWeather::FwiWeather() noexcept
  : FwiWeather(Zero)
{
}
#pragma warning(suppress: 26495)
FwiWeather::FwiWeather(util::Database* db) noexcept
  : FwiWeather(read_fwi_weather(db))
{
}
}
}
