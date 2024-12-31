import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_threads
import hal_processes
import hal_notify
import hal_utils
import hal_files
import hal_cpus
import hal_vmm
import hal_sync
from hal_utils import HalCommandType
from hal_utils import HalCommand

def __lldb_init_module(debugger, internal_dict):
    print('Loading HAL9000 module...')

    print('Initializing hal_utils')
    hal_utils.init(debugger)

    commands = [
        HalCommand('hal_dbg.hal_utils.hal_commands', 
                   HalCommandType.HalCommandTypeFunction, 
                   'hal_commands'),
        HalCommand('hal_dbg.hal_threads.ListThreadsCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_threads'),
        HalCommand('hal_dbg.hal_threads.DumpThreadCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_thread'),
        HalCommand('hal_dbg.hal_processes.ListProcessesCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_processes'),
        HalCommand('hal_dbg.hal_processes.DumpProcessCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_process'),
        HalCommand('hal_dbg.hal_threads.ListRunningThreadsCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_running_threads'),
        HalCommand('hal_dbg.hal_files.ListFileObjectsCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_file_objects'),
        HalCommand('hal_dbg.hal_files.DumpFileObjectCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_file_object'),
        HalCommand('hal_dbg.hal_vmm.DumpVmmReservationSpaceCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_vmm_reservation_space'),
        HalCommand('hal_dbg.hal_vmm.DumpVmmReservationCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_vmm_reservation'),
        HalCommand('hal_dbg.hal_sync.ListLocksCommand',
                   HalCommandType.HalCommandTypeParsed,
                   'list_locks'),
        HalCommand('hal_dbg.hal_sync.DumpLockCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_lock'),
        HalCommand('hal_dbg.hal_sync.ListMutexesCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_mutexes'),
        HalCommand('hal_dbg.hal_sync.DumpMutexCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_mutex'),
        HalCommand('hal_dbg.hal_sync.ListExEventsCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_ex_events'),
        HalCommand('hal_dbg.hal_sync.DumpExEventCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_ex_event'),
        HalCommand('hal_dbg.hal_cpus.ListCpusCommand',
                   HalCommandType.HalCommandTypeClass,
                   'list_cpus'),
        HalCommand('hal_dbg.hal_cpus.DumpCpuCommand',
                   HalCommandType.HalCommandTypeClass,
                   'dump_cpu'),
        HalCommand('hal_dbg.hal_notify.TrackCommand',
                   HalCommandType.HalCommandTypeClass,
                   'track')
    ]

    hal_utils.add_commands(debugger, commands)

    print('Setting notification breakpoint')
    debugger.HandleCommand('breakpoint set -n NotifyDebugger')
    debugger.HandleCommand('breakpoint command add -F hal_dbg.hal_notify.receive_notification')

    hal_notify.register_notification('IoCreateFile', hal_files.on_file_create)
    hal_notify.register_notification('IoCloseFile', hal_files.on_file_close)
    hal_notify.register_notification('MutexInit', hal_sync.on_mutex_init)
    hal_notify.register_notification('MutexDestroy', hal_sync.on_mutex_destroy)
    hal_notify.register_notification('ExEventInit', hal_sync.on_ex_event_init)
    hal_notify.register_notification('ExEventDestroy', hal_sync.on_ex_event_destroy)
    hal_notify.register_notification('SpinlockInit', hal_sync.on_spinlock_init)
    hal_notify.register_notification('MonitorLockInit', hal_sync.on_monlock_init)
    hal_notify.register_notification('_LockDestroy', hal_sync.on_lock_destroy)
    hal_notify.register_notification('RwSpinlockInit', hal_sync.on_rw_spinlock_init)
    hal_notify.register_notification('RwSpinlockDestroy', hal_sync.on_rw_spinlock_destroy)
    hal_notify.register_notification('RecRwSpinlockInit', hal_sync.on_rec_rw_spinlock_init)
    hal_notify.register_notification('RecRwSpinlockDestroy', hal_sync.on_rec_rw_spinlock_destroy)

    print('Loaded HAL9000 module.')
