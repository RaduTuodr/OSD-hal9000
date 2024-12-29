import lldb

import hal_utils

def list_threads(debugger, command, exe_cxt, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread_data = target.FindFirstGlobalVariable('m_threadSystemData')
    all_threads_list = thread_data.GetChildMemberWithName('AllThreadsList')

    def list_callback(list_entry):
        thread = hal_utils.containing_record(target, list_entry, hal_utils.THREAD_TYPE, 'AllList') 
        thread_name = hal_utils.get_thread_name(process, thread)
        proc_addr = thread.GetChildMemberWithName('Process').GetValueAsAddress()
        proc = hal_utils.get_value_from_address(target, hal_utils.PROCESS_TYPE, proc_addr) 
        proc_name = hal_utils.get_process_name(process, proc)
        print(f'Name: {thread_name}, Process: {proc_name}')

    print('Threads:')
    hal_utils.traverse_list(target, all_threads_list, list_callback)

def list_running_threads(debugger, command, exe_cxt, result, internal_dict):
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    core_count = process.GetNumThreads()

    print('Running threads:')
    for i in range(core_count):
        core = process.GetThreadAtIndex(i)
        frame = core.GetSelectedFrame()
        thread = hal_utils.get_current_thread(target, frame) 
        thread_name = hal_utils.get_thread_name(process, thread)
        proc_addr = thread.GetChildMemberWithName('Process').GetValueAsAddress()
        proc = hal_utils.get_value_from_address(target, hal_utils.PROCESS_TYPE, proc_addr) 
        proc_name = hal_utils.get_process_name(process, proc)
        print(f'Core {i}: Name: {thread_name}, Process: {proc_name}')
