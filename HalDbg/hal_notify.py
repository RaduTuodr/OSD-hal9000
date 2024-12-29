import lldb

count = 0

def receive_notification(frame, bp_loc, internal_dict):
    global count
    thread = frame.GetThread()
    process = thread.GetProcess()

    if thread.GetNumFrames() <= 1:
        process.Continue()

    notifier_frame = thread.GetFrameAtIndex(1)

    count = count + 1
    print(f'Notification {count} received!')
    print(f'Notifier Frame: {notifier_frame}')
    print(f'Notifier Frame rip: {hex(notifier_frame.GetPC())}')
    process.Continue()
