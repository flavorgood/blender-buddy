"""Run in offline factory-startup Blender. For the native UI check, point the
platform temp environment (TEMP and TMP on Windows, TMPDIR on Unix) to a
private folder under BLENDER_USER_RESOURCES so quit.blend is isolated too.
"""
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import traceback

import bpy


assert "--factory-startup" in sys.argv and not bpy.app.online_access and not bpy.data.filepath
if not bpy.app.background:
    resources = Path(os.environ["BLENDER_USER_RESOURCES"]).resolve()
    for path_type in ("CONFIG", "SCRIPTS", "EXTENSIONS", "DATAFILES"):
        assert Path(bpy.utils.user_resource(path_type)).resolve().is_relative_to(resources)
    for variable in (("TEMP", "TMP") if os.name == "nt" else ("TMPDIR",)):
        assert Path(os.environ[variable]).resolve().is_relative_to(resources)
    assert Path(bpy.app.tempdir).resolve().is_relative_to(resources), "Use a private Blender test temp folder."
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as buddy


class StaleHandle:
    def __init__(self, exception):
        self.exception = exception

    @property
    def bl_idname(self):
        raise self.exception("RNA operator is no longer valid")


def check_handles():
    other = SimpleNamespace(bl_idname="OTHER_OT_modal")
    stale = [None, object(), StaleHandle(ReferenceError), StaleHandle(RuntimeError), other]
    pointer = 39
    legacy = SimpleNamespace(as_pointer=lambda: pointer)
    buddy._CARD_INPUT_WINDOWS.add(pointer)
    try:
        assert buddy._card_has_listener(legacy)
        assert not buddy._card_has_listener(SimpleNamespace(modal_operators=stale, as_pointer=legacy.as_pointer))
        live = SimpleNamespace(bl_idname="BUDDY_OT_expert_card_modal")
        assert buddy._card_has_listener(SimpleNamespace(modal_operators=stale + [live]))
    finally:
        buddy._CARD_INPUT_WINDOWS.discard(pointer)
    assert not buddy._card_has_listener(legacy)


def check_native():
    try:
        window = bpy.context.window_manager.windows[0]
        area = next(a for a in window.screen.areas if a.type == "VIEW_3D")
        region = next(r for r in area.regions if r.type == "WINDOW")
        with bpy.context.temp_override(window=window, area=area, region=region):
            assert not buddy._card_has_listener(window)
            assert bpy.ops.buddy.expert_card_modal("INVOKE_DEFAULT") == {"RUNNING_MODAL"}
            assert buddy._card_has_listener(window)
            assert bpy.ops.buddy.expert_card_modal("INVOKE_DEFAULT") == {"CANCELLED"}
        print("EXPERT_LISTENER_NATIVE_OK", bpy.app.version_string, flush=True)
    except Exception:
        traceback.print_exc()
        sys.stderr.flush()
        os._exit(1)  # An exception in an app timer does not set Blender's exit status.
    bpy.ops.wm.quit_blender()
    return None


check_handles()
print("EXPERT_LISTENER_STALE_HANDLES_OK", bpy.app.version_string, flush=True)
if not bpy.app.background:
    # Register only the listener; the normal watchdog would race this specific test.
    bpy.utils.register_class(buddy.BUDDY_OT_expert_card_modal)
    bpy.app.timers.register(check_native, first_interval=0.5)
