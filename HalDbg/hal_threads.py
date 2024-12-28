import lldb

import hal_utils

def list_threads(debugger, command, exe_cxt, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread_type = target.FindFirstType('THREAD')
    process_type = target.FindFirstType('PROCESS')
    thread_data = target.FindFirstGlobalVariable('m_threadSystemData')
    all_threads_list = thread_data.GetChildMemberWithName('AllThreadsList')
    error = lldb.SBError()

    def list_callback(list_entry):
        thread = hal_utils.containing_record(target, list_entry, thread_type, 'AllList') 
        name_addr = thread.GetChildMemberWithName('Name').GetValueAsAddress()
        thread_name = process.ReadCStringFromMemory(name_addr, 256, error)
        proc_addr = thread.GetChildMemberWithName('Process').GetValueAsAddress()
        proc = hal_utils.get_value_from_address(target, process_type, proc_addr) 
        proc_name_addr = proc.GetChildMemberWithName('ProcessName').GetValueAsAddress()
        proc_name = process.ReadCStringFromMemory(proc_name_addr, 256, error)
        print(f'Name: {thread_name}, Process: {proc_name}')

    print('Threads:')
    hal_utils.traverse_list(target, all_threads_list, list_callback)
