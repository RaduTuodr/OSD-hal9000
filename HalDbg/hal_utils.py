import lldb

def get_value_from_address(target, type, address):
   addr = lldb.SBAddress(address, target)
   return target.CreateValueFromAddress('Value', addr, type)

def traverse_list(target, list_head_value, callback):
   type = target.FindFirstType('LIST_ENTRY')
   list_head = list_head_value.GetAddress().GetLoadAddress(target)
   curr_entry = list_head_value.GetChildMemberWithName('Flink').GetValueAsAddress()

   while curr_entry != list_head:
      list_entry = get_value_from_address(target, type, curr_entry)
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
