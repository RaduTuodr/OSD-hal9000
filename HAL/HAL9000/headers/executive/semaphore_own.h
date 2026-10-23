#pragma once

#include "HAL9000.h"
#include "list.h"
#include "synch.h"

typedef struct _SEMAPHORE
{
    DWORD               Value;

    // DO NOT CHANGE THE NAMES OF THESE FIELDS
    LOCK                SemaphoreLock;

    _Guarded_by_(SemaphoreLock)
    char                Name[16];

    _Guarded_by_(SemaphoreLock)
    LIST_ENTRY          WaitingList;
    struct _THREAD*     Holder;
    
    LIST_ENTRY          AllList;
} SEMAPHORE, *PSEMAPHORE;

STATUS
SemaphoreSystemPreinit(
    void
    );

void 
SemaphoreInit(
    OUT PSEMAPHORE Semaphore,
    IN DWORD InitialValue
    );

void 
SemaphoreDown(
    INOUT PSEMAPHORE Semaphore
    );

void 
SemaphoreUp(
    INOUT PSEMAPHORE Semaphore
    );

    