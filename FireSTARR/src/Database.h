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
#include <map>
#include <vector>
#include "Log.h"
#include "Util.h"
namespace firestarr
{
namespace wx
{
struct ModelCompare;
class Weather;
class WeatherModel;
}
namespace util
{
/**
 * \brief Provides access to a database with the ability to read objects using queries.
 */
class Database
{
public:
  /**
   * \brief Create a Database for the given Data Source Name
   * \param dsn Data Source Name to use
   */
  explicit Database(const wstring& dsn);
  ~Database();
  /**
   * \brief Move constructor
   * \param rhs Database to move from
   */
  Database(Database&& rhs) noexcept = default;
  /**
   * \brief Copy constructor
   * \param rhs Database to copy from
   */
  Database(const Database& rhs) = default;
  /**
   * \brief Move assignment
   * \param rhs Database to move from
   * \return This, after assignment
   */
  Database& operator=(Database&& rhs) noexcept = default;
  /**
   * \brief Copy assignment
   * \param rhs Databse to copy from
   * \return This, after assignment
   */
  Database& operator=(const Database& rhs) = default;
  /**
   * \brief Read a double from the current column of the current query
   * \return double from the current column of the current query
   */
  [[nodiscard]] double getDouble() noexcept;
  /**
   * \brief Read a double form the current column of the current query
   * \tparam N Precision to round value that is read to
   * \return double from the current column of the current query
   */
  template <unsigned int N>
  [[nodiscard]] double getDouble() noexcept
  {
    // HACK: database access from website does this rounding, so we need to match it
    return round_to_precision<N>(getDouble());
  }
  /**
   * \brief Read an int from the current column of the current query
   * \return int from the current column of the current query
   */
  [[nodiscard]] int getInteger() noexcept;
  /**
   * \brief Read a TIMESTAMP_STRUCT from the current column of the current query
   * \return TIMESTAMP_STRUCT from the current column of the current query
   */
  [[nodiscard]] TIMESTAMP_STRUCT getTimestamp() noexcept;
  /**
   * \brief Read a wstring from the current column of the current query
   * \return wstring from the current column of the current query
   */
  [[nodiscard]] wstring getString() noexcept;
  /**
   * \brief Check if the result is an error and output message if so
   * \param result RETCODE to check for error status 
   * \param format Message to output on error
   * \param ... Arguments for formatting message
   * \return None
   */
  static void checkError(RETCODE result, const char* format, ...) noexcept;
  /**
   * \brief Read a T from the current column of the current query
   * \tparam T type to return
   * \param sql_type SQLSMALLINT representing type to return
   * \return T from the current column of the current query
   */
  template <class T>
  [[nodiscard]] T getValue(const SQLSMALLINT sql_type) noexcept
  {
    T value{};
    getValue(&value, sql_type, 0);
    return value;
  }
  /**
   * \brief Read an array of T from the current column of the current query
   * \tparam T type to return
   * \param value array of T to read into
   * \param sql_type SQLSMALLINT representing type to return
   * \param buffer_length Maximum length of array of T to read into
   */
  template <class T>
  void getValue(T* value, const SQLSMALLINT sql_type, const SQLLEN buffer_length) noexcept
  {
    SQLLEN cb;
    checkError(SQLGetData(h_stmt_, cur_column_, sql_type, value, buffer_length, &cb),
               "Can't read column %d as type '%s'",
               cur_column_,
               typeid(T).name());
    cur_column_++;
  }
  /**
   * \brief Read a vector of T based on performing the given query
   * \tparam T type to be returned
   * \param query Query to perform that returns a series of rows that each represent a T
   * \return vector of T based on performing the given query
   */
  template <class T>
  [[nodiscard]] vector<T> readList(wstring query)
  {
    SQLSMALLINT num_results;
    logging::check_fatal(SQLExecDirect(h_stmt_, &query[0], SQL_NTS) != SQL_SUCCESS,
                         "Could not read from database");
    SQLNumResultCols(h_stmt_, &num_results);
    assert(num_results > 0);
    vector<T> results{};
    results.reserve(static_cast<size_t>(num_results));
    auto ret_code = SQLFetch(h_stmt_);
    while (ret_code != SQL_NO_DATA_FOUND)
    {
      cur_column_ = 1;
      results.emplace_back(this);
      ret_code = SQLFetch(h_stmt_);
    }
    SQLFreeStmt(h_stmt_, SQL_CLOSE);
    return results;
  }
  /**
   * \brief Read a map of WeatherModels to maps of days to Weather
   * \param query Query to run
   * \return 
   */
  [[nodiscard]] map<wx::WeatherModel, map<int, vector<wx::Weather>>, wx::ModelCompare>
  readModel(wstring query);
private:
  /**
   * \brief Handle to environment
   */
  SQLHENV h_env_ = nullptr;
  /**
   * \brief Handle to database
   */
  SQLHDBC h_dbc_ = nullptr;
  /**
   * \brief Handle to statement that was executed
   */
  SQLHSTMT h_stmt_ = nullptr;
  /**
   * \brief Connection string for accessing database
   */
  wstring connection_;
#pragma warning (push)
#pragma warning (disable: 4820)
  /**
   * \brief Current column to read from query results
   */
  SQLUSMALLINT cur_column_ = 0;
};
#pragma warning (pop)
}
}
