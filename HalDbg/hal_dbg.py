import lldb

import hal_threads
import hal_processes

def __lldb_init_module(debugger, internal_dict):
    print('Loading HAL9000 module...')

    print('Adding command list_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_threads list_threads')

    print('Adding command list_processes')
    debugger.HandleCommand('command script add -f hal_dbg.hal_processes.list_processes list_processes')

    print('Adding command list_running_threads')
    debugger.HandleCommand('command script add -f hal_dbg.hal_threads.list_running_threads list_running_threads')

    print('Loaded HAL9000 module.')
