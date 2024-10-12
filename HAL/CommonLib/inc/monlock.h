#pragma once

C_HEADER_START

#include "cal_warning.h"

#define MONITOR_FILTER_SIZE     64

#pragma pack(push,16)
WARNING_PUSH

// warning C4201: nonstandard extension used: nameless struct/union
MSVC_WARNING_DISABLE(4201)
typedef struct _MONITOR_LOCK
{
    union
    {
        SPINLOCK                Lock;
        volatile BYTE           Reserved[MONITOR_FILTER_SIZE];
    };
} MONITOR_LOCK, *PMONITOR_LOCK;

WARNING_POP
#pragma pack(pop)

void
MonitorLockInit(
    OUT         PMONITOR_LOCK       Lock
    );

void
MonitorLockAcquire(
    INOUT       PMONITOR_LOCK       Lock,
    OUT         INTR_STATE*         IntrState
    );

BOOL_SUCCESS
BOOLEAN
MonitorLockTryAcquire(
    INOUT       PMONITOR_LOCK       Lock,
    OUT         INTR_STATE*         IntrState
    );

BOOLEAN
MonitorLockIsOwner(
    IN          PMONITOR_LOCK       Lock
    );

void
MonitorLockRelease(
    INOUT       PMONITOR_LOCK       Lock,
    IN          INTR_STATE          OldIntrState
    );
C_HEADER_END
