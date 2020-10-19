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
#include "Util.h"
#include "Log.h"
namespace firestarr
{
namespace util
{
//https://codereview.stackexchange.com/questions/419/converting-between-stdwstring-and-stdstring
wstring string_to_widestring(const string& s)
{
  const auto string_length = static_cast<int>(s.length()) + 1;
  const auto len = MultiByteToWideChar(CP_ACP, 0, s.c_str(), string_length, nullptr, 0);
  const auto buf = new wchar_t[static_cast<size_t>(len)];
  MultiByteToWideChar(CP_ACP, 0, s.c_str(), string_length, buf, len);
  wstring r(buf);
  delete[] buf;
  return r;
}
string widestring_to_string(const wstring& s)
{
  const auto string_length = static_cast<int>(s.length()) + 1;
  const auto len = WideCharToMultiByte(CP_ACP,
                                       0,
                                       s.c_str(),
                                       string_length,
                                       nullptr,
                                       0,
                                       nullptr,
                                       nullptr);
  const auto buf = new char[static_cast<size_t>(len)];
  WideCharToMultiByte(CP_ACP, 0, s.c_str(), string_length, buf, len, nullptr, nullptr);
  string r(buf);
  delete[] buf;
  return r;
}
ostream& operator<<(ostream& os, const wstring& s)
{
  os << widestring_to_string(s);
  return os;
}
void read_directory(const wstring& name, vector<string>* v, const wstring& match)
{
  auto pattern(name);
  pattern.append(match);
  WIN32_FIND_DATA data;
  HANDLE h_find;
  if ((h_find = FindFirstFile(pattern.c_str(), &data)) != INVALID_HANDLE_VALUE)
  {
    while (true)
    {
      v->push_back(widestring_to_string(name + wstring(data.cFileName)));
      if (0 == FindNextFile(h_find, &data))
      {
        break;
      }
    }
    FindClose(h_find);
  }
}
void read_directory(const wstring& name, vector<string>* v)
{
  read_directory(name, v, L"\\*");
}
vector<string> find_rasters(const string& dir, const int year)
{
  const auto by_year = dir + "/" + to_string(year) + "/";
  const auto raster_root = directory_exists(by_year.c_str())
                             ? by_year
                             : dir + "/default/";
  vector<string> results{};
  read_directory(string_to_widestring(raster_root), &results, L"fuel*.TIF");
  return results;
}
bool directory_exists(const char* dir) noexcept
{
  struct stat dir_info{};
  return stat(dir, &dir_info) == 0 && dir_info.st_mode & S_IFDIR;
}
void make_directory(const char* dir) noexcept
{
  if (-1 == _mkdir(dir) && errno != EEXIST)
  {
    struct stat dir_info{};
    if (stat(dir, &dir_info) != 0)
    {
      logging::fatal("Cannot create directory %s", dir);
    }
    else if (dir_info.st_mode & S_IFDIR)
    {
      // everything is fine
    }
    else
    {
      logging::fatal("%s is not a directory\n", dir);
    }
  }
}
void make_directory_recursive(const char* dir) noexcept
{
  char tmp[256];
  snprintf(tmp, sizeof tmp, "%s", dir);
  const auto len = strlen(tmp);
  if (tmp[len - 1] == '/')
    tmp[len - 1] = 0;
  for (auto p = tmp + 1; *p; ++p)
    if (*p == '/')
    {
      *p = 0;
      make_directory(tmp);
      *p = '/';
    }
  make_directory(tmp);
}
void read_date(istringstream* iss, string* str, tm* t)
{
  *t = {};
  // Date
  getline(iss, str, ',');
  string ds;
  istringstream dss(*str);
  getline(dss, ds, '-');
  t->tm_year = stoi(ds) - 1900;
  getline(dss, ds, '-');
  t->tm_mon = stoi(ds) - 1;
  getline(dss, ds, ' ');
  t->tm_mday = stoi(ds);
}
UsageCount::~UsageCount()
{
  logging::note("%s called %d times", for_what_.c_str(), count_.load());
}
UsageCount::UsageCount(string for_what) noexcept
  : count_(0), for_what_(std::move(for_what))
{
}
UsageCount& UsageCount::operator++() noexcept
{
  ++count_;
  return *this;
}
}
}
