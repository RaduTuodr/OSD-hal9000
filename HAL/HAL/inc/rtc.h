#pragma once

#include "cal_annotate.h"

void
RtcInit(
    OUT_OPT     QWORD*          TscFrequency
    );

void
RtcAcknowledgeTimerInterrupt(
    void
    );

ALWAYS_INLINE
QWORD
RtcGetTickCount(
    void
    )
{
    _mm_lfence();
    return __rdtsc();
}