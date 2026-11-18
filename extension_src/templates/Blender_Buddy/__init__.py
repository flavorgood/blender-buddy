# Blender Buddy app template.
#
# When Blender opens with this template, the whole program is
# Buddy's screens (Start / Model / Look / Finish) - this little
# file just makes sure the Buddy add-on itself is switched on,
# whichever way it was installed. If Buddy isn't installed,
# the template still opens; install Blender Buddy and the
# screens come alive.
#
# The enable is tried at once and then retried on a timer for
# a few seconds: at template-load time the extension list may
# not have been scanned yet, and a single early attempt can
# miss an installed-but-not-yet-listed Buddy (found the hard
# way: a cold profile opened the template with Buddy present
# on disk but never switched on).

import bpy

_MODULES = ("bl_ext.user_default.blender_buddy",
            "blender_buddy")
_tries = [0]


def _try_enable():
    for module in _MODULES:
        if module in bpy.context.preferences.addons:
            return True
    for module in _MODULES:
        try:
            bpy.ops.preferences.addon_enable(module=module)
            return True
        except Exception:
            pass
    return False


def _retry():
    _tries[0] += 1
    if _try_enable() or _tries[0] >= 10:
        return None
    return 1.0


def register():
    _tries[0] = 0
    if not _try_enable():
        try:
            bpy.app.timers.register(_retry, first_interval=1.0)
        except Exception:
            pass


def unregister():
    pass
