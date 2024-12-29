import lldb
from lldb.plugins.parsed_cmd import ParsedCommand

import hal_utils

class DumpVmmReservationSpaceCommand(ParsedCommand):
    def setup_command_definition(self):
        parser = self.get_parser()
        parser.make_argument_element(lldb.eArgTypeAddress, 'plain')

    def get_short_help(self):
        return "Dump vmm reservation space based on address."

    def get_flags(self):
        return lldb.eCommandRequiresFrame | lldb.eCommandProcessMustBePaused
    
    def __call__(self, debugger, args_array, exe_ctx, result):
        try:
            addr = int(args_array, base=16)
        except ValueError:
            print('Invalid hexadecimal address!')
            return

        vmm_res_space = hal_utils.get_value_from_address(hal_utils.VMM_RESERVATION_SPACE_TYPE,
                                                    addr)
        vmm_res_list = hal_utils.get_field_as_address(vmm_res_space, 'ReservationList')
        vmm_bitmap_start = hal_utils.get_field_as_address(vmm_res_space, 'BitmapAddressStart')

        vmm_state_free = hal_utils.get_enum_member_value_as_unsigned(hal_utils.VMM_RESERVATION_STATE_TYPE,
                                                                    'VmmReservationStateFree')
        vmm_state_used = hal_utils.get_enum_member_value_as_unsigned(hal_utils.VMM_RESERVATION_STATE_TYPE,
                                                                    'VmmReservationStateUsed')
        vmm_state_last = hal_utils.get_enum_member_value_as_unsigned(hal_utils.VMM_RESERVATION_STATE_TYPE,
                                                                    'VmmReservationStateLast')

        vmm_res_size = hal_utils.VMM_RESERVATION_TYPE.GetByteSize()

        print(f'VMM Reservation Space: {hex(addr)}')
        print(vmm_res_space)
        print('VMM Reservations:')

        curr_ptr = vmm_res_list
        curr = hal_utils.get_value_from_address(hal_utils.VMM_RESERVATION_TYPE,
                                                curr_ptr)
        while hal_utils.get_field_as_unsigned(curr, 'State') != vmm_state_last and curr_ptr < vmm_bitmap_start:
            start_va = hal_utils.get_field_as_address(curr, 'StartVa')
            size = hal_utils.get_field_as_unsigned(curr, 'Size')
            page_rights = hal_utils.get_field_as_unsigned(curr, 'PageRights')
            state = hal_utils.get_field_as_unsigned(curr, 'State')
            uncacheable = hal_utils.get_field_as_unsigned(curr, 'Uncacheable')
            file = hal_utils.get_field_as_address(curr, 'BackingFile')
            if state == vmm_state_used:
                print(f'VMM Reservation {hex(curr_ptr)}: StartVa: {hex(start_va)}, Size: {hex(size)}, PageRights: {page_rights}, Unchacheable: {uncacheable}, BackingFile: {hex(file)}')
            curr_ptr = curr_ptr + vmm_res_size
            curr = hal_utils.get_value_from_address(hal_utils.VMM_RESERVATION_TYPE,
                                                    curr_ptr)
