import lldb

_notifications = {}

def register_notification(function_name, callback):
    if function_name in _notifications:
        print(f'Notification {function_name} already registered!')
        return

    _notifications[function_name] = callback
    print(f'Notification {function_name} registered.')

def receive_notification(frame, bp_loc, internal_dict):
    global _notifications
    thread = frame.GetThread()
    process = thread.GetProcess()
    target = process.GetTarget()

    if thread.GetNumFrames() <= 1:
        process.Continue()

    notifier_frame = thread.GetFrameAtIndex(1)
    function_name = notifier_frame.GetFunctionName()

    print(f'Notification received!')
    print(f'Notifier Frame: {notifier_frame}')
    print(f'Notifier Frame rip: {hex(notifier_frame.GetPC())}')

    for name, callback in _notifications.items():
        if function_name == name:
            print(f'Handling notification {function_name}')
            callback(target, process, thread, notifier_frame) 
            break

    process.Continue()
