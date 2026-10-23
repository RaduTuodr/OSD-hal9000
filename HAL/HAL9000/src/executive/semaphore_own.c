#include "HAL9000.h"
#include "thread_internal.h"
#include "semaphore_own.h"

typedef struct _SEMAPHORE_SYSTEM_DATA
{
    LOCK                  Lock;

    _Guarded_by_(Lock)
    LIST_ENTRY            SemaphoreList;
} SEMAPHORE_SYSTEM_DATA, *PSEMAPHORE_SYSTEM_DATA;

static SEMAPHORE_SYSTEM_DATA s_semaphoreData;

STATUS
SemaphorePreInit(
    void
    )
{
    memzero(&s_semaphoreData, sizeof(SEMAPHORE_SYSTEM_DATA));
    LockInit(&s_semaphoreData.Lock);
    LockSetName(&s_semaphoreData.Lock, "SemaphoreList");
    InitializeListHead(&s_semaphoreData.SemaphoreList);

    return STATUS_SUCCESS;
}

void 
SemaphoreInit(
    OUT PSEMAPHORE Semaphore,
    IN DWORD InitialValue
    )
{
    INTR_STATE oldState;

    ASSERT( NULL != Semaphore );

    memzero(Semaphore, sizeof(SEMAPHORE));

    LockInit(&Semaphore->SemaphoreLock);
    Semaphore->Value = InitialValue;
    InitializeListHead(&Semaphore->WaitingList);
    
    LockAcquire(&s_semaphoreData.Lock, &oldState);
    InsertTailList(&s_semaphoreData.SemaphoreList, &Semaphore->AllList);
    LockRelease(&s_semaphoreData.Lock, oldState);
}

void 
SemaphoreDown(
    INOUT PSEMAPHORE Semaphore
    )
{
    INTR_STATE oldState;
    INTR_STATE dummyState;
    PTHREAD pCurrentThread = GetCurrentThread();
    
    ASSERT(NULL != Semaphore);
    ASSERT(NULL != pCurrentThread);
    
    oldState = CpuIntrDisable();
    LockAcquire(&Semaphore->SemaphoreLock, &dummyState);

    while (Semaphore->Value == 0)
    {
        InsertTailList(&Semaphore->WaitingList, &pCurrentThread->ReadyList);
        ThreadTakeBlockLock();
        LockRelease(&Semaphore->SemaphoreLock, dummyState);
        ThreadBlock();
        LockAcquire(&Semaphore->SemaphoreLock, &dummyState);
    }

    Semaphore->Value--;
    LockRelease(&Semaphore->SemaphoreLock, dummyState);

    CpuIntrSetState(oldState);
}

void
SemaphoreUp(
    INOUT PSEMAPHORE Semaphore
    )
{
    INTR_STATE oldState;
    PLIST_ENTRY pEntry;

    ASSERT(NULL != Semaphore);

    LockAcquire(&Semaphore->SemaphoreLock, &oldState);

    pEntry = RemoveHeadList(&Semaphore->WaitingList);

    if (pEntry != &Semaphore->WaitingList)
    {
        PTHREAD pThread = CONTAINING_RECORD(pEntry, THREAD, ReadyList);
        ThreadUnblock(pThread);
    }
    else
    {
        Semaphore->Value++;
    }

    LockRelease(&Semaphore->SemaphoreLock, oldState);
}