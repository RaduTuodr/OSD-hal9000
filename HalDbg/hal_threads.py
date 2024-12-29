import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils

class ListThreadsCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List all threads.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        thread_data = hal_utils.find_global_variable('m_threadSystemData')
        all_threads_list = hal_utils.get_field(thread_data, 'AllThreadsList')

        def list_callback(list_entry):
            thread = hal_utils.containing_record(list_entry, hal_utils.THREAD_TYPE, 'AllList') 
            thread_addr = hal_utils.get_address_of_value(thread)
            thread_name = hal_utils.get_thread_name(thread)
            proc = hal_utils.get_process_from_thread(thread)
            proc_addr = hal_utils.get_address_of_value(proc)
            proc_name = hal_utils.get_process_name(proc)
            print(f'Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')

        print('Threads:')
        hal_utils.traverse_list(all_threads_list, list_callback)

class ListRunningThreadsCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List running threads.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        core_count = hal_utils.DEBUGGER_PROCESS.GetNumThreads()

        print('Running threads:')
        for i in range(core_count):
            core = hal_utils.DEBUGGER_PROCESS.GetThreadAtIndex(i)
            frame = core.GetSelectedFrame()
            thread = hal_utils.get_current_thread(frame) 
            thread_addr = hal_utils.get_address_of_value(thread)
            thread_name = hal_utils.get_thread_name(thread)
            proc = hal_utils.get_process_from_thread(thread)
            proc_addr = hal_utils.get_address_of_value(proc)
            proc_name = hal_utils.get_process_name(proc)
            print(f'Core {i}: Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')
