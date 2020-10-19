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
#include "FireSpread.h"
#include "FuelLookup.h"
#include "FuelType.h"
#include "Scenario.h"
#include "Settings.h"
namespace firestarr
{
namespace sim
{
SlopeTableArray make_slope_table() noexcept
{
  // HACK: slope can be infinite, but anything > max is the same as max
  SlopeTableArray result{};
  for (size_t i = 0; i <= MAX_SLOPE_FOR_FACTOR; ++i)
  {
    result.at(i) = exp(3.533 * pow(i / 100.0, 1.2));
  }
  static_assert(result.size() == MAX_SLOPE_FOR_DISTANCE + 1);
  for (size_t i = MAX_SLOPE_FOR_FACTOR + 1; i < result.size(); ++i)
  {
    result.at(i) = result.at(MAX_SLOPE_FOR_FACTOR);
  }
  return result;
}
const SlopeTableArray SpreadInfo::SlopeTable = make_slope_table();
int calculate_nd_for_point(const int elevation, const topo::Point& point) noexcept
{
  return static_cast<int>(truncl(
    elevation < 0
      ? 0.5 + 151.0 * point.latitude() /
      (23.4 * exp(-0.0360 * (150 - point.longitude())) + 46.0)
      : 0.5 + 142.1 * point.latitude() /
      (33.7 * exp(-0.0351 * (150 - point.longitude())) + 43.0)
      + 0.0172 * elevation));
}
static double calculate_standard_back_isi_wsv(const double v) noexcept
{
  return 0.208 * exp(-0.05039 * v);
}
static const util::LookupTable<&calculate_standard_back_isi_wsv> STANDARD_BACK_ISI_WSV{};
static double calculate_standard_wsv(const double v) noexcept
{
  return v < 40.0
           ? exp(0.05039 * v)
           : 12.0 * (1.0 - exp(-0.0818 * (v - 28)));
}
static const util::LookupTable<&calculate_standard_wsv> STANDARD_WSV{};
SpreadInfo::SpreadInfo(const Scenario& scenario,
                       const double time,
                       const topo::Cell& cell,
                       const int nd,
                       const wx::FwiWeather* weather)
  : cell_(cell),
    weather_(weather),
    time_(time),
    nd_(nd)
{
  max_intensity_ = -1;
  const auto ffmc_effect = ffmcEffect();
  // needs to be non-const so we can update if slopeEffect changes direction
  auto raz = wind().heading();
  const auto isz = 0.208 * ffmc_effect;
  const auto slope_azimuth = cell_.aspect();
  const auto fuel = fuel::check_fuel(cell);
  const auto has_no_slope = 0 == percentSlope();
  auto wsv = wind().speed().asDouble();
  if (!has_no_slope)
  {
    const auto isf1 = fuel->calculateIsf(*this, isz);
    // const auto isf = (0.0 == isf1) ? isz : isf1;
    // we know const auto isz = 0.208 * ffmc_effect;
    auto wse = 0.0 == isf1 ? 0 : log(isf1 / isz) / 0.05039;
    if (wse > 40)
    {
      wse = 28.0 - log(
        1.0 - min(0.999 * 2.496 * ffmc_effect, isf1) / (2.496 * ffmc_effect)) / 0.0818;
    }
    const auto heading = util::to_heading(
      util::to_radians(static_cast<double>(slope_azimuth)));
    // we know that at->raz is already set to be the wind heading
    const auto wsv_x = wind().wsvX() + wse * cos(heading);
    const auto wsv_y = wind().wsvY() + wse * sin(heading);
    wsv = sqrt(wsv_x * wsv_x + wsv_y * wsv_y);
    raz = acos(wsv_y / wsv);
    if (wsv_x < 0)
    {
      raz = util::RAD_360 - raz;
    }
  }
  const auto isi = isz * STANDARD_WSV(wsv);
  const auto bui_eff = fuel->buiEffect(bui().asDouble());
  head_ros_ = fuel->calculateRos(nd,
                                 *weather,
                                 isi) * bui_eff;
  const auto min_ros = Settings::minimumRos();
  if (min_ros > head_ros_)
  {
    head_ros_ = -1;
    return;
  }
  const auto sfc = fuel->surfaceFuelConsumption(*this);
  const auto critical_surface_intensity = fuel->criticalSurfaceIntensity(*this);
  const auto rso = fuel::FuelType::criticalRos(sfc, critical_surface_intensity);
  const auto is_crown = fuel::FuelType::isCrown(critical_surface_intensity,
                                                fuel::fire_intensity(sfc, head_ros_));
  const auto back_isi = ffmc_effect * STANDARD_BACK_ISI_WSV(wsv);
  auto back_ros = fuel->calculateRos(nd,
                                     *weather,
                                     back_isi) * bui_eff;
  if (is_crown)
  {
    head_ros_ = fuel->finalRos(*this,
                               isi,
                               fuel->crownFractionBurned(head_ros_, rso),
                               head_ros_);
    back_ros = fuel->finalRos(*this,
                              back_isi,
                              fuel->crownFractionBurned(back_ros, rso),
                              back_ros);
  }
  // do everything we can to avoid calling trig functions unnecessarily
  const auto b_semi = has_no_slope ? 0 : cos(atan(percentSlope() / 100.0));
  const auto slope_radians = util::to_radians(slope_azimuth);
  // do check once and make function just return 1.0 if no slope
  const auto no_correction = [](const double) noexcept { return 1.0; };
  const auto do_correction = [b_semi, slope_radians](const double theta) noexcept
  {
    // never gets called if isInvalid() so don't check
    // figure out how far the ground distance is in map distance horizontally
    const auto angle_unrotated = theta - slope_radians;
    const auto tan_u = tan(angle_unrotated);
    const auto y = b_semi / sqrt(b_semi * tan_u * (b_semi * tan_u) + 1.0);
    const auto x = y * tan_u;
    return sqrt(x * x + y * y);
  };
  const auto correction_factor = has_no_slope
                                   ? std::function<double(double)>(no_correction)
                                   : std::function<double(double)>(do_correction);
  const auto cell_size = scenario.cellSize();
  const auto add_offset = [this, cell_size, min_ros](const double direction,
                                                     const double ros)
  {
    if (ros < min_ros)
    {
      return false;
    }
    // spreading, so figure out offset from current point
    const auto ros_cell = ros / cell_size;
    offsets_.emplace_back(ros_cell * sin(direction), ros_cell * cos(direction));
    return true;
  };
  const auto threshold = scenario.spreadThresholdByRos(time_);
  // if not over spread threshold then don't spread
  // HACK: assume there is no fuel where a crown fire's sfc is < COMPARE_LIMIT but it's fc is >
  double ros{};
  // HACK: set ros in boolean if we get that far so we don't have to repeat the if body
  if (head_ros_ < threshold
    || sfc < COMPARE_LIMIT
    || !add_offset(raz, ros = (head_ros_ * correction_factor(raz))))
  {
    // mark as invalid
    head_ros_ = -1;
    return;
  }
  auto fc = sfc;
  // don't need to re-evaluate if crown with new head_ros_ because it would only go up if is_crown
  if (fuel->canCrown() && is_crown)
  {
    // wouldn't be crowning if ros is 0 so that's why this is in an else
    fc += fuel->crownConsumption(fuel->crownFractionBurned(head_ros_, rso));
  }
  // max intensity should always be at the head
  max_intensity_ = fuel::fire_intensity(fc, ros);
  const auto a = (head_ros_ + back_ros) / 2.0;
  const auto c = a - back_ros;
  const auto flank_ros = a / fuel->lengthToBreadth(wsv);
  const auto a_sq = a * a;
  const auto flank_ros_sq = flank_ros * flank_ros;
  const auto a_sq_sub_c_sq = a_sq - (c * c);
  const auto ac = a * c;
  const auto calculate_ros =
    [a, c, ac, flank_ros, a_sq, flank_ros_sq, a_sq_sub_c_sq](const double theta) noexcept
  {
    const auto cos_t = cos(theta);
    const auto cos_t_sq = cos_t * cos_t;
    const auto f_sq_cos_t_sq = flank_ros_sq * cos_t_sq;
    // 1.0 = cos^2 + sin^2
    const auto sin_t_sq = 1.0 - cos_t_sq;
    return abs((a * ((flank_ros * cos_t *
        sqrt(f_sq_cos_t_sq + a_sq_sub_c_sq * sin_t_sq) - ac * sin_t_sq)
      / (f_sq_cos_t_sq + a_sq * sin_t_sq)) + c) / cos_t);
  };
  const auto add_offsets =
    [&correction_factor, &add_offset, raz, threshold](
    const double angle_radians,
    const double ros_flat)
  {
    if (ros_flat < threshold)
    {
      return false;
    }
    auto direction = util::fix_radians(angle_radians + raz);
    // spread is symmetrical across the center axis, but needs to be adjusted if on a slope
    // intentionally don't use || because we want both of these to happen all the time
    auto added = add_offset(direction, ros_flat * correction_factor(direction));
    direction = util::fix_radians(raz - angle_radians);
    added |= add_offset(direction, ros_flat * correction_factor(direction));
    return added;
  };
  const auto add_offsets_calc_ros =
    [&add_offsets, &calculate_ros](const double angle_radians)
  {
    return add_offsets(angle_radians, calculate_ros(angle_radians));
  };
  // HACK: rely on && to stop when first ros is too low
  if (add_offsets_calc_ros(util::to_radians(10))
    && add_offsets_calc_ros(util::to_radians(20))
    && add_offsets_calc_ros(util::to_radians(30))
    && add_offsets_calc_ros(util::to_radians(60))
    && add_offsets(util::to_radians(90.0), flank_ros * sqrt(a_sq_sub_c_sq) / a)
    && add_offsets_calc_ros(util::to_radians(120))
    && add_offsets_calc_ros(util::to_radians(150)))
  {
    //only use back ros if every other angle is spreading since this should be lowest
    // 180
    if (back_ros < threshold)
    {
      return;
    }
    const auto direction = util::fix_radians(util::RAD_180 + raz);
    static_cast<void>(!add_offset(direction, back_ros * correction_factor(direction)));
  }
}
// double SpreadInfo::calculateSpreadProbability(const double ros)
// {
//   // note: based off spread event probability from wotton
//   return 1 / (1 + exp(1.64 - 0.16 * ros));
// }
}
}
