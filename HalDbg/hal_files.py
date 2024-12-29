import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils

_file_objects = {}

# What about record ?
class FileObject:
    def __init__(self, process, file_name, file_object):
        self.process = process
        self.process_name = hal_utils.get_process_name(process)
        self.file_object = file_object
        self.file_name = file_name

def on_file_create(core, frame):
    global _file_objects
    handle_param = frame.FindVariable('Handle')
    file_name_param = frame.FindVariable('FileName')

    pfile_obj_addr = handle_param.GetValueAsAddress()
    pfile_obj = hal_utils.get_value_from_address(
        hal_utils.PFILE_OBJECT_TYPE,
        pfile_obj_addr)
    file_obj_addr = pfile_obj.GetValueAsAddress()
    file_obj = hal_utils.get_value_from_address(
        hal_utils.FILE_OBJECT_TYPE,
        file_obj_addr)
    
    file_name_addr = file_name_param.GetValueAsAddress()
    file_name = hal_utils.DEBUGGER_PROCESS.ReadCStringFromMemory(
        file_name_addr,
        256,
        lldb.SBError())

    thread = hal_utils.get_current_thread(core.GetSelectedFrame())
    process = hal_utils.get_process_from_thread(thread)

    _file_objects[file_obj_addr] = FileObject(process, file_name, file_obj) 

def on_file_close(core, frame):
    global _file_objects

    handle_param = frame.FindVariable('FileHandle')
    file_obj_addr = handle_param.GetValueAsAddress()
    if file_obj_addr in _file_objects:
        _file_objects.pop(file_obj_addr)

def list_file_objects(debugger, command, exe_cxt, result, internal_dict):
    """List all file objects."""
    global _file_objects

    print('File objects:')
    for key, value in _file_objects.items():
        proc_addr = hal_utils.get_address_of_value(value.process)
        print(f'File object {hex(key)}: FileName: {value.file_name}; Process {hex(proc_addr)}: {value.process_name}')

class DumpFileObjectCommand(ParsedCommand):
    def setup_command_definition(self):
        try:
            parser = self.get_parser()
            parser.make_argument_element(lldb.eArgTypeAddress, 'plain')
        except Exception as e:
            print(e)

    def get_short_help(self):
        return "Dump file object based on address."

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_ctx, result):
        print(args_array)
