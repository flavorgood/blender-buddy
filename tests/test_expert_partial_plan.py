"""Native, offline regression for review of a partially executed plan."""
import json
from pathlib import Path
import sys
from unittest import mock

import bpy


assert bpy.app.background and not bpy.app.online_access and not bpy.data.filepath
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as buddy
buddy.register()
context = bpy.context
wm = context.window_manager
cube = context.active_object
assert cube.mode == "OBJECT" and not cube.modifiers
original = json.dumps([{"kind": "button", "id": "round_all_edges"},
                       {"kind": "tool", "id": "mesh.subdivide"}])
settings = {"service": "LOCAL", "url": "http://localhost:11434/v1/chat/completions"}


def offer_original(already_retried):
    wm.buddy_plan = original
    wm.buddy_plan_summary = "Bevel edges, then subdivide."
    wm.buddy_plan_retried = "1" if already_retried else ""
    buddy._EXPERT_JOB["reviewed_target"] = (original, buddy._expert_selection(context))


with mock.patch.object(buddy, "_expert_settings", return_value=settings):
    for ready, retried in ((False, False), (True, True), (True, False)):
        offer_original(retried)
        count = len(cube.modifiers)
        with mock.patch.object(buddy, "_expert_ready", return_value=ready), \
                mock.patch.object(buddy, "_ask_ai", return_value="No revised plan.") as provider:
            assert bpy.ops.buddy.run_plan() == {"CANCELLED"}
            assert len(cube.modifiers) == count + 1 and cube.modifiers[-1].type == "BEVEL"
            assert not wm.buddy_plan and buddy._EXPERT_JOB["reviewed_target"] is None
            assert "Stopped at step 2 of 2" in wm.buddy_plan_report
            assert bpy.ops.buddy.run_plan() == {"CANCELLED"} and len(cube.modifiers) == count + 1
            assert provider.call_count == int(ready and not retried)

    # Even when a replacement is available, it requires a new explicit Run.
    offer_original(False)
    count = len(cube.modifiers)
    with mock.patch.object(buddy, "_expert_ready", return_value=True), mock.patch.object(
            buddy, "_ask_ai", return_value="SUMMARY: Smooth\nSTEP: tool:object.shade_smooth"):
        assert bpy.ops.buddy.run_plan() == {"CANCELLED"}
    assert wm.buddy_plan and wm.buddy_plan != original
    assert buddy._EXPERT_JOB["reviewed_target"] == (wm.buddy_plan, buddy._expert_selection(context))
    assert not any(p.use_smooth for p in cube.data.polygons)
    assert bpy.ops.buddy.run_plan() == {"FINISHED"} and len(cube.modifiers) == count + 1
    assert all(p.use_smooth for p in cube.data.polygons)
buddy.unregister()
print("EXPERT_PARTIAL_PLAN_OK", bpy.app.version_string, "offline, retried, unavailable and successful replans")
