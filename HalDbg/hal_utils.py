import lldb

LIST_ENTRY = None
THREAD_TYPE = None
PROCESS_TYPE = None

def init(debugger):
   global LIST_ENTRY
   global THREAD_TYPE
   global PROCESS_TYPE

   target = debugger.GetSelectedTarget()
   LIST_ENTRY = target.FindFirstType('LIST_ENTRY')
   THREAD_TYPE = target.FindFirstType('THREAD')
   PROCESS_TYPE = target.FindFirstType('PROCESS')

def get_value_from_address(target, type, address):
   addr = lldb.SBAddress(address, target)
   return target.CreateValueFromAddress('Value', addr, type)

def traverse_list(target, list_head_value, callback):
   list_head = list_head_value.GetAddress().GetLoadAddress(target)
   curr_entry = list_head_value.GetChildMemberWithName('Flink').GetValueAsAddress()

   while curr_entry != list_head:
      list_entry = get_value_from_address(target, LIST_ENTRY, curr_entry)
      callback(list_entry)
      curr_entry = list_entry.GetChildMemberWithName('Flink').GetValueAsAddress()

def containing_record(target, list_entry, type, field_name):
   list_entry_addr = list_entry.GetAddress().GetLoadAddress(target)
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

   return get_value_from_address(target, type, list_entry_addr)

def get_current_thread(target, frame):
   thread_addr = frame.FindRegister('fs_base').GetValueAsAddress()
   return get_value_from_address(target, THREAD_TYPE, thread_addr)

def get_thread_name(proc, thread):
   name_addr = thread.GetChildMemberWithName('Name').GetValueAsAddress()
   return proc.ReadCStringFromMemory(name_addr, 256, lldb.SBError())

def get_process_name(proc, process):
   proc_name_addr = process.GetChildMemberWithName('ProcessName').GetValueAsAddress()
   return proc.ReadCStringFromMemory(proc_name_addr, 256, lldb.SBError())
