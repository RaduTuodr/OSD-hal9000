import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_threads
import hal_processes
import hal_notify
import hal_utils
import hal_files
import hal_cpus

def __lldb_init_module(debugger, internal_dict):
    print('Loading HAL9000 module...')

    print('Initializing hal_utils')
    hal_utils.init(debugger)

    print('Adding command hal_commands')
    hal_utils.add_function_command(debugger, 'hal_dbg.hal_utils.hal_commands', 'hal_commands')

    print('Adding command list_threads')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_threads.ListThreadsCommand', 'list_threads')

    print('Adding command list_processes')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_processes.ListProcessesCommand', 'list_processes')

    print('Adding command list_running_threads')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_threads.ListRunningThreadsCommand', 'list_running_threads')

    print('Setting notification breakpoint')
    debugger.HandleCommand('breakpoint set -n NotifyDebugger')
    debugger.HandleCommand('breakpoint command add -F hal_dbg.hal_notify.receive_notification')

    print('Registering file notification handlers')
    hal_notify.register_notification('IoCreateFile', hal_files.on_file_create)
    hal_notify.register_notification('IoCloseFile', hal_files.on_file_close)

    print('Adding command list_file_objects')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_files.ListFileObjectsCommand', 'list_file_objects')

    print('Adding command dump_file_object')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_files.DumpFileObjectCommand', 'dump_file_object')
    
    print('Adding command list_cpus')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_cpus.ListCpusCommand', 'list_cpus')

    print('Adding command dump_cpu')
    hal_utils.add_class_command(debugger, 'hal_dbg.hal_cpus.DumpCpuCommand', 'dump_cpu')

    print('Loaded HAL9000 module.')
