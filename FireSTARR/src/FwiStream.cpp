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
#include "FwiStream.h"
#include "Startup.h"
namespace firestarr::wx
{
FwiStream::FwiStream(FwiVector&& wx) noexcept
  : wx_(std::move(wx))
{
}
FwiStream::FwiStream(const vector<TIMESTAMP_STRUCT>& dates,
                     Startup* startup,
                     const double latitude,
                     vector<Weather> cur_member)
{
  static const AccumulatedPrecipitation ZeroFfmcPrecipitationAmount(2);
  static const AccumulatedPrecipitation ZeroDmcPrecipitationAmount(10);
  assert(cur_member.size() <= dates.size());
  int month = dates.at(0).month;
  auto started = (nullptr != startup) ||
    (month > 9 || (9 == month && 15 <= dates.at(0).day));
  auto shutdown = !started;
  static auto fake_startup = Startup(L"",
                                     TIMESTAMP_STRUCT{},
                                     topo::Point(0, 0),
                                     0,
                                     Ffmc(0),
                                     Dmc(0),
                                     Dc(0),
                                     AccumulatedPrecipitation(0),
                                     false);
  // HACK: could be started but now ended and marked as started because of month/day
  const Startup* const use_startup = (!started || nullptr == startup)
                                       ? &fake_startup
                                       : startup;
  auto last_ffmc = use_startup->ffmc();
  auto last_dmc = use_startup->dmc();
  auto last_dc = use_startup->dc();
  Dc shutdown_dc(-1);
  AccumulatedPrecipitation since_shutdown_accumulation(-1);
  for (size_t date_index = 0; date_index < cur_member.size(); ++date_index)
  {
    const auto& wx = cur_member.at(date_index);
    const auto for_date = dates.at(date_index);
    month = for_date.month;
    if (date_index >= 2)
    {
      // if we rolled into next year then start checking for startup conditions again
      if (shutdown && started && 1 == month)
      {
        started = false;
      }
      if (!started)
      {
        // try to see if we can start things
        double sum = 0;
        for (auto j = date_index - 2; j <= date_index; ++j)
        {
          sum += cur_member.at(j).tmp().asDouble();
        }
        const auto avg = sum / 3;
        // start stations if average temperature is at or over 11C for 3 consecutive days
        started = avg >= 11;
        if (started)
        {
          // use default startup values for FWI indices
          // FIX: check that we're doing this right - should these be yesterday's indices
          // (i.e. lastValues) or today's?
          last_ffmc = Ffmc(85.0);
          last_dmc = Dmc(6.0);
          // FIX: DC adjustment isn't correct over winter
          if (Dc(0) <= shutdown_dc)
          {
            last_dc = Dc(15.0);
          }
        }
        // we aren't shutdown if we just started
        shutdown = !started;
        if (started)
        {
          shutdown_dc = Dc(-1);
          since_shutdown_accumulation = AccumulatedPrecipitation(-1);
        }
      }
      else if (((!shutdown && month > 9)
        || (9 == month && 15 <= for_date.day)) && date_index >= 2)
      {
        // try to see if we can stop things
        double sum = 0;
        for (auto j = date_index - 2; j <= date_index; ++j)
        {
          sum += cur_member.at(j).tmp().asDouble();
        }
        auto avg = sum / 3;
        // shut down station if DMC < 10 and temperature <= 2.5C for 3 days
        shutdown = Dmc(10) > last_dmc && 2.5 >= avg;
        // check if past week has been 2.5C
        // NOTE: need to be able to average at least 7 days
        if (!shutdown && date_index >= 6)
        {
          // try to see if we can stop things
          sum = 0;
          for (auto j = date_index - 6; j <= date_index; ++j)
          {
            sum += cur_member.at(j).tmp().asDouble();
          }
          avg = sum / 7;
          // shut down station if temperature <= 2.5C for 7 days
          shutdown = 2.5 >= avg;
        }
      }
      else if (10 <= month)
      {
        shutdown = true;
      }
    }
    auto apcp = wx.apcp();
    // have to add apcp because it isn't in accumulation yet
    if (shutdown)
    {
      since_shutdown_accumulation += apcp;
    }
    // if no startup then we don't need to add since it's 0
    if (0 == date_index && nullptr != startup)
    {
      // need to add in 0800 obs for day 1
      apcp += startup->apcp0800();
    }
    Ffmc ffmc(wx.tmp(), wx.rh(), wx.wind().speed(), apcp, last_ffmc);
    if (shutdown)
    {
      // HACK: if we got 2mm of pcp since shutdown then assume 0 indices
      if (since_shutdown_accumulation > ZeroFfmcPrecipitationAmount)
      {
        ffmc = Ffmc(0.0);
      }
      else
      {
        // want to decrease the value but never increase it
        ffmc = min(last_ffmc, ffmc);
      }
    }
    ffmc = max(Ffmc(0.0), ffmc);
    Dmc dmc(wx.tmp(), wx.rh(), apcp, last_dmc, month, latitude);
    if (shutdown)
    {
      // HACK: if we got 10mm of pcp since shutdown then assume 0 indices
      if (since_shutdown_accumulation > ZeroDmcPrecipitationAmount)
      {
        dmc = Dmc(0.0);
      }
      else
      {
        // want to decrease the value but never increase it
        dmc = min(last_dmc, dmc);
      }
    }
    dmc = max(Dmc(0.0), dmc);
    Dc dc(0);
    if (shutdown)
    {
      assert(Dc(0) <= shutdown_dc);
      assert(AccumulatedPrecipitation(0) <= since_shutdown_accumulation);
      const auto a = 1.0;
      // NOTE: concerned about the lack of overwinter precipitation present
      // in reanalysis data
      // NOTE: use 0.9 due to deep duff fuels
      const auto b = 0.9;
      const auto smi_f = 800 * exp(-shutdown_dc.asDouble() / 400.0);
      const auto smi_s = a * smi_f + b * since_shutdown_accumulation.asDouble();
      dc = min(last_dc, Dc(400 * log(800 / smi_s)));
    }
    else
    {
      dc = Dc(wx.tmp(), apcp, last_dc, month, latitude);
    }
    dc = max(Dc(0.0), dc);
    const Isi isi(wx.wind().speed(), ffmc);
    const Bui bui(dmc, dc);
    const Fwi fwi(isi, bui);
    // need to add in check for station startup and shutdown
    wx_.emplace_back(wx.tmp(),
                     wx.rh(),
                     wx.wind(),
                     apcp,
                     ffmc,
                     dmc,
                     dc,
                     isi,
                     bui,
                     fwi);
    last_ffmc = ffmc;
    last_dmc = dmc;
    last_dc = dc;
    if (started && !shutdown)
    {
      shutdown_dc = last_dc;
      since_shutdown_accumulation = AccumulatedPrecipitation(0.0);
    }
  }
}
}
