import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils

class DumpMutexCommand(ParsedCommand):
    def setup_command_definition(self):
        parser = self.get_parser()
        parser.make_argument_element(lldb.eArgTypeAddress, 'plain')

    def get_short_help(self):
        return "Dump mutex based on address."

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_ctx, result):
        try:
            addr = int(args_array, base=16)
        except ValueError:
            print('Invalid hexadecimal address!')
            return

        mutex = hal_utils.get_value_from_address(hal_utils.MUTEX_TYPE,
                                                    addr)
        waiting_list = hal_utils.get_field_as_address(mutex, 'WaitingList')

        def list_callback(list_entry):
            thread = hal_utils.containing_record(list_entry, hal_utils.THREAD_TYPE, 'ReadyList') 
            thread_addr = hal_utils.get_address_of_value(thread)
            thread_name = hal_utils.get_thread_name(thread)
            proc = hal_utils.get_process_from_thread(thread)
            proc_addr = hal_utils.get_address_of_value(proc)
            proc_name = hal_utils.get_process_name(proc)
            print(f'Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')

        print(f'Mutex: {hex(addr)}')
        print(mutex)
        print(f'Waiting list: ')
        hal_utils.traverse_list(waiting_list, list_callback)

class DumpExEventCommand(ParsedCommand):
    def setup_command_definition(self):
        parser = self.get_parser()
        parser.make_argument_element(lldb.eArgTypeAddress, 'plain')

    def get_short_help(self):
        return "Dump ex event based on address."

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_ctx, result):
        try:
            addr = int(args_array, base=16)
        except ValueError:
            print('Invalid hexadecimal address!')
            return

        ex_event = hal_utils.get_value_from_address(hal_utils.EX_EVENT_TYPE,
                                                    addr)
        waiting_list = hal_utils.get_field_as_address(ex_event, 'WaitingList')

        def list_callback(list_entry):
            thread = hal_utils.containing_record(list_entry, hal_utils.THREAD_TYPE, 'ReadyList') 
            thread_addr = hal_utils.get_address_of_value(thread)
            thread_name = hal_utils.get_thread_name(thread)
            proc = hal_utils.get_process_from_thread(thread)
            proc_addr = hal_utils.get_address_of_value(proc)
            proc_name = hal_utils.get_process_name(proc)
            print(f'Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')

        print(f'EX Event: {hex(addr)}')
        print(ex_event)
        print(f'Waiting list: ')
        hal_utils.traverse_list(waiting_list, list_callback)

