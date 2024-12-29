import lldb

import hal_utils

def list_threads(debugger, command, exe_cxt, result, internal_dict):
    """List all threads"""
    thread_data = hal_utils.DEBUGGER_TARGET.FindFirstGlobalVariable('m_threadSystemData')
    all_threads_list = thread_data.GetChildMemberWithName('AllThreadsList')

    def list_callback(list_entry):
        thread = hal_utils.containing_record(list_entry, hal_utils.THREAD_TYPE, 'AllList') 
        thread_addr = hal_utils.get_address_of_value(thread)
        thread_name = hal_utils.get_thread_name(thread)
        proc = hal_utils.get_process_from_thread(thread)
        proc_addr = hal_utils.get_address_of_value(proc)
        proc_name = hal_utils.get_process_name(proc)
        print(f'Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')

    print('Threads:')
    hal_utils.traverse_list(all_threads_list, list_callback)

def list_running_threads(debugger, command, exe_cxt, result, internal_dict):
    """List running threads"""
    core_count = hal_utils.DEBUGGER_PROCESS.GetNumThreads()

    print('Running threads:')
    for i in range(core_count):
        core = hal_utils.DEBUGGER_PROCESS.GetThreadAtIndex(i)
        frame = core.GetSelectedFrame()
        thread = hal_utils.get_current_thread(frame) 
        thread_addr = hal_utils.get_address_of_value(thread)
        thread_name = hal_utils.get_thread_name(thread)
        proc = hal_utils.get_process_from_thread(thread)
        proc_addr = hal_utils.get_address_of_value(proc)
        proc_name = hal_utils.get_process_name(proc)
        print(f'Core {i}: Thread {hex(thread_addr)}: {thread_name}; Process {hex(proc_addr)}: {proc_name}')
