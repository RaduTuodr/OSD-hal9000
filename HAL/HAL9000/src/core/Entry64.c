#include "HAL9000.h"

#include "bootinfo.h"

#include "system.h"
#include "cmd_interpreter.h"
#include "common_lib.h"
#include "hal_assert.h"
#include "synch.h"
#include "cpumu.h"

#include "display.h"
#include "log.h"
#include "print.h"

//#define TST

#ifdef TST
#include "test_common
.h"
#include "keyboard.h"
#endif

int _fltused = 1;

void
Entry64(
    IN  int                       argc,
    IN  HAL_BOOT_INFORMATION*     argv
    )
{
    STATUS status;
    COMMON_LIB_INIT initSettings;

    // We don't have commonlib support yet, as a result we have no way of asserting at this point
    if (!IS_STACK_ALIGNED) __halt();

    status = STATUS_SUCCESS;
    memzero(&initSettings, sizeof(COMMON_LIB_INIT));

    initSettings.Size = sizeof(COMMON_LIB_INIT);
    initSettings.AssertFunction = Hal9000Assert;

    CpuMuPreinit();

    status = CpuMuSetMonitorFilterSize(sizeof(MONITOR_LOCK));
    initSettings.MonitorSupport = SUCCEEDED(status);

    status = CommonLibInit(&initSettings);
    if (!SUCCEEDED(status))
    {
        // not good lads
        __halt();
    }

    // No display configured yet
    // // ASSERT_INFO(1 == argc, "We are always expecting a single parameter\n");
    // // ASSERT_INFO(NULL != argv, "We are expecting a non-NULL pointer\n");
    if (argc != 1 || argv == NULL)
    {
        __halt();
    }

    if (!SUCCEEDED(ValidateHalBootInformation(argv)))
    {
        __halt();
    }

    gVirtualToPhysicalOffset = argv->VirtualToPhysicalOffset;
    gAcpiRsdpAddress = argv->AcpiRsdp;
    SystemPreinit(argv);

    status = SystemInit(argv);

    ASSERT(SUCCEEDED(status));

    LOGL("InitSystem executed successfully\n");

#ifdef TST
    TestRunAllFunctional();
    TestRunAllPerformance();
    KeyboardResetSystem();
#endif

    // will run until exit command
    CmdRun();

    // uninitialize system
    // at the end of this routine interrupts should be disabled
    SystemUninit();

    __halt();
}