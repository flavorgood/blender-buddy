"""Native Blender target validation. Run with --background --factory-startup --offline-mode."""
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import mock

import bpy

assert bpy.app.background and not bpy.app.online_access and not bpy.data.filepath
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as buddy
buddy.register()
context = bpy.context
wm = context.window_manager
cube = context.active_object
assert cube.name == "Cube" and len(cube.data.polygons) == 6
bpy.ops.mesh.primitive_cube_add(location=(4, 0, 0))
other = context.active_object


def select(obj):
    for selected in list(context.selected_objects):
        selected.select_set(False)
    if obj is not None:
        obj.select_set(True)
    context.view_layer.objects.active = obj


def ask(reply="STEP: tool:object.shade_smooth", before_reply=None):
    wm.buddy_ask = "Change the current shape"
    def provider(*args):
        if before_reply:
            before_reply()
        return "SUMMARY: update the scene\n" + reply
    # Native operators and plan parsing are real. No external provider or prefs.
    with mock.patch.object(buddy, "_expert_settings", return_value={"service":"LOCAL", "url":"http://localhost:11434/v1/chat/completions"}), \
            mock.patch.object(buddy, "_local_alive", return_value=True), \
            mock.patch.object(buddy, "_ask_ai", side_effect=provider):
        assert bpy.ops.buddy.ask_expert() == {"FINISHED"} and wm.buddy_plan


def reject():
    assert bpy.ops.buddy.run_plan() == {"CANCELLED"}
    assert not wm.buddy_plan and "Nothing ran" in wm.buddy_answer
    assert not any(p.use_smooth for p in cube.data.polygons)
    assert not any(p.use_smooth for p in other.data.polygons)


select(cube)
wm.buddy_agent = True
ask(before_reply=lambda: select(other))
reject()
assert context.active_object == other
select(cube)
ask()
other.select_set(True)
reject()
assert context.active_object == cube and other.select_get()

select(cube)
ask()
scene = context.scene
new_scene = bpy.data.scenes.new("Other test scene")
context.window.scene = new_scene
reject()
context.window.scene = scene

select(None)
ask("STEP: button:add_ball")
select(other)
reject()
select(None)
ask("STEP: button:add_ball")
count = len(bpy.data.objects)
assert bpy.ops.buddy.run_plan() == {"FINISHED"} and len(bpy.data.objects) == count + 1

# An object rename does not change its identity.
select(cube)
ask()
cube.name = "Same object renamed"
assert bpy.ops.buddy.run_plan() == {"FINISHED"}
assert all(p.use_smooth for p in cube.data.polygons)

# Manually supplied plans retain their established behavior.
select(other)
wm.buddy_plan = json.dumps([{"kind":"tool", "id":"object.shade_smooth"}])
assert bpy.ops.buddy.run_plan() == {"FINISHED"}
assert all(p.use_smooth for p in other.data.polygons)

# A plan and pending target must not survive a file load as executable steps.
select(cube)
ask()
with TemporaryDirectory() as tmp:
    blend = str(Path(tmp) / "private-target-check.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend, check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=blend, load_ui=False, use_scripts=False)
    assert not bpy.context.window_manager.buddy_plan
    assert buddy._EXPERT_JOB.get("reviewed_target") is None

# Confirm the native key handler with synthetic platform events and clipboard.
ctx = SimpleNamespace(window_manager=SimpleNamespace(clipboard="two\n words"))
with mock.patch.object(buddy, "_card_tag_redraw"):
    for platform, ctrl, command, expected in (("darwin", False, True, True),
                                               ("linux", True, False, True),
                                               ("win32", False, True, False)):
        with mock.patch.object(sys, "platform", platform):
            buddy._CARD.update(text="", caret=0)
            event = SimpleNamespace(type="V", ctrl=ctrl, oskey=command, unicode="")
            handled = buddy.BUDDY_OT_expert_card_modal._type_key(None, ctx, event)
            assert handled == expected and buddy._CARD["text"] == ("two words" if expected else "")
buddy.unregister()
print("EXPERT_TARGET_OK", bpy.app.version_string, "selection, scene, no target, rename, manual, file load and paste")
