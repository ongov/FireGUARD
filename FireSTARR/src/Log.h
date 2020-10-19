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
namespace firestarr
{
namespace logging
{
static const int LOG_EXTENSIVE = 0;
static const int LOG_VERBOSE = 1;
static const int LOG_DEBUG = 2;
static const int LOG_INFO = 3;
static const int LOG_NOTE = 4;
static const int LOG_WARNING = 5;
static const int LOG_ERROR = 6;
static const int LOG_FATAL = 7;
static const int LOG_SILENT = 8;
/**
 * \brief Provides logging functionality.
 */
class Log
{
  /**
   * \brief Current logging level
   */
  static int logging_level_;
public:
  /**
   * \brief Output a message to the log
   * \param name Name of logging level to mark message with
   * \param format Format string for message
   * \param args Arguments to use in format string
   * \return None
   */
  static void output(const char* name, const char* format, va_list* args) noexcept;
  /**
   * \brief Set logging level to a specific level
   * \param log_level Log level to use
   * \return None
   */
  static void setLogLevel(int log_level) noexcept;
  /**
   * \brief Increase amount of logging output by one level
   * \return None
   */
  static void increaseLogLevel() noexcept;
  /**
   * \brief Decrease amount of logging output by one level
   * \return None
   */
  static void decreaseLogLevel() noexcept;
  /**
   * \brief Get current logging level
   * \return Current logging level
   */
  static int getLogLevel() noexcept;
};
/**
 * \brief Log with EXTENSIVE level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void extensive(const char* format, ...) noexcept;
/**
 * \brief Log with VERBOSE level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void verbose(const char* format, ...) noexcept;
/**
 * \brief Log with DEBUG level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void debug(const char* format, ...) noexcept;
/**
 * \brief Log with INFO level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void info(const char* format, ...) noexcept;
/**
 * \brief Log with NOTE level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void note(const char* format, ...) noexcept;
/**
 * \brief Log with WARNING level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void warning(const char* format, ...) noexcept;
/**
 * \brief Log with ERROR level
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void error(const char* format, ...) noexcept;
/**
 * \brief Check condition and log and exit if true
 * \param condition Condition to check (true ends program after logging)
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void check_fatal(bool condition, const char* format, ...) noexcept;
/**
 * \brief Log with FATAL level and exit
 * \param format Format string for message
 * \param ... Arguments to format message with
 */
void fatal(const char* format, ...) noexcept;
// templated so we can return it from any function and not get an error
// about not returning on all paths
/**
 * \brief Log a fatal error and quit
 * \tparam T Type to return (so that it can be used to avoid no return value warning)
 * \param format Format string for message
 * \param args Arguments to format message with
 * \return Nothing, because this ends the program
 */
template <class T>
T fatal(const char* format, va_list* args) noexcept
{
  Log::output("FATAL: ", format, args);
  exit(EXIT_FAILURE);
}
/**
 * \brief Log a fatal error and quit
 * \tparam T Type to return (so that it can be used to avoid no return value warning)
 * \param format Format string for message
 * \param ... Arguments to format message with
 * \return Nothing, because this ends the program
 */
template <class T>
T fatal(const char* format, ...) noexcept
{
  va_list args;
  va_start(args, format);
  // cppcheck-suppress va_end_missing
  return fatal<T>(format, &args);
  //  va_end(args);
}
}
}
