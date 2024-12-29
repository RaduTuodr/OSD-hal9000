import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils
from hal_utils import FrameLocation

_mutexes = {}
_ex_events = {}

class Mutex:
    def __init__(self, frame_location):
        self.frame_location = frame_location

class ExEvent:
    def __init__(self, frame_location):
        self.frame_location = frame_location

def on_mutex_init(core, frame):
    global _mutexes

    mutex_ptr = frame.FindVariable('Mutex').GetValueAsAddress()

    loc = None
    if core.GetNumFrames() >= 3:
        creator = core.GetFrameAtIndex(2)
        loc = FrameLocation(creator.GetDisplayFunctionName(),
                            creator.GetLineEntry(),
                            []) # Do not store too much
                            # creator.arguments) 

    _mutexes[mutex_ptr] = Mutex(loc)

def on_mutex_destroy(core, frame):
    global _mutexes

    mutex_ptr = frame.FindVariable('Mutex').GetValueAsAddress()

    if mutex_ptr in _mutexes:
        _mutexes.pop(mutex_ptr)

class ListMutexesCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List all mutexes.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        global _mutexes

        print('Mutexes:')
        for key, value in _mutexes.items():
            print(f'Mutex {hex(key)}')
            if value.frame_location:
                function = value.frame_location.function
                filename = value.frame_location.line_entry.GetFileSpec().basename
                line = value.frame_location.line_entry.GetLine()
                col = value.frame_location.line_entry.GetColumn()
                print(f'  Init location: {function} at {filename}:{line}:{col}')

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
        waiting_list = hal_utils.get_field(mutex, 'WaitingList')

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

def on_ex_event_init(core, frame):
    global _ex_events

    event_ptr = frame.FindVariable('Event').GetValueAsAddress()

    loc = None
    if core.GetNumFrames() >= 3:
        creator = core.GetFrameAtIndex(2)
        loc = FrameLocation(creator.GetDisplayFunctionName(),
                            creator.GetLineEntry(),
                            []) # Do not store too much
                            # creator.arguments) 

    _ex_events[event_ptr] = ExEvent(loc)

def on_ex_event_destroy(core, frame):
    global _ex_events

    event_ptr = frame.FindVariable('Event').GetValueAsAddress()

    if event_ptr in _ex_events:
        _ex_events.pop(event_ptr)

class ListExEventsCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List all executive events.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        global _ex_events

        print('EX Events:')
        for key, value in _ex_events.items():
            print(f'EX Event {hex(key)}')
            if value.frame_location:
                function = value.frame_location.function
                filename = value.frame_location.line_entry.GetFileSpec().basename
                line = value.frame_location.line_entry.GetLine()
                col = value.frame_location.line_entry.GetColumn()
                print(f'  Init location: {function} at {filename}:{line}:{col}')

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
        waiting_list = hal_utils.get_field(ex_event, 'WaitingList')

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

