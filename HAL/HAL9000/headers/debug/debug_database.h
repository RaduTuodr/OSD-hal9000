#pragma once

#include "mutex.h"

// DO NOT CHANGE ANYTHING IN THIS FILE.

STATUS
DebugDatabasePreinit(
    void
    );

void
DebugDatabaseSetMutexList(
    IN PLOCK             ListLock,
    IN PLIST_ENTRY       ListHead
    );

void
DebugDatabaseSetThreadList(
    IN PLOCK             ListLock,
    IN PLIST_ENTRY       ListHead
    );

void
DebugDatabaseSetProcessList(
    IN PMUTEX           ListMutex,
    IN PLIST_ENTRY      ListHead
    );
