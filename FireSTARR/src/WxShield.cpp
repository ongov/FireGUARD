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
#include "WxShield.h"
#include "FWI.h"
#include "FwiStream.h"
#include "Log.h"
#include "Score.h"
#include "Settings.h"
#include "Time.h"
#include "Util.h"
namespace firestarr
{
namespace wx
{
map<WeatherModel, map<int, vector<Weather>>, ModelCompare> WxShield::
readForecastByOffset(
  const topo::Point& point,
  const TIMESTAMP_STRUCT& start_date,
  const int offset,
  const size_t num_days)
{
  auto db = getWxDb(start_date);
  return db.readModel(
    L"SELECT [Generated],"
    " [Model], [Latitude], [Longitude], [DISTANCE_FROM], [Member],"
    " [ForTime],"
    " [TMP], [RH], [WS], [WD], [APCP]"
    " FROM [INPUTS].[FCT_Forecast_By_Offset](" + to_wstring(offset)
    + L", " + to_wstring(point.latitude())
    + L", " + to_wstring(point.longitude())
    + L", " + to_wstring(num_days) + L")"
    " order by [Model], [Member], [ForTime]\n");
}
map<WeatherModel, map<int, vector<Weather>>, ModelCompare> WxShield::
readHindcastByOffset(
  const topo::Point& point,
  const int offset,
  const size_t num_days)
{
  return util::Database(L"HINDCAST").readModel(
    L"SELECT [Generated],"
    " [Model], [Latitude], [Longitude], [DISTANCE_FROM], [Member],"
    " [ForTime],"
    " [TMP], [RH], [WS], [WD], [APCP]"
    " FROM [HINDCAST].[FCT_Hindcast_By_Offset](" + to_wstring(offset)
    + L", " + to_wstring(point.latitude())
    + L", " + to_wstring(point.longitude())
    + L", " + to_wstring(num_days) + L")"
    " order by [Model], [Member], [ForTime]\n");
}
unique_ptr<FwiWeather> WxShield::readYesterday(const topo::Point& point,
                                               const TIMESTAMP_STRUCT& start_date,
                                               const int offset)
{
  auto y = getDfossDb(start_date).readList<FwiWeather>(
    L"SELECT [ForTime],"
    " [TMP], [RH], [WS], [WD], [APCP], "
    " [FFMC], [DMC], [DC], [ISI], [BUI], [FWI]"
    " FROM [INPUTS].[FCT_Actuals](" + to_wstring(offset - 1)
    + L", " + to_wstring(1)
    + L", " + to_wstring(point.latitude())
    + L", " + to_wstring(point.longitude())
    + L", DEFAULT) order by [ForTime]\n");
  return y.empty() ? nullptr : make_unique<FwiWeather>(y.at(0));
}
unique_ptr<FwiWeather> WxShield::readYesterday() const
{
  return readYesterday(point_, start_date_, offset_);
}
vector<Weather> WxShield::readActualsByOffset(const topo::Point& point,
                                              const TIMESTAMP_STRUCT& start_date,
                                              const int offset,
                                              const size_t num_days)
{
  auto result = getDfossDb(start_date).readList<Weather>(
    L"SELECT [ForTime],"
    " [TMP], [RH], [WS], [WD], [APCP]"
    " FROM [INPUTS].[FCT_Actuals](" + to_wstring(offset)
    + L", " + to_wstring(num_days)
    + L", " + to_wstring(point.latitude())
    + L", " + to_wstring(point.longitude())
    + L", DEFAULT) order by [ForTime]\n");
  // HACK: assume weather is missing at start of period if in first half of year
  if (start_date.month < 6)
  {
    while (result.size() < num_days)
    {
      result.emplace(result.begin(),
                     Temperature::Zero,
                     RelativeHumidity::Zero,
                     Wind::Zero,
                     AccumulatedPrecipitation::Zero);
    }
  }
  return result;
}
WxShield& WxShield::operator=(const WxShield& rhs)
{
  if (this != &rhs)
  {
    dates_ = rhs.dates_;
    point_ = rhs.point_;
    start_date_ = rhs.start_date_;
    save_to_ = rhs.save_to_;
    startup_ = make_unique<Startup>(*rhs.startup_);
    offset_ = rhs.offset_;
  }
  return *this;
}
vector<Score> WxShield::readScoreByOffset(const int offset)
{
  return util::Database(L"HINDCAST").readList<Score>(
    L"SELECT [Year], [AVG_VALUE], [GRADE]"
    " FROM [HINDCAST].[FCT_HistoricMatch_By_Offset]"
    "(" + to_wstring(offset) + L")"
    " ORDER BY [GRADE] DESC\n");
}
util::Database WxShield::getWxDb(const TIMESTAMP_STRUCT& start_date)
{
  WCHAR buf[10];
  swprintf_s(buf, 10, L"WX_%04d%02d", start_date.year, start_date.month);
  return util::Database(wstring(buf));
}
util::Database WxShield::getDfossDb(const TIMESTAMP_STRUCT& start_date)
{
  return util::Database(L"DFOSS_" + to_wstring(start_date.year));
}
unique_ptr<Startup> WxShield::readStartupByOffset(const topo::Point& point,
                                                  const TIMESTAMP_STRUCT& start_date,
                                                  const int offset)
{
  auto rows = getDfossDb(start_date).readList<Startup>(
    L"SELECT [Member], [Generated], [Latitude], [Longitude],"
    " [DISTANCE_FROM], [FFMC], [DMC], [DC], ISNULL([APCP_0800], 0)"
    " FROM [INPUTS].[FCT_FWIObserved_By_Offset]("
    + to_wstring(offset - 1)
    + L", " + to_wstring(point.latitude())
    + L", " + to_wstring(point.longitude()) +
    L", DEFAULT)\n");
  logging::check_fatal(rows.size() > 1,
                       "Too many rows returned when looking for startup indices");
  return 1 == rows.size() ? make_unique<Startup>(rows.at(0)) : nullptr;
}
string to_string(const TIMESTAMP_STRUCT& ts)
{
  char buf[100] = {0};
  assert(0 == ts.fraction);
  assert(0 == ts.second);
  sprintf_s(buf,
            100,
            "%04d-%02d-%02d %02d:%02d",
            ts.year,
            ts.month,
            ts.day,
            ts.hour,
            ts.minute);
  return string(buf);
}
ostream& operator<<(ostream& os, const TIMESTAMP_STRUCT& ts)
{
  os << to_string(ts);
  return os;
}
template <class T>
TIMESTAMP_STRUCT date_by_offset(T offset) noexcept
{
  TIMESTAMP_STRUCT result{};
  const auto t = time(nullptr) + DAY_SECONDS * static_cast<time_t>(offset);
  // convert to local time
  tm local{};
  localtime_s(&local, &t);
  // HACK: always use 13:00
  local.tm_hour = 13;
  local.tm_min = 0;
  local.tm_sec = 0;
  util::to_ts(local, &result);
  return result;
}
int offset_by_date(const TIMESTAMP_STRUCT& d) noexcept
{
  const auto t = time(nullptr);
  tm tmd{0, 0, 0, d.day, d.month - 1, d.year - 1900, 0, 0, 0};
  const auto seconds = difftime(mktime(&tmd), t);
  return static_cast<int>(seconds / DAY_SECONDS);
}
void WxShield::preProcessEnsembles(ModelMap& hindcasts, vector<int>& years) const
{
  unordered_map<int, bool> remove_years{};
  const size_t year_length = 365;
  auto members = &hindcasts.at(hindcasts.begin()->first);
  const auto original_length = min(year_length,
                                   (*members).at(members->begin()->first).size());
  for (const auto& kv : hindcasts)
  {
    auto& cur_model = kv.first;
    members = &hindcasts.at(cur_model);
    // do this to deal with leap years possibly being in there (so 366 days)
    for (const auto& mv : *members)
    {
      auto m = mv.first;
      // make this a pointer so we don't copy it
      // don't use mv.second since it doesn't seem to append to the vector
      auto cur_member = &((*members).at(m));
      auto current_end = cur_member->size() - 1;
      auto offset = 1;
      while (current_end < (dates_.size() - 1) && (remove_years.find(m) == remove_years.
        end()))
      {
        const auto days_left = (dates_.size() - 1) - current_end;
        const auto f = m + offset;
        // >= since leap years might be longer
        if (members->find(f) != members->end() && (*members).at(f).size() >=
          original_length)
        {
          const auto from_member = &((*members).at(f));
          for (size_t i = 0; i <
               min(days_left, min(year_length, from_member->size() - 1)); ++i)
          {
            const auto wx = (*from_member).at(i);
            // need to fix date but copy everything else
            cur_member->emplace_back(wx);
          }
        }
        else
        {
          // need to remove this year from everything because it goes too far
          const auto now = date_by_offset(0);
          const int cur_year = now.year;
          for (auto i = m; i <= min(f, cur_year - 1); ++i)
          {
            remove_years.emplace(i, true);
          }
        }
        current_end = cur_member->size() - 1;
        offset++;
      }
      assert(cur_member->size() <= dates_.size());
    }
    for (const auto& r : remove_years)
    {
      // get rid of all members that can't go far enough for the projection we asked for
      auto i = r.first;
      members->erase(i);
    }
  }
  for (auto y : years)
  {
    for (auto& kv : hindcasts)
    {
      auto h = kv.second;
      const auto& seek = h.find(y);
      logging::check_fatal(seek == h.end(),
                           "Hindcast %s missing year %d",
                           kv.first.name().c_str(),
                           y);
    }
  }
}
FwiStream WxShield::processMember(Startup* startup,
                                  const double latitude,
                                  const vector<Weather> cur_member) const
{
  return FwiStream(dates_, startup, latitude, cur_member);
}
template <class M, class V>
size_t find_min_bounds(map<WeatherModel, map<M, vector<V>>, ModelCompare> models)
{
  auto min_val = numeric_limits<size_t>::max();
  for (const auto& kv : models)
  {
    const WeatherModel& m = kv.first;
    if (m.name() != L"AFFES")
    {
      for (const auto& member : kv.second)
      {
        min_val = min(min_val, member.second.size());
      }
    }
  }
  return min_val;
}
/**
 * \brief Formats a double to output with a certain number of decimal places.
 */
class DecimalFormatter
{
  // this exists so that we can output a maximum number of places after the
  // decimal place but not if it's 0
public:
  ~DecimalFormatter() = default;
  DecimalFormatter(const DecimalFormatter& rhs) = delete;
  DecimalFormatter(DecimalFormatter&& rhs) = delete;
  DecimalFormatter& operator=(const DecimalFormatter& rhs) = delete;
  DecimalFormatter& operator=(DecimalFormatter&& rhs) = delete;
  /**
   * \brief Constructor
   * \param value Value to be formatted
   * \param after_decimal Number of digits to display after decimal place
   */
  DecimalFormatter(const double value, const int after_decimal) noexcept
    : value(value), after_decimal(after_decimal)
  {
  }
  /**
   * \brief Value to be formatted
   */
  const double value;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Number of digits to display after decimal place
   */
  const int after_decimal;
};
#pragma warning (pop)
ostream& operator<<(ostream& os, const DecimalFormatter& df)
{
  ostringstream ss{};
  // let this figure out how the number should be rounded
  ss << fixed << setprecision(df.after_decimal) << df.value;
  auto s = ss.str();
  // remove trailing 0's
  while (s.at(s.size() - 1) == '0')
  {
    s = s.substr(0, s.size() - 1);
  }
  // if last character is the decimal the remove it
  if (s.at(s.size() - 1) == '.')
  {
    s = s.substr(0, s.size() - 1);
  }
  os << s;
  return os;
}
ostream& operator<<(ostream& os, const FwiWeather& w)
{
  os << DecimalFormatter(w.apcp().asDouble(), 1) << ","
    << DecimalFormatter(w.tmp().asDouble(), 1) << ","
    << DecimalFormatter(w.rh().asDouble(), 1) << ","
    << DecimalFormatter(w.wind().speed().asDouble(), 1) << ","
    << DecimalFormatter(w.wind().direction().asDegrees(), 1) << ","
    << DecimalFormatter(w.ffmc().asDouble(), 1) << ","
    << DecimalFormatter(w.dmc().asDouble(), 1) << ","
    << DecimalFormatter(w.dc().asDouble(), 1) << ","
    << DecimalFormatter(w.isi().asDouble(), 1) << ","
    << DecimalFormatter(w.bui().asDouble(), 1) << ","
    << DecimalFormatter(w.fwi().asDouble(), 1);
  return os;
}
// HACK: was getting a not found error
[[nodiscard]] ostream& operator<<(ostream& os, const wstring& s)
{
  return util::operator<<(os, s);
}
ostream& operator<<(ostream& os,
                    const tuple<wstring, FwiStream, vector<TIMESTAMP_STRUCT>>&
                    member)
{
  for (size_t d = 0; d < get<1>(member).wx().size(); ++d)
  {
    const auto w = get<1>(member).wx().at(d);
    const auto for_time = get<2>(member).at(d);
    os << get<0>(member) << ","
      << for_time << ","
      << w
      << endl;
  }
  return os;
}
void WxShield::processEnsembles(const vector<Weather>& actuals,
                                ModelMap& hindcasts,
                                ModelMap& forecasts,
                                vector<int>& years,
                                const size_t end_of_ensemble)
{
  map<wstring, FwiStream> scenarios{};
  map<wstring, FwiStream> reanalysis{};
  // HACK: override the APCP_0800 since the actuals are already counting the whole day
  const auto actuals_startup = nullptr == startup_
                                 ? nullptr
                                 : make_unique<Startup>(startup_->station(),
                                                        startup_->generated(),
                                                        startup_->point(),
                                                        startup_->distanceFrom(),
                                                        startup_->ffmc(),
                                                        startup_->dmc(),
                                                        startup_->dc(),
                                                        AccumulatedPrecipitation::Zero,
                                                        startup_->isOverridden());
  auto fix_actuals = processMember(&(*actuals_startup), point_.latitude(), actuals);
  // find AFFES forecast
  const vector<Weather>* affes = nullptr;
  size_t affes_days = 0;
  for (const auto& kv : forecasts)
  {
    const auto model = kv.first;
    if (model.name() == L"AFFES")
    {
      logging::check_fatal(kv.second.size() != 1,
                           "There should only be one AFFES forecast");
      affes = &kv.second.at(0);
      affes_days = affes->size();
      break;
    }
  }
  wstring first;
  auto i = 0;
  // vector<vector<Weather*>> affes_members;
  // static const auto EnsembleMembers = 42;
  // affes_members.reserve(EnsembleMembers * years_.size() * affes_days);
  for (const auto& kv : forecasts)
  {
    const auto model = kv.first;
    if (model.name() == L"AFFES")
    {
      continue;
    }
    auto members = kv.second;
    for (const auto& mkv : members)
    {
      const auto member_id = mkv.first;
      auto member = mkv.second;
      for (const auto& hkv : hindcasts)
      {
        auto hindcast = hkv.second;
        for (const auto& year : years)
        {
          auto h = &hindcast.at(year);
          const auto count = min(h->size() - end_of_ensemble,
                                 dates_.size() - member.size());
          vector<Weather> m{member.size() + count};
          m.reserve(dates_.size());
          std::copy(member.begin(), member.end(), m.begin());
          std::copy_n(h->begin() + static_cast<__int64>(end_of_ensemble),
                      static_cast<__int64>(count),
                      m.begin() + static_cast<__int64>(member.size()));
          const auto mem_id = L"0" + to_wstring(member_id);
          const auto fake_name = model.name() + L"x" + to_wstring(year) + L"x"
            + mem_id.substr(mem_id.size() - 2);
          scenarios.emplace(fake_name, processMember(&(*startup_), point_.latitude(), m));
          if (first.empty())
          {
            // we know that scenario 0 should be first
            first = fake_name;
          }
          ++i;
          // add in AFFES versions of this member
          // for (size_t cur_days = 1; cur_days <= affes_days; ++cur_days)
          if (0 < affes_days)
          {
            vector<Weather> affes_m{m.size()};
            std::copy(m.begin(), m.end(), affes_m.begin());
            // copy over the first j days with the AFFES forecast
            // std::copy_n(affes->begin(), cur_days, affes_m.begin());
            std::copy_n(affes->begin(), affes_days, affes_m.begin());
            // ReSharper disable once StringLiteralTypo
            const auto affes_fake_name = L"AFFESX" + model.name() + L"x" +
              to_wstring(year) + L"x"
              + mem_id.substr(mem_id.size() - 2);
            scenarios.emplace(affes_fake_name,
                              processMember(&(*startup_), point_.latitude(), affes_m));
          }
        }
      }
    }
  }
  if (full_wx_)
  {
    for (const auto& hkv : hindcasts)
    {
      auto hindcast = hkv.second;
      auto min_year = numeric_limits<int>::max();
      auto max_year = numeric_limits<int>::min();
      for (const auto& ykv : hindcast)
      {
        const auto year = ykv.first;
        min_year = min(min_year, year);
        max_year = max(max_year, year);
      }
      for (auto year = min_year; year <= max_year; ++year)
      {
        auto h = &hindcast.at(year);
        const auto count = dates_.size();
        vector<Weather> m{count};
        m.reserve(dates_.size());
        std::copy_n(h->begin(), static_cast<__int64>(count), m.begin());
        reanalysis.emplace(to_wstring(year),
                           processMember(&(*startup_), point_.latitude(), m));
      }
    }
  }
  static const auto IndicesHeader =
    "Scenario,Date,APCP,TMP,RH,WS,WD,FFMC,DMC,DC,ISI,BUI,FWI";
  if (nullptr != affes)
  {
    // do this so we know the scenario was processed and indices calculated
    for (const auto& s : scenarios)
    {
      auto k = s.first;
      if (0 == k.find(L"AFFES"))
      {
        auto v = s.second;
        FwiVector wx{affes_days};
        vector<TIMESTAMP_STRUCT> dates{affes_days};
        // find first scenario that used the AFFES forecast
        for (size_t d = 0; d < affes_days; ++d)
        {
          wx.at(d) = v.wx().at(d);
          dates.at(d) = dates_.at(d);
        }
        const string tmp;
        stringstream iss(tmp);
        logging::note("AFFES indices are:");
        iss << IndicesHeader << endl;
        const FwiStream fwi_wx(std::move(wx));
        iss << make_tuple(L"AFFES", fwi_wx, dates);
        cout << iss.str();
        break;
      }
    }
  }
  logging::info("Saving to %s", save_to_.c_str());
  ofstream out;
  out.open(save_to_);
  out << IndicesHeader << endl;
  out << make_tuple(L"actual", fix_actuals, dates_);
  i = 0;
  for (const auto& kv : scenarios)
  {
    out << make_tuple(to_wstring(--i), kv.second, dates_);
  }
  if (!reanalysis.empty())
  {
    auto min_year = numeric_limits<int>::max();
    auto max_year = numeric_limits<int>::min();
    for (const auto& ykv : reanalysis)
    {
      const auto year = ykv.first;
      min_year = min(min_year, stoi(year));
      max_year = max(max_year, stoi(year));
    }
    for (auto year = min_year; year <= max_year; ++year)
    {
      const auto y = to_wstring(year);
      out << make_tuple(y, reanalysis.at(y), dates_);
    }
  }
  out.close();
}
static vector<int> find_years(const int offset)
{
  vector<int> years{};
  auto scores = WxShield::readScoreByOffset(offset);
  double sum_grade = 0;
  const auto target = sim::Settings::maxGrade();
  logging::note("Target score is %f", target);
  for (const auto& s : scores)
  {
    if (sum_grade >= target)
    {
      break;
    }
    sum_grade += s.grade();
    years.push_back(s.year());
  }
  // HACK: sort now so that output order is the same as wxshield csv
  sort(years.begin(), years.end());
  return years;
}
static vector<TIMESTAMP_STRUCT> make_dates(const int offset, const size_t num_days)
{
  vector<TIMESTAMP_STRUCT> dates{num_days};
  // HACK: assume all dates are sequential and continuous from startDate
  for (size_t i = 0; i < num_days; ++i)
  {
    dates.at(i) = date_by_offset(offset + i);
  }
  return dates;
}
static const Startup STARTUP_ZERO(L"INVALID",
                                  TIMESTAMP_STRUCT{},
                                  topo::Point{0, 0},
                                  0.0,
                                  Ffmc::Zero,
                                  Dmc::Zero,
                                  Dc::Zero,
                                  AccumulatedPrecipitation::Zero,
                                  false);
static unique_ptr<Startup> override_startup(const topo::Point& point,
                                            unique_ptr<Startup> startup,
                                            const Ffmc* const ffmc,
                                            const Dmc* const dmc,
                                            const Dc* const dc,
                                            const AccumulatedPrecipitation* const
                                            apcp_0800)
{
  // if no overrides then just use original
  if (nullptr == ffmc && nullptr == dmc && nullptr == dc && nullptr == apcp_0800)
  {
    return startup;
  }
  const auto& base = (nullptr == startup) ? STARTUP_ZERO : *startup;
  return make_unique<Startup>(Startup(L"N/A",
                                      {},
                                      (nullptr == startup) ? point : base.point(),
                                      0.0,
                                      (nullptr == ffmc) ? base.ffmc() : *ffmc,
                                      (nullptr == dmc) ? base.dmc() : *dmc,
                                      (nullptr == dc) ? base.dc() : *dc,
                                      (nullptr == apcp_0800)
                                        ? base.apcp0800()
                                        : *apcp_0800,
                                      true));
}
WxShield::WxShield(const TIMESTAMP_STRUCT& start_date,
                   const topo::Point& point,
                   const size_t num_days,
                   string save_to,
                   const int offset,
                   vector<int>&& years,
                   Ffmc* ffmc,
                   Dmc* dmc,
                   Dc* dc,
                   AccumulatedPrecipitation* apcp_0800,
                   const bool full_wx)
  : dates_(make_dates(offset, num_days)),
    point_(point),
    start_date_(start_date),
    save_to_(std::move(save_to)),
    startup_(override_startup(point,
                              readStartupByOffset(point, start_date, offset),
                              ffmc,
                              dmc,
                              dc,
                              apcp_0800)),
    offset_(offset),
    full_wx_(full_wx)
{
  auto hindcasts = readHindcastByOffset(point, offset, num_days);
  auto forecasts = readForecastByOffset(point, start_date, offset, num_days);
  const auto actuals = readActualsByOffset(point, start_date, offset, num_days);
  logging::note("Initialized WxShield with date %s", to_string(start_date).c_str());
  if (find_min_bounds(hindcasts) != num_days)
  {
    logging::info(
      "More dates requested than returned - will need to splice years together");
  }
  const auto end_of_ensemble = find_min_bounds(forecasts);
  logging::debug("End of ensembles is %d", end_of_ensemble);
  if (nullptr == startup_)
  {
    logging::note("No valid startup indices found for %s",
                  to_string(date_by_offset(offset - 1)).c_str());
  }
  else
  {
    if (startup_->isOverridden())
    {
      logging::note(
        "Startup indices were overridden to be"
        " (%0.1fmm, FFMC %0.1f, DMC %0.1f, DC %0.1f)",
        startup_->apcp0800(),
        startup_->ffmc(),
        startup_->dmc(),
        startup_->dc());
    }
    else
    {
      logging::note(
        "Startup indices are (%S, %04d-%02d-%02d, "
        "%0.1fmm, FFMC %0.1f, DMC %0.1f, DC %0.1f)",
        startup_->station().c_str(),
        startup_->generated().year,
        startup_->generated().month,
        startup_->generated().day,
        startup_->apcp0800(),
        startup_->ffmc(),
        startup_->dmc(),
        startup_->dc());
    }
    // const auto yesterday = readYesterday();
    // check_fatal(startup_->ffmc != yesterday->ffmc()
    //             || startup_->dmc != yesterday->dmc()
    //             || startup_->dc != yesterday->dc(),
    //             "Indices (%.2f, %.2f, %.2f) don't match (%.2f, %.2f, %.2f)",
    //             startup_->ffmc, startup_->dmc, startup_->dc, yesterday->ffmc(),
    //             yesterday->dmc(), yesterday->dc());
    // delete yesterday;
  }
  preProcessEnsembles(hindcasts, years);
  // HACK: if not going beyond ensembles then remove all but one year
  if (num_days - 1 <= end_of_ensemble)
  {
    years.erase(years.begin() + 1, years.end());
  }
  processEnsembles(actuals, hindcasts, forecasts, years, end_of_ensemble);
}
WxShield::WxShield(const TIMESTAMP_STRUCT& start_date,
                   const topo::Point& point,
                   const size_t num_days,
                   const string& save_to,
                   const int offset,
                   Ffmc* ffmc,
                   Dmc* dmc,
                   Dc* dc,
                   AccumulatedPrecipitation* apcp_0800,
                   const bool full_wx)
  : WxShield(start_date,
             point,
             num_days,
             save_to,
             offset,
             find_years(offset),
             ffmc,
             dmc,
             dc,
             apcp_0800,
             full_wx)
{
}
WxShield::WxShield(const TIMESTAMP_STRUCT& start_date,
                   const topo::Point& point,
                   const size_t num_days,
                   const string& save_to,
                   Ffmc* ffmc,
                   Dmc* dmc,
                   Dc* dc,
                   AccumulatedPrecipitation* apcp_0800,
                   const bool full_wx)
  : WxShield(start_date,
             point,
             num_days,
             save_to,
             offset_by_date(start_date),
             ffmc,
             dmc,
             dc,
             apcp_0800,
             full_wx)
{
}
WxShield::WxShield(const WxShield& rhs)
  : dates_(rhs.dates_),
    point_(rhs.point_),
    start_date_(rhs.start_date_),
    save_to_(rhs.save_to_),
    //end_of_ensemble_(rhs.end_of_ensemble_),
    startup_(make_unique<Startup>(*rhs.startup_)),
    offset_(rhs.offset_),
    full_wx_(rhs.full_wx_)
{
}
}
}
