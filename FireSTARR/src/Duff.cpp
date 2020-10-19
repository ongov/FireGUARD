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
#include "Duff.h"
namespace firestarr
{
namespace fuel
{
// from kerry's paper
// const Duff Duff::FeatherMossUpper(17.2, 46.4, 13.9873, -0.3296, 0.4904, 0.0568);
// const Duff Duff::FeatherMossLower(19.1, 38.9, 13.2628, -0.1167, 0.3308, -0.2604);
const DuffType<124, 218, -88306, -608, 8095, 2735> Duff::SphagnumUpper{};
// const Duff Duff::SphagnumLower(56.7, 119, 327.3347, -3.7655, -8.7849, 2.6684);
const DuffType<181, 427, 90970, -1040, 1165, -646> Duff::FeatherMoss{};
const DuffType<261, 563, 80359, -393, -591, -340> Duff::Reindeer{};
// const Duff Duff::SedgeMeadowUpper(23.3, 69.4, 39.8477, -0.18, -0.3727, -0.1874);
// const Duff Duff::SedgeMeadowLower(44.9, 91.5, 29.0818, -0.2059, -0.2319, -0.042);
const DuffType<359, 1220, 3325604, -12220, -21024, -12619> Duff::WhiteSpruce{};
const DuffType<94, 2220, -198198, -1169, 10414, 782> Duff::Peat{};
const DuffType<349, 2030, 372276, -1876, -2833, -951> Duff::PeatMuck{};
// const Duff Duff::SedgeMeadowSeney(35.4, 183, 7.1813, -0.1413, -0.1253, 0.039);
const DuffType<365, 1900, 451778, -3227, -3644, -362> Duff::PineSeney{};
const DuffType<307, 1160, 586921, -2737, -5413, -1246> Duff::SprucePine{};
// const Duff Duff::GrassSedgeMarsh(35.2, 120, 236.2934, -0.8423, -2.5097, -0.4902);
// const Duff Duff::SouthernPine(68, 112, 58.6921, -0.2737, -0.5413, -0.1246);
// const Duff Duff::HardwoodSwamp(18.2, 138, 33.6907, -0.2946, -0.3002, -0.0404);
}
}
