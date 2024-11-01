#pragma once

#define DO_PRAGMA(x) _Pragma(#x)

#if defined(_MSC_VER)

#define CAL_MSVC

#ifdef _M_AMD64
#define CAL_X86_64
#endif

#elif defined(__GNUC__)

#define CAL_GNU

#ifdef __x86_64__
#define CAL_X86_64
#endif

#endif

