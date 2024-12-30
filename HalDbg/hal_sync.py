import lldb
from lldb.plugins.parsed_cmd import ParsedCommand
from enum import Enum

import hal_utils
from hal_utils import FrameLocation

_mutexes = {}
_ex_events = {}
_locks = {}

class LockType(Enum):
    Spinlock = 1,
    MonitorLock = 2,
    RwSpinlock = 3,
    RecRwSpinlock = 4,
    Any = 5

class Lock:
    def __init__(self, type, frame_location):
        self.type = type
        self.frame_location = frame_location

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

def add_lock(type, lock_ptr, core):
    global _locks

    loc = None
    if core.GetNumFrames() >= 3:
        creator = core.GetFrameAtIndex(2)
        loc = FrameLocation(creator.GetDisplayFunctionName(),
                            creator.GetLineEntry(),
                            []) # Do not store too much
                            # creator.arguments) 

    _locks[lock_ptr] = Lock(type, loc)

def on_spinlock_init(core, frame):
    lock_ptr = frame.FindVariable('Lock').GetValueAsAddress()

    add_lock(LockType.Spinlock, lock_ptr, core)

def on_monlock_init(core, frame):
    lock_ptr = frame.FindVariable('Lock').GetValueAsAddress()

    add_lock(LockType.MonitorLock, lock_ptr, core)

def on_lock_destroy(core, frame):
    global _locks

    lock_ptr = frame.FindVariable('Lock').GetValueAsAddress()

    if lock_ptr in _locks:
        _locks.pop(lock_ptr)

def on_rw_spinlock_init(core, frame):
    lock_ptr = frame.FindVariable('Spinlock').GetValueAsAddress()

    add_lock(LockType.RwSpinlock, lock_ptr, core)

def on_rec_rw_spinlock_init(core, frame):
    global _locks

    lock_ptr = frame.FindVariable('Spinlock').GetValueAsAddress()
    rec_rw_lock = hal_utils.get_value_from_address(hal_utils.REC_RW_SPINLOCK_TYPE,
                                                   lock_ptr)
    rw_lock = hal_utils.get_field(rec_rw_lock, 'RwSpinlock')
    rw_lock_ptr = hal_utils.get_address_of_value(rw_lock)

    # See rec rw lock init function
    if rw_lock_ptr in _locks:
        _locks.pop(rw_lock_ptr)
    else:
        print('We should have had a rw lock saved')

    add_lock(LockType.RecRwSpinlock, lock_ptr, core) 

def on_rw_spinlock_destroy(core, frame):
    global _locks

    lock_ptr = frame.FindVariable('Spinlock').GetValueAsAddress()

    if lock_ptr in _locks:
        _locks.pop(lock_ptr)

def on_rec_rw_spinlock_destroy(core, frame):
    global _locks

    lock_ptr = frame.FindVariable('Spinlock').GetValueAsAddress()

    if lock_ptr in _locks:
        _locks.pop(lock_ptr)

class ListAllLocksCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List all locks.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        global _locks

        print('Locks:')
        for key, value in _locks.items():
            print(f'Lock {hex(key)}, Type: {value.type.name}')
            if value.frame_location:
                function = value.frame_location.function
                filename = value.frame_location.line_entry.GetFileSpec().basename
                line = value.frame_location.line_entry.GetLine()
                col = value.frame_location.line_entry.GetColumn()
                print(f'  Init location: {function} at {filename}:{line}:{col}')

class ListLocksCommand(ParsedCommand):

    def setup_command_definition(self):
        enum_values = [
            ['Any', 'Select all lock types'],
            ['Spinlock', 'Select all spinlocks'],
            ['MonitorLock', 'Select all monitorlocks'],
            ['RwSpinlock', 'Select all rw spinlocks'],
            ['RecRwSpinlock', 'Select all rec rw spinlocks']
        ]

        parser = self.get_parser()
        parser.add_option(short_option='t',
                        long_option='type',
                        help='Filters displayed spinlocks based on type',
                        default='Any',
                        value_type=lldb.eArgTypeTypeName,
                        enum_values=enum_values)

    def get_short_help(self):
        return 'List all locks of a given type.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        global _locks

        filt = LockType[self.get_parser().type]

        print('Locks:')
        for key, value in _locks.items():
            if filt == LockType.Any or filt == value.type:
                print(f'Lock {hex(key)}, Type: {value.type.name}')
                if value.frame_location:
                    function = value.frame_location.function
                    filename = value.frame_location.line_entry.GetFileSpec().basename
                    line = value.frame_location.line_entry.GetLine()
                    col = value.frame_location.line_entry.GetColumn()
                    print(f'  Init location: {function} at {filename}:{line}:{col}')
