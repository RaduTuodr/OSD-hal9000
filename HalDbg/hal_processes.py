import lldb

import hal_utils

def list_processes(debugger, command, exe_cxt, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    proc_type = target.FindFirstType('PROCESS')
    proc_data = target.FindFirstGlobalVariable('m_processData')
    all_proc_list = proc_data.GetChildMemberWithName('ProcessList')
    error = lldb.SBError()

    def list_callback(list_entry):
        proc = hal_utils.containing_record(target, list_entry, proc_type, 'NextProcess') 
        name_addr = proc.GetChildMemberWithName('ProcessName').GetValueAsAddress()
        proc_name = process.ReadCStringFromMemory(name_addr, 256, error)
        print(f'Name: {proc_name}')

    print('Processes:')
    hal_utils.traverse_list(target, all_proc_list, list_callback)
