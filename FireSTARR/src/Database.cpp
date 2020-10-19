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
#include "Database.h"
#include "Weather.h"
#include "WeatherModel.h"
namespace firestarr::util
{
double Database::getDouble() noexcept
{
  return static_cast<double>(getValue<SQLDOUBLE>(SQL_DOUBLE));
}
int Database::getInteger() noexcept
{
  return static_cast<int>(getValue<SQLINTEGER>(SQL_INTEGER));
}
TIMESTAMP_STRUCT Database::getTimestamp() noexcept
{
  return getValue<TIMESTAMP_STRUCT>(SQL_C_TIMESTAMP);
}
#pragma warning (push)
#pragma warning (disable: 26447)
wstring Database::getString() noexcept
{
  try
  {
    SQLLEN cch_display;
    checkError(SQLColAttribute(h_stmt_,
                               cur_column_,
                               SQL_DESC_DISPLAY_SIZE,
                               nullptr,
                               0,
                               nullptr,
                               &cch_display),
               "Cannot determine size of column %d",
               cur_column_);
    const auto value = new WCHAR[static_cast<size_t>(cch_display) + 1]{0};
    getValue<void>(value,
                   SQL_C_TCHAR,
                   (cch_display + 1) * static_cast<SQLLEN>(sizeof(WCHAR)));
    auto result = wstring(value);
    delete[] value;
    return result;
  }
  catch (...)
  {
    std::terminate();
  }
}
#pragma warning (pop)
void Database::checkError(const RETCODE result, const char* format, ...) noexcept
{
  va_list args;
  va_start(args, format);
  logging::check_fatal(SQL_ERROR == result, format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
  va_end(args);
#pragma warning (pop)
}
map<wx::WeatherModel, map<int, vector<wx::Weather>>, wx::ModelCompare>
Database::readModel(wstring query)
{
  SQLSMALLINT num_results;
  logging::check_fatal(SQLExecDirect(h_stmt_, &query[0], SQL_NTS) != SQL_SUCCESS,
                       "Could not read from database");
  SQLNumResultCols(h_stmt_, &num_results);
  assert(num_results > 0);
  map<wx::WeatherModel, map<int, vector<wx::Weather>>, wx::ModelCompare> results{};
  auto ret_code = SQLFetch(h_stmt_);
  while (ret_code != SQL_NO_DATA_FOUND)
  {
    cur_column_ = 1;
    auto k = wx::WeatherModel(this);
    const auto fk = results.find(k);
    if (fk == results.end())
    {
      static const map<int, vector<wx::Weather>> EmptyMap{};
      results.emplace(k, EmptyMap);
    }
    else
    {
      k = fk->first;
    }
    auto m = stoi(getString());
    if (results.at(k).find(m) == results.at(k).end())
    {
      results.at(k).emplace(m, vector<wx::Weather>());
    }
    results.at(k).at(m).emplace_back(this);
    ret_code = SQLFetch(h_stmt_);
  }
  SQLFreeStmt(h_stmt_, SQL_CLOSE);
  return results;
}
Database::Database(const wstring& dsn)
// ReSharper disable StringLiteralTypo
  : connection_(
    wstring(L"DSN=HINDCAST;DATABASE=" + dsn + L";UID=wx_readonly;PWD=wx_r34d0nly!;"))
// ReSharper restore StringLiteralTypo
{
  checkError(SQLAllocHandle(SQL_HANDLE_ENV, nullptr, &h_env_),
             "Unable to allocate handle for environment");
  // Register this as an application that expects 3.x behaviour,
  // you must register something if you use SQLAllocHandle
#pragma warning(push)
#pragma warning (disable: 26490)
  checkError(SQLSetEnvAttr(h_env_,
                           SQL_ATTR_ODBC_VERSION,
                           reinterpret_cast<SQLPOINTER>(SQL_OV_ODBC3),
                           0),
             "Unable to set version");
#pragma warning (pop)
  // Allocate a connection
  checkError(SQLAllocHandle(SQL_HANDLE_DBC, h_env_, &h_dbc_),
             "Unable to allocate handle for database");
  auto err = widestring_to_string(dsn);
  // HACK: checkError doesn't seem to work with err being converted from widestring
  logging::check_fatal(SQL_ERROR == SQLDriverConnect(h_dbc_,
                                                     nullptr,
                                                     &connection_[0],
                                                     SQL_NTS,
                                                     nullptr,
                                                     0,
                                                     nullptr,
                                                     SQL_DRIVER_COMPLETE),
                                                     "Unable to open connection to database '%s'",
                                                     err.c_str());
  checkError(SQLAllocHandle(SQL_HANDLE_STMT, h_dbc_, &h_stmt_),
             "Unable to allocate handle for statement");
}
Database::~Database()
{
  if (h_stmt_)
  {
    SQLFreeHandle(SQL_HANDLE_STMT, h_stmt_);
  }
  if (h_dbc_)
  {
    SQLDisconnect(h_dbc_);
    SQLFreeHandle(SQL_HANDLE_DBC, h_dbc_);
  }
  if (h_env_)
  {
    SQLFreeHandle(SQL_HANDLE_ENV, h_env_);
  }
}
}
