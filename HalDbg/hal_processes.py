import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils

class ListProcessesCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List processes.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        proc_data = hal_utils.find_global_variable('m_processData')
        all_proc_list = hal_utils.get_field(proc_data, 'ProcessList')

        def list_callback(list_entry):
            proc = hal_utils.containing_record(list_entry, hal_utils.PROCESS_TYPE, 'NextProcess') 
            proc_addr = hal_utils.get_address_of_value(proc)
            proc_name = hal_utils.get_process_name(proc)
            print(f'Process {hex(proc_addr)}: {proc_name}')

        print('Processes:')
        hal_utils.traverse_list(all_proc_list, list_callback)
