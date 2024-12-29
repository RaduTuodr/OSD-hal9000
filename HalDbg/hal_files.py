import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils
from hal_utils import FrameLocation

_file_objects = {}

# What about record ?
class FileObject:
    def __init__(self, process, file_name, frame_location):
        self.process = hal_utils.get_address_of_value(process)
        self.process_name = hal_utils.get_process_name(process)
        self.file_name = file_name
        self.frame_location = frame_location

def on_file_create(core, frame):
    global _file_objects
    handle_param = frame.FindVariable('Handle')
    file_name_param = frame.FindVariable('FileName')

    pfile_obj_addr = handle_param.GetValueAsAddress()
    pfile_obj = hal_utils.get_value_from_address(
        hal_utils.PFILE_OBJECT_TYPE,
        pfile_obj_addr)
    file_obj_addr = pfile_obj.GetValueAsAddress()
    
    file_name_addr = file_name_param.GetValueAsAddress()
    file_name = hal_utils.get_c_string(file_name_addr, 256) 

    thread = hal_utils.get_current_thread(core.GetSelectedFrame())
    process = hal_utils.get_process_from_thread(thread)

    loc = None
    if core.GetNumFrames() >= 3:
        creator = core.GetFrameAtIndex(2)
        loc = FrameLocation(creator.GetDisplayFunctionName(),
                            creator.GetLineEntry(),
                            []) # Do not store too much
                            # creator.arguments) 

    _file_objects[file_obj_addr] = FileObject(process, file_name, loc) 

def on_file_close(core, frame):
    global _file_objects

    handle_param = frame.FindVariable('FileHandle')
    file_obj_addr = handle_param.GetValueAsAddress()
    if file_obj_addr in _file_objects:
        _file_objects.pop(file_obj_addr)

class ListFileObjectsCommand(ParsedCommand):
    def setup_command_definition(self):
        None

    def get_short_help(self):
        return 'List all file objects.'        

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_cxt, result):
        global _file_objects

        print('File objects:')
        for key, value in _file_objects.items():
            print(f'File object {hex(key)}: FileName: {value.file_name}; Process {hex(value.process)}: {value.process_name}')
            if value.frame_location:
                function = value.frame_location.function
                filename = value.frame_location.line_entry.GetFileSpec().basename
                line = value.frame_location.line_entry.GetLine()
                col = value.frame_location.line_entry.GetColumn()
                print(f'  Create location: {function} at {filename}:{line}:{col}')

class DumpFileObjectCommand(ParsedCommand):
    def setup_command_definition(self):
        parser = self.get_parser()
        parser.make_argument_element(lldb.eArgTypeAddress, 'plain')

    def get_short_help(self):
        return "Dump file object based on address."

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_ctx, result):
        try:
            addr = int(args_array, base=16)
        except ValueError:
            print('Invalid hexadecimal address!')
            return

        file_obj = hal_utils.get_value_from_address(hal_utils.FILE_OBJECT_TYPE,
                                                    addr)

        print(f'File object: {hex(addr)}')
        print(file_obj)
