import lldb

import hal_utils

def list_processes(debugger, command, exe_cxt, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    proc_data = target.FindFirstGlobalVariable('m_processData')
    all_proc_list = proc_data.GetChildMemberWithName('ProcessList')

    def list_callback(list_entry):
        proc = hal_utils.containing_record(target, list_entry, hal_utils.PROCESS_TYPE, 'NextProcess') 
        proc_name = hal_utils.get_process_name(process, proc)
        print(f'Name: {proc_name}')

    print('Processes:')
    hal_utils.traverse_list(target, all_proc_list, list_callback)
