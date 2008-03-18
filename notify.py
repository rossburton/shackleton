import pynotify

pynotify.init("Shackleton")

def enter(context):
    l = ["<b>Entering %s context:</b>" % context]
    l += [str(a) for a in context.entering_actions]
    details = "\n\342\200\242 ".join(l)
    pynotify.Notification("Changing Context", details).show()
