#pragma once

#include "cal_compiler.h"

#ifdef CAL_MSVC

#define PUSH_OPTIONS
#define POP_OPTIONS

#define NO_OPTIMIZE DO_PRAGMA(optimize("", off))
#define OPTIMIZE DO_PRAGMA(optimize("", on))

#else

#define PUSH_OPTIONS DO_PRAGMA(GCC push_options)
#define POP_OPTIONS DO_PRAGMA(GCC pop_options)

#define NO_OPTMIZE DO_PRAGMA(GCC optimize ("O0"))
#define OPTMIZE DO_PRAGMA(GCC optimize ("O2"))

#endif
