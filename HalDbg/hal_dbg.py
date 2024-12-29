import lldb

import hal_threads
import hal_processes
import hal_notify

def __lldb_init_module(debugger, internal_dict):
    print('Loading HAL9000 module...')

    print('Adding command list_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_threads list_threads')

    print('Adding command list_processes')
    debugger.HandleCommand('command script add -f hal_dbg.hal_processes.list_processes list_processes')

    print('Adding command list_running_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_running_threads list_running_threads')

    print('Setting notification breakpoint')
    debugger.HandleCommand('breakpoint set -n NotifyDebugger')
    debugger.HandleCommand('breakpoint command add -F hal_dbg.hal_notify.receive_notification')

    print('Loaded HAL9000 module.')
