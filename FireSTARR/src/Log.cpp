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
#include "Log.h"
namespace firestarr::logging
{
int Log::logging_level_ = LOG_DEBUG;
void Log::setLogLevel(const int log_level) noexcept
{
  logging_level_ = log_level;
}
void Log::increaseLogLevel() noexcept
{
  // HACK: make sure we never go below 0
  logging_level_ = max(0, getLogLevel() - 1);
}
void Log::decreaseLogLevel() noexcept
{
  // HACK: make sure we never go above silent
  logging_level_ = min(LOG_SILENT, getLogLevel() + 1);
}
int Log::getLogLevel() noexcept
{
  return logging_level_;
}
#pragma warning (push)
#pragma warning (disable: 26447)
void Log::output(const char* name, const char* format, va_list* args) noexcept
{
  try
  {
    const auto now = time(nullptr);
    tm buf{};
    localtime_s(&buf, &now);
    // NOTE: create string first so that entire line writes
    // (otherwise threads might mix lines)
    const string tmp;
    stringstream iss(tmp);
    iss << put_time(&buf, "[%F %T] ") << name;
    static char buffer[1024]{0};
    vsprintf_s(buffer, 1024, format, *args);
    iss << buffer << "\n";
    cout << iss.str();
  }
  catch (...)
  {
    std::terminate();
  }
}
#pragma warning (pop)
void extensive(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_EXTENSIVE)
  {
    va_list args;
    va_start(args, format);
    Log::output("EXTENSIVE:", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void verbose(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_VERBOSE)
  {
    va_list args;
    va_start(args, format);
    Log::output("VERBOSE:", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void debug(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_DEBUG)
  {
    va_list args;
    va_start(args, format);
    Log::output("DEBUG: ", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void info(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_INFO)
  {
    va_list args;
    va_start(args, format);
    Log::output("INFO:  ", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void note(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_NOTE)
  {
    va_list args;
    va_start(args, format);
    Log::output("NOTE:  ", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void warning(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_WARNING)
  {
    va_list args;
    va_start(args, format);
    Log::output("WARN:  ", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void error(const char* format, ...) noexcept
{
  if (Log::getLogLevel() <= LOG_ERROR)
  {
    va_list args;
    va_start(args, format);
    Log::output("ERROR: ", format, &args);
#pragma warning (push)
#pragma warning (disable: 26477)
    va_end(args);
#pragma warning (pop)
  }
}
void fatal(const char* format, va_list* args) noexcept
{
  // HACK: call the other version
  fatal<int>(format, args);
}
void fatal(const char* format, ...) noexcept
{
  va_list args;
  va_start(args, format);
  fatal(format, &args);
  // cppcheck-suppress va_end_missing
  // va_end(args);
}
void check_fatal(const bool condition, const char* format, va_list* args) noexcept
{
  if (condition)
  {
    fatal(format, args);
  }
}
void check_fatal(const bool condition, const char* format, ...) noexcept
{
  if (condition)
  {
    va_list args;
    va_start(args, format);
    fatal(format, &args);
    // cppcheck-suppress va_end_missing
    // va_end(args);
  }
}
}
