import lldb
from enum import Enum

DEBUGGER_TARGET = None
DEBUGGER_PROCESS = None
LIST_ENTRY = None
THREAD_TYPE = None
PROCESS_TYPE = None
PFILE_OBJECT_TYPE = None
FILE_OBJECT_TYPE = None
FILE_OBJECT_FLAGS_TYPE = None
PCPU_TYPE = None

_hal_commands = None

class HalCommandType(Enum):
   HalCommandTypeClass = 1,
   HalCommandTypeFunction = 2

class HalCommand:
   def __init__(self, impl, type, name):
      self.impl = impl
      self.type = type
      self.name = name

def init(debugger):
   global DEBUGGER_TARGET
   global DEBUGGER_PROCESS
   global LIST_ENTRY
   global THREAD_TYPE
   global PROCESS_TYPE
   global PFILE_OBJECT_TYPE
   global FILE_OBJECT_TYPE
   global FILE_OBJECT_FLAGS_TYPE
   global PCPU_TYPE
   global _hal_commands

   DEBUGGER_TARGET = debugger.GetSelectedTarget()
   DEBUGGER_PROCESS = DEBUGGER_TARGET.GetProcess()
   LIST_ENTRY = DEBUGGER_TARGET.FindFirstType('struct _LIST_ENTRY')
   THREAD_TYPE = DEBUGGER_TARGET.FindFirstType('struct _THREAD')
   PROCESS_TYPE = DEBUGGER_TARGET.FindFirstType('struct _PROCESS')
   PFILE_OBJECT_TYPE = DEBUGGER_TARGET.FindFirstType('PFILE_OBJECT')
   FILE_OBJECT_TYPE = DEBUGGER_TARGET.FindFirstType('struct _FILE_OBJECT')
   FILE_OBJECT_FLAGS_TYPE = DEBUGGER_TARGET.FindFirstType('struct _FILE_OBJECT_FLAGS')
   PCPU_TYPE = DEBUGGER_TARGET.FindFirstType('struct _PCPU')

   _hal_commands = []

def add_function_command(debugger, cmd):
   debugger.HandleCommand(f'command script add -f {cmd.impl} {cmd.name}')
   _hal_commands.append(cmd)

def add_class_command(debugger, cmd):
   debugger.HandleCommand(f'command script add -c {cmd.impl} {cmd.name}')
   _hal_commands.append(cmd)

def add_commands(debugger, commands):
   for cmd in commands:
      print(f'Adding command {cmd.name}')
      if cmd.type == HalCommandType.HalCommandTypeFunction:
            add_function_command(debugger, cmd)
      elif cmd.type == HalCommandType.HalCommandTypeClass:
            add_class_command(debugger, cmd)

def hal_commands(debugger, command, exe_ctx, result, internal_dict):
   """List all commands for HAL9000."""
   for cmd in _hal_commands:
      print(cmd.name)

def traverse_list(list_head_value, callback):
   list_head = list_head_value.GetAddress().GetLoadAddress(DEBUGGER_TARGET)
   curr_entry = list_head_value.GetChildMemberWithName('Flink').GetValueAsAddress()

   while curr_entry != list_head:
      list_entry = get_value_from_address(LIST_ENTRY, curr_entry)
      callback(list_entry)
      curr_entry = list_entry.GetChildMemberWithName('Flink').GetValueAsAddress()

def containing_record(list_entry, type, field_name):
   list_entry_addr = list_entry.GetAddress().GetLoadAddress(DEBUGGER_TARGET)
   found = False

   for i in range(type.GetNumberOfFields()):
      field = type.GetFieldAtIndex(i)
      if field.GetName() == field_name:
         offset = field.GetOffsetInBytes()
         found = True
         break
   
   if not found:
      return None

   list_entry_addr -= offset

   return get_value_from_address(type, list_entry_addr)

def find_global_variable(name):
   return DEBUGGER_TARGET.FindFirstGlobalVariable(name)

def get_value_from_address(type, address):
   addr = lldb.SBAddress(address, DEBUGGER_TARGET)
   return DEBUGGER_TARGET.CreateValueFromAddress('Value', addr, type)

def get_address_of_value(value):
   return value.GetAddress().GetLoadAddress(DEBUGGER_TARGET)

def get_c_string(addr, max_length):
   return DEBUGGER_PROCESS.ReadCStringFromMemory(addr, max_length, lldb.SBError())

def get_field(object, field):
   return object.GetChildMemberWithName(field)

def get_field_as_address(object, field):
   return object.GetChildMemberWithName(field).GetValueAsAddress()

def get_field_as_unsigned(object, field):
   return object.GetChildMemberWithName(field).GetValueAsUnsigned()

def get_current_thread(frame):
   thread_addr = frame.FindRegister('fs_base').GetValueAsAddress()
   return get_value_from_address(THREAD_TYPE, thread_addr)

def get_current_cpu(frame): 
   pcpu_addr = frame.FindRegister('gs_base').GetValueAsAddress()
   return get_value_from_address(PCPU_TYPE, pcpu_addr)

def get_process_from_thread(thread):
   proc_addr = get_field_as_address(thread, 'Process')
   return get_value_from_address(PROCESS_TYPE, proc_addr) 

def get_thread_name(thread):
   name_addr = get_field_as_address(thread, 'Name')
   return get_c_string(name_addr, 256)

def get_process_name(process):
   name_addr = get_field_as_address(process, 'ProcessName')
   return get_c_string(name_addr, 256)

def get_file_name(file_object):
   name_addr = get_field_as_address(file_object, 'FileName')
   return get_c_string(name_addr, 256)
