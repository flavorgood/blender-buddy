"""Offline Blender regression for Expert action and native-tool boundaries.

Run with blender --background --factory-startup --offline-mode --python-exit-code 19
--python tests/test_expert_guard.py.
The fixture intercepts provider calls, filesystem actions and dangerous operators.
"""
import json
import sys
from pathlib import Path
from unittest import mock

import bpy

assert bpy.app.background and not bpy.data.filepath
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as buddy

def fail_call(*args, **kwargs):
    raise AssertionError("The guard dispatched a forbidden operation.")

for cls in (buddy.BUDDY_OT_action, buddy.BUDDY_OT_run_plan):
    bpy.utils.register_class(cls)
wm = bpy.context.window_manager
for field in ("buddy_plan", "buddy_plan_summary", "buddy_plan_report",
              "buddy_suggested", "buddy_answer", "buddy_ask", "buddy_plan_retried"):
    if not hasattr(bpy.types.WindowManager, field):
        setattr(bpy.types.WindowManager, field, bpy.props.StringProperty())
buddy._ask_ai = fail_call
buddy._expert_ready = lambda settings: False
manual = {"throw_away", "save_work", "send_web", "send_print", "send_obj", "take_picture"}
denied = {"object.delete", "scene.delete", "wm.save_mainfile", "wm.open_mainfile",
          "wm.quit_blender", "wm.obj_export", "screen.back_to_previous",
          "object.multires_external_save", "scene.freestyle_module_open", "object.volume_import"}
assert manual <= buddy.ACTIONS_BY_ID.keys()
assert not (manual & buddy._expert_buttons().keys())
assert not (denied & buddy._plan_tools().keys())
assert {"add_cube", "reshape_as_circle"} <= buddy._expert_buttons().keys()
assert {"object.shade_smooth", "mesh.subdivide"} <= buddy._plan_tools().keys()
prompts = (buddy._expert_agent_prompt(bpy.context), buddy._expert_system_prompt())
for handle in manual:
    assert all(f"{handle} =" not in prompt for prompt in prompts)
    assert not buddy._extract_suggestion("Do this.\nBUTTON: " + handle)[1]
for ident in denied:
    assert (ident + " =") not in prompts[0]
for kind, cases in (("button", manual), ("tool", denied)):
    for identifier in cases:
        summary, steps, dropped = buddy._parse_plan(f"SUMMARY: Test\nSTEP: {kind}:{identifier}")
        assert not steps and dropped == 1, (identifier, steps, dropped)
        # A previous release could persist this plan in an open file.
        # Include one valid operation before it to catch partial execution.
        wm.buddy_plan = json.dumps([{"kind": "button", "id": "add_cube"}, {"kind": kind, "id": identifier}])
        before = set(o.as_pointer() for o in bpy.data.objects)
        with mock.patch.object(buddy, "_resolve_op", side_effect=fail_call), mock.patch.dict(
                buddy._CUSTOM, {name: fail_call for name in buddy._EXPERT_MANUAL_ACTIONS}):
            assert bpy.ops.buddy.run_plan() == {"CANCELLED"}
        assert set(o.as_pointer() for o in bpy.data.objects) == before and not wm.buddy_plan
        assert "unavailable" in wm.buddy_answer
summary, steps, dropped = buddy._parse_plan("SUMMARY: Smooth\nSTEP: tool:object.shade_smooth")
assert dropped == 0 and len(steps) == 1
wm.buddy_plan = json.dumps(steps)
wm.buddy_plan_summary = summary
assert bpy.ops.buddy.run_plan() == {"FINISHED"}
assert all(poly.use_smooth for poly in bpy.context.object.data.polygons)
with mock.patch.dict(buddy._CUSTOM, {"delete_object": lambda context: {"FINISHED"}}):
    # No deletion occurs: the direct shortcut must still reach the harmless test handler.
    assert bpy.ops.buddy.action(action_id="throw_away") == {"FINISHED"}
print(f"EXPERT_GUARD_OK Blender {bpy.app.version_string}, {len(manual)} curated, {len(denied)} raw")
