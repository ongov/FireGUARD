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
#include "LookupTable.h"
namespace firestarr
{
namespace fuel
{
// References
// Lawson, B.D.; Frandsen, W.H.; Hawkes, B.C.; Dalrymple, G.N. 1997.
// Probability of sustained smoldering ignitions for some boreal forest duff types.
// https://cfs.nrcan.gc.ca/pubwarehouse/pdfs/11900.pdf
//
// Frandsen, W.H. 1997.
// Ignition probability of organic soils.
// https://www.nrcresearchpress.com/doi/pdf/10.1139/x97-106
//
template <int Ash, int Rho, int B0, int B1, int B2, int B3>
class DuffType;
/**
 * \brief Base class for DuffType.
 */
class Duff
{
public:
  virtual ~Duff() = default;
  Duff(const Duff& rhs) noexcept = delete;
  Duff(Duff&& rhs) noexcept = delete;
  Duff& operator=(const Duff& rhs) noexcept = delete;
  Duff& operator=(Duff&& rhs) noexcept = delete;
  /**
   * \brief Equality operator
   * \param rhs Duff to compare to
   * \return Whether or not these are identical
   */
  [[nodiscard]] constexpr bool operator==(const Duff& rhs) const
  {
    // HACK: only equivalent if identical
    return this == &rhs;
  }
  /**
   * \brief Inequality operator
   * \param rhs Duff to compare to
   * \return Whether or not these are not identical
   */
  [[nodiscard]] constexpr bool operator!=(const Duff& rhs) const
  {
    return !operator==(rhs);
  }
  /**
   * \brief Survival probability calculated using probability of ony survival based on multiple formulae
   * \param mc_pct Moisture content (%)
   * \return Chance of survival (% / 100)
   */
  [[nodiscard]] virtual double probabilityOfSurvival(double mc_pct) const noexcept = NULL;
  // from kerry's paper
  // static const Duff FeatherMossUpper;
  // static const Duff FeatherMossLower;
  /**
   * \brief Sphagnum (upper) [Frandsen table 2/3]
   */
  static const DuffType<124, 218, -88306, -608, 8095, 2735> SphagnumUpper;
  // static const Duff SphagnumLower;
  /**
   * \brief Feather [Frandsen table 3]
   */
  static const DuffType<181, 427, 90970, -1040, 1165, -646> FeatherMoss;
  /**
   * \brief Reindeer/feather [Frandsen table 2/3]
   */
  static const DuffType<261, 563, 80359, -393, -591, -340> Reindeer;
  // static const Duff SedgeMeadowUpper;
  // static const Duff SedgeMeadowLower;
  /**
   * \brief White spruce duff [Frandsen table 2/3]
   */
  static const DuffType<359, 1220, 3325604, -12220, -21024, -12619> WhiteSpruce;
  /**
   * \brief Peat [Frandsen table 2/3]
   */
  static const DuffType<94, 2220, -198198, -1169, 10414, 782> Peat;
  /**
   * \brief Peat muck [Frandsen table 2/3]
   */
  static const DuffType<349, 2030, 372276, -1876, -2833, -951> PeatMuck;
  // static const Duff SedgeMeadowSeney;
  /**
   * \brief Pine duff (Seney) [Frandsen table 2/3]
   */
  static const DuffType<365, 1900, 451778, -3227, -3644, -362> PineSeney;
  /**
   * \brief Spruce/pine duff [Frandsen table 2/3]
   */
  static const DuffType<307, 1160, 586921, -2737, -5413, -1246> SprucePine;
  // static const Duff GrassSedgeMarsh;
  // static const Duff SouthernPine;
  // static const Duff HardwoodSwamp;
  // coefficients aren't defined in the table these came from
  // static const Duff Pocosin;
  // static const Duff SwampForest;
  // static const Duff Flatwoods;
protected:
  Duff() = default;
};
/**
 * \brief A specific type of Duff layer, and the associated smouldering coefficients.
 */
template <int Ash, int Rho, int B0, int B1, int B2, int B3>
class DuffType final
  : public Duff
{
public:
  DuffType() = default;
#pragma warning (push)
#pragma warning (disable: 26443)
  virtual ~DuffType() = default;
#pragma warning (pop)
  DuffType(const DuffType& rhs) noexcept = delete;
  DuffType(DuffType&& rhs) noexcept = delete;
  DuffType& operator=(const DuffType& rhs) noexcept = delete;
  DuffType& operator=(DuffType&& rhs) noexcept = delete;
  /**
   * \brief Probability of survival (% / 100) [eq Ig-1]
   * \param mc_pct Moisture content, percentage dry oven weight
   * \return Probability of survival (% / 100) [eq Ig-1]
   */
  [[nodiscard]] double probabilityOfSurvival(const double mc_pct) const noexcept override
  {
    return probability_of_survival_(mc_pct);
  }
  /**
   * \brief Inorganic content, percentage oven dry weight
   * \return Inorganic content, percentage oven dry weight
   */
  [[nodiscard]] static constexpr double ash() { return Ash / 10.0; }
  /**
   * \brief Organic bulk density (kg/m^3)
   * \return Organic bulk density (kg/m^3)
   */
  [[nodiscard]] static constexpr double rho() { return Rho / 10.0; }
  /**
   * \brief B_0 [table 2]
   * \return B_0 [table 2]
   */
  [[nodiscard]] static constexpr double b0() { return B0 / 10000.0; }
  /**
   * \brief B_1 [table 2]
   * \return B_1 [table 2]
   */
  [[nodiscard]] static constexpr double b1() { return B1 / 10000.0; }
  /**
   * \brief B_2 [table 2]
   * \return B_2 [table 2]
   */
  [[nodiscard]] static constexpr double b2() { return B2 / 10000.0; }
  /**
   * \brief B_3 [table 2]
   * \return B_3 [table 2]
   */
  [[nodiscard]] static constexpr double b3() { return B3 / 10000.0; }
private:
  /**
   * \brief Constant part of ignition probability equation [eq Ig-1]
   */
  static constexpr auto ConstantPart = b0() + b2() * ash() + b3() * rho();
  /**
   * \brief Ignition Probability (% / 100) [eq Ig-1]
   * \param mc_pct Moisture content, percentage dry oven weight
   * \return Ignition Probability (% / 100) [eq Ig-1]
   */
  [[nodiscard]] static constexpr double duffFunction(const double mc_pct) noexcept
  {
    const auto d = 1 + exp(-(b1() * mc_pct + ConstantPart));
    if (0 == d)
    {
      return 1.0;
    }
    return 1.0 / d;
  }
  /**
   * \brief Ignition Probability (% / 100) [eq Ig-1]
   * \param mc_pct Moisture content, percentage dry oven weight
   * \return Ignition Probability (% / 100) [eq Ig-1]
   */
  const util::LookupTable<&duffFunction> probability_of_survival_{};
};
}
}
