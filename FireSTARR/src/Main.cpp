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

/*! \mainpage FireSTARR Documentation
 *
 * \section intro_sec Introduction
 *
 * FireSTARR is a probabilistic fire growth model that relies on the presence of
 * WeatherSHIELD for its inputs.
 */
#include "stdafx.h"
#include "Model.h"
#include "Scenario.h"
#include "Test.h"
#include "Time.h"
#include "Util.h"
#include "WxShield.h"
using firestarr::logging::Log;
using firestarr::sim::Settings;
void show_usage_and_exit(const char* name)
{
  cout << "Usage:" << name <<
    " <output_dir> <yyyy-mm-dd> <lat> <lon> <HH:MM> [options] [-v | -q]" << endl << endl
    << " Run simulations and save output in the specified directory" << endl << endl
    << "Usage: " << name <<
    " <output_dir> <yyyy-mm-dd> <lat> <lon> <numDays> [-v | -q | -f]"
    << endl << endl
    << " Save WeatherSHIELD output for the give number of days in the specified directory"
    << endl << endl
    << "Usage: " << name << " test <output_dir> <numHours>"
    << "[slope [aspect [wind_speed [wind_direction]]]]" << endl << endl
    << " Run test cases and save output in the specified directory" << endl << endl
    << " Input Options" << endl
    << "   -h                        Show help" << endl
    << "   -v                        Increase output level" << endl
    << "   -q                        Decrease output level" << endl
    << "   -a                        Run using actuals for weather" << endl
    << "   -i                        Save intensity maps for simulations" << endl
    << "   -s                        Run in synchronous mode" << endl
    << "   -f                        Full export of all weather" << endl
    << "   --perim                   Start from perimeter" << endl
    << "   --size                    Start from size" << endl
    << "   --ffmc                    Override startup Fine Fuel Moisture Code" << endl
    << "   --dmc                     Override startup Duff Moisture Code" << endl
    << "   --dc                      Override startup Drought Code" << endl
    << "   --apcp_0800               Override startup 0800 precipitation" << endl;
  exit(-1);
}
const char* get_arg(const char* const name,
                    int* i,
                    const int argc,
                    const char* const argv[]) noexcept
{
  // check if we don't have any more arguments
  firestarr::logging::check_fatal(*i + 1 >= argc, "Missing argument to --%s", name);
  // check if we have another flag right after
  firestarr::logging::check_fatal('-' == argv[*i + 1][0],
                                  "Missing argument to --%s",
                                  name);
  return argv[++*i];
}
int main(const int argc, const char* const argv[])
{
  // _CrtSetDbgFlag(_CRTDBG_ALLOC_MEM_DF | _CRTDBG_LEAK_CHECK_DF);
  Log::setLogLevel(firestarr::logging::LOG_NOTE);
  auto bin = string(argv[0]);
  replace(bin.begin(), bin.end(), '\\', '/');
  const auto end = max(static_cast<size_t>(0), bin.rfind('/') + 1);
  bin = bin.substr(end, bin.size() - end);
  const auto name = bin.c_str();
  if (3 > argc)
  {
    show_usage_and_exit(name);
  }
  try
  {
    if (argc > 3 && 0 == strcmp(argv[1], "test"))
    {
      return firestarr::sim::test(argc, argv);
    }
    if (6 <= argc)
    {
      // HACK: use a variable and ++ in case if arg indices change
      auto i = 1;
      string output_directory(argv[i++]);
      replace(output_directory.begin(), output_directory.end(), '\\', '/');
      if ('/' != output_directory[output_directory.length() - 1])
      {
        output_directory += '/';
      }
      firestarr::logging::debug("Output directory is %s", output_directory.c_str());
      string date(argv[i++]);
      TIMESTAMP_STRUCT start_date{};
      start_date.year = static_cast<SQLSMALLINT>(stoi(date.substr(0, 4)));
      start_date.month = static_cast<SQLUSMALLINT>(stoi(date.substr(5, 2)));
      start_date.day = static_cast<SQLUSMALLINT>(stoi(date.substr(8, 2)));
      const auto latitude = stod(argv[i++]);
      const auto longitude = stod(argv[i++]);
      const firestarr::topo::StartPoint start_point(latitude, longitude);
      size_t num_days = 0;
      auto is_wx_only = false;
      string arg(argv[i++]);
      auto save_intensity = false;
      auto actuals_only = false;
      auto full_wx = false;
      string perim;
      size_t size = 0;
      auto score = 0.0;
      firestarr::wx::Ffmc* ffmc = nullptr;
      firestarr::wx::Dmc* dmc = nullptr;
      firestarr::wx::Dc* dc = nullptr;
      firestarr::wx::AccumulatedPrecipitation* apcp_0800 = nullptr;
      tm start{};
      if (5 == arg.size() && ':' == arg[2])
      {
        try
        {
          // if this is a time then we aren't just running the weather
          start_date.hour = static_cast<SQLUSMALLINT>(stoi(arg.substr(0, 2)));
          start_date.minute = static_cast<SQLUSMALLINT>(stoi(arg.substr(3, 2)));
          // we were given a time, so number of days is until end of year
          firestarr::util::to_tm(start_date, &start);
          // HACK: make sure we have the same start hour
          start.tm_hour = start_date.hour;
          const auto start_t = mktime(&start);
          auto year_end = start;
          year_end.tm_mon = 11;
          year_end.tm_mday = 31;
          const auto seconds = difftime(mktime(&year_end), start_t);
          // start day counts too, so +1
          // HACK: but we don't want to go to Jan 1 so don't add 1
          num_days = static_cast<size_t>(seconds / firestarr::DAY_SECONDS);
          firestarr::logging::debug("Calculated number of days until end of year: %d",
                                    num_days);
          // +1 because day 1 counts too
          // +2 so that results don't change when we change number of days
          num_days = min(num_days, static_cast<size_t>(Settings::maxDateOffset()) + 2);
        }
        catch (std::exception&)
        {
          show_usage_and_exit(name);
        }
        while (i < argc)
        {
          if (0 == strcmp(argv[i], "-i"))
          {
            if (save_intensity)
            {
              show_usage_and_exit(name);
            }
            save_intensity = true;
          }
          else if (0 == strcmp(argv[i], "-s"))
          {
            if (!Settings::runAsync())
            {
              show_usage_and_exit(name);
            }
            Settings::setRunAsync(false);
          }
          else if (0 == strcmp(argv[i], "-v"))
          {
            // can be used multiple times
            Log::increaseLogLevel();
          }
          else if (0 == strcmp(argv[i], "-q"))
          {
            // if they want to specify -v and -q then that's fine
            Log::decreaseLogLevel();
          }
          else if (0 == strcmp(argv[i], "-a"))
          {
            if (actuals_only)
            {
              show_usage_and_exit(name);
            }
            actuals_only = true;
          }
          else if (0 == strcmp(argv[i], "--perim"))
          {
            if (!perim.empty())
            {
              show_usage_and_exit(name);
            }
            perim = get_arg("perim", &i, argc, argv);
          }
          else if (0 == strcmp(argv[i], "-w"))
          {
            Settings::setWeatherFile(string(get_arg("w", &i, argc, argv)));
          }
          else if (0 == strcmp(argv[i], "--size"))
          {
            if (0 != size)
            {
              show_usage_and_exit(name);
            }
            size = static_cast<size_t>(stoi(get_arg("size", &i, argc, argv)));
          }
          else if (0 == strcmp(argv[i], "--score"))
          {
            if (0 != score)
            {
              show_usage_and_exit(name);
            }
            score = stod(get_arg("score", &i, argc, argv));
            Settings::setMaxGrade(score);
          }
          else if (0 == strcmp(argv[i], "--ffmc"))
          {
            if (nullptr != ffmc)
            {
              show_usage_and_exit(name);
            }
            ffmc = new firestarr::wx::Ffmc(stod(get_arg("ffmc", &i, argc, argv)));
          }
          else if (0 == strcmp(argv[i], "--dmc"))
          {
            if (nullptr != dmc)
            {
              show_usage_and_exit(name);
            }
            dmc = new firestarr::wx::Dmc(stod(get_arg("dmc", &i, argc, argv)));
          }
          else if (0 == strcmp(argv[i], "--dc"))
          {
            if (nullptr != dc)
            {
              show_usage_and_exit(name);
            }
            dc = new firestarr::wx::Dc(stod(get_arg("dc", &i, argc, argv)));
          }
          else if (0 == strcmp(argv[i], "--apcp_0800"))
          {
            if (nullptr != apcp_0800)
            {
              show_usage_and_exit(name);
            }
            apcp_0800 = new firestarr::wx::AccumulatedPrecipitation(
              stod(get_arg("apcp_0800", &i, argc, argv)));
          }
          else
          {
            show_usage_and_exit(name);
          }
          ++i;
        }
      }
      else
      {
        // we weren't given a time as the argument, so it's number of days
        try
        {
          is_wx_only = true;
          num_days = static_cast<size_t>(stoi(arg));
          if (0 != strcmp(to_string(num_days).c_str(), arg.c_str()))
          {
            show_usage_and_exit(name);
          }
          while (i < argc)
          {
            if (0 == strcmp(argv[i], "-f"))
            {
              if (full_wx)
              {
                show_usage_and_exit(name);
              }
              firestarr::logging::note("Dumping all weather");
              full_wx = true;
            }
            else if (0 == strcmp(argv[i], "-v"))
            {
              // can be used multiple times
              Log::increaseLogLevel();
            }
            else if (0 == strcmp(argv[i], "-q"))
            {
              // if they want to specify -v and -q then that's fine
              Log::decreaseLogLevel();
            }
            else if (0 == strcmp(argv[i], "-a"))
            {
              if (actuals_only)
              {
                show_usage_and_exit(name);
              }
              actuals_only = true;
            }
            else if (0 == strcmp(argv[i], "-w"))
            {
              Settings::setWeatherFile(string(get_arg("w", &i, argc, argv)));
            }
            else if (0 == strcmp(argv[i], "--score"))
            {
              if (0 != score)
              {
                show_usage_and_exit(name);
              }
              score = stod(get_arg("score", &i, argc, argv));
              Settings::setMaxGrade(score);
            }
            else if (0 == strcmp(argv[i], "--ffmc"))
            {
              if (nullptr != ffmc)
              {
                show_usage_and_exit(name);
              }
              ffmc = new firestarr::wx::Ffmc(stod(get_arg("ffmc", &i, argc, argv)));
            }
            else if (0 == strcmp(argv[i], "--dmc"))
            {
              if (nullptr != dmc)
              {
                show_usage_and_exit(name);
              }
              dmc = new firestarr::wx::Dmc(stod(get_arg("dmc", &i, argc, argv)));
            }
            else if (0 == strcmp(argv[i], "--dc"))
            {
              if (nullptr != dc)
              {
                show_usage_and_exit(name);
              }
              dc = new firestarr::wx::Dc(stod(get_arg("dc", &i, argc, argv)));
            }
            else if (0 == strcmp(argv[i], "--apcp_0800"))
            {
              if (nullptr != apcp_0800)
              {
                show_usage_and_exit(name);
              }
              apcp_0800 = new firestarr::wx::AccumulatedPrecipitation(
                stod(get_arg("apcp_0800", &i, argc, argv)));
            }
            else
            {
              show_usage_and_exit(name);
            }
            ++i;
          }
        }
        catch (std::exception&)
        {
          show_usage_and_exit(name);
        }
      }
      struct stat info{};
      if (stat(output_directory.c_str(), &info) != 0 || !(info.st_mode & S_IFDIR))
      {
        firestarr::util::make_directory_recursive(output_directory.c_str());
      }
      auto wx_file = output_directory + Settings::weatherFile();
      firestarr::wx::WxShield wx(start_date,
                                 start_point,
                                 num_days,
                                 wx_file,
                                 ffmc,
                                 dmc,
                                 dc,
                                 apcp_0800,
                                 full_wx);
      if (is_wx_only)
      {
        return 0;
      }
      const auto y = wx.readYesterday();
      auto yesterday{nullptr == y ? firestarr::wx::FwiWeather::Zero : *y};
      // replace any overridden indices
      const auto ffmc_fixed = nullptr == ffmc ? yesterday.ffmc() : *ffmc;
      const auto dmc_fixed = nullptr == dmc ? yesterday.dmc() : *dmc;
      const auto dc_fixed = nullptr == dc ? yesterday.dc() : *dc;
      const auto isi_fixed = firestarr::wx::Isi(yesterday.wind().speed(), ffmc_fixed);
      const auto bui_fixed = firestarr::wx::Bui(dmc_fixed, dc_fixed);
      const auto fwi_fixed = firestarr::wx::Fwi(isi_fixed, bui_fixed);
      yesterday = firestarr::wx::FwiWeather(yesterday.tmp(),
                                            yesterday.rh(),
                                            yesterday.wind(),
                                            yesterday.apcp(),
                                            ffmc_fixed,
                                            dmc_fixed,
                                            dc_fixed,
                                            isi_fixed,
                                            bui_fixed,
                                            fwi_fixed);
      firestarr::util::to_tm(start_date, &start);
      // HACK: make sure we have the same start hour
      start.tm_hour = start_date.hour;
      cout << "Arguments are:\n";
      for (auto j = 0; j < argc; ++j)
      {
        cout << " " << argv[j];
      }
      cout << "\n";
      return firestarr::sim::Model::runScenarios(output_directory.c_str(),
                                                 wx_file.c_str(),
                                                 Settings::fuelLookupTable(),
                                                 Settings::rasterRoot(),
                                                 yesterday,
                                                 start_point,
                                                 start,
                                                 save_intensity,
                                                 actuals_only,
                                                 perim,
                                                 size);
    }
    show_usage_and_exit(name);
  }
  catch (const runtime_error& err)
  {
    firestarr::logging::fatal(err.what());
  }
}
