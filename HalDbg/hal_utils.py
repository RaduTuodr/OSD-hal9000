import lldb

DEBUGGER_TARGET = None
DEBUGGER_PROCESS = None
LIST_ENTRY = None
THREAD_TYPE = None
PROCESS_TYPE = None

def init(debugger):
   global DEBUGGER_TARGET
   global DEBUGGER_PROCESS
   global LIST_ENTRY
   global THREAD_TYPE
   global PROCESS_TYPE

   DEBUGGER_TARGET = debugger.GetSelectedTarget()
   DEBUGGER_PROCESS = DEBUGGER_TARGET.GetProcess()
   LIST_ENTRY = DEBUGGER_TARGET.FindFirstType('LIST_ENTRY')
   THREAD_TYPE = DEBUGGER_TARGET.FindFirstType('THREAD')
   PROCESS_TYPE = DEBUGGER_TARGET.FindFirstType('PROCESS')

def get_value_from_address(type, address):
   addr = lldb.SBAddress(address, DEBUGGER_TARGET)
   return DEBUGGER_TARGET.CreateValueFromAddress('Value', addr, type)

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

def get_current_thread(frame):
   thread_addr = frame.FindRegister('fs_base').GetValueAsAddress()
   return get_value_from_address(THREAD_TYPE, thread_addr)

def get_process_from_thread(thread):
   proc_addr = thread.GetChildMemberWithName('Process').GetValueAsAddress()
   return get_value_from_address(PROCESS_TYPE, proc_addr) 

def get_thread_name(thread):
   name_addr = thread.GetChildMemberWithName('Name').GetValueAsAddress()
   return DEBUGGER_PROCESS.ReadCStringFromMemory(name_addr, 256, lldb.SBError())

def get_process_name(process):
   proc_name_addr = process.GetChildMemberWithName('ProcessName').GetValueAsAddress()
   return DEBUGGER_PROCESS.ReadCStringFromMemory(proc_name_addr, 256, lldb.SBError())
