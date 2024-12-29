import lldb

import hal_threads
import hal_processes
import hal_notify
import hal_utils
import hal_files

def __lldb_init_module(debugger, internal_dict):
    print('Loading HAL9000 module...')

    print('Initializing hal_utils')
    hal_utils.init(debugger)

    print('Adding command list_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_threads list_threads')

    print('Adding command list_processes')
    debugger.HandleCommand('command script add -f hal_dbg.hal_processes.list_processes list_processes')

    print('Adding command list_running_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_running_threads list_running_threads')

    print('Setting notification breakpoint')
    debugger.HandleCommand('breakpoint set -n NotifyDebugger')
    debugger.HandleCommand('breakpoint command add -F hal_dbg.hal_notify.receive_notification')

    print('Registering file notification handlers')
    hal_notify.register_notification('IoCreateFile', hal_files.on_file_create)
    hal_notify.register_notification('IoCloseFile', hal_files.on_file_close)

    print('Adding command list_file_objects')
    debugger.HandleCommand('command script add -f hal_dbg.hal_files.list_file_objects list_file_objects')

    print('Loaded HAL9000 module.')
