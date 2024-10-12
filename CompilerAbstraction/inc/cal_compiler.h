#pragma once

#define DO_PRAGMA(x) _Pragma(#x)

#if defined(_MSC_VER)

#define CAL_MSVC

#elif defined(__GNUC__)

#define CAL_GNU

#endif

