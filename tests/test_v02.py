"""Blender Buddy v0.2 proof.

Run with:
  blender -b --factory-startup --python tests/test_v02.py

Checks:
  * 90+ plain-words buttons across all sections
  * EVERY modifier button actually adds its modifier to a real object
  * the complete index covers 2,000+ of Blender's own tools, is
    searchable in plain words, and its Run button executes real tools
  * sculpt mode toggles, keyframes land, exports write real files,
    the picture and save buttons write real files
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
HOME = os.path.expanduser("~")

import blender_buddy as bb  # noqa: E402

bb.register()
print("TEST_PASS register")

count = len(bb.ACTIONS)
print(f"CURATED_ACTIONS {count}")
assert count >= 90, count
sections = {a["section"] for a in bb.ACTIONS}
assert len(sections) >= 12, sections
print("TEST_PASS curated coverage")

# --- the complete index -------------------------------------------------------
index = bb.build_index()
print(f"INDEX_SIZE {len(index)}")
assert len(index) >= 2000, len(index)
hit_ids = [e["idname"] for e in bb.search_index("bevel")]
assert "mesh.bevel" in hit_ids, hit_ids
hit_ids = [e["idname"] for e in bb.search_index("render")]
assert any(h.startswith("render.") for h in hit_ids), hit_ids
print("TEST_PASS complete index + search")


def run(action_id):
    return bpy.ops.buddy.action(action_id=action_id)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


# index Run button executes a real Blender tool
clear()
res = bpy.ops.buddy.run_any(op_id="mesh.primitive_cube_add")
assert "FINISHED" in res and bpy.context.object is not None
print("TEST_PASS index run button")

# --- every modifier button ----------------------------------------------------
clear()
run("add_cube")
cube = bpy.context.object
mod_actions = [a for a in bb.ACTIONS if a["kind"] == "modifier"]
print(f"MODIFIER_ACTIONS {len(mod_actions)}")
failed = []
for act in mod_actions:
    select_only(cube)
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    n_before = len(cube.modifiers)
    res = run(act["id"])
    if "FINISHED" not in res or len(cube.modifiers) != n_before + 1:
        failed.append(act["id"])
    else:
        cube.modifiers.remove(cube.modifiers[-1])
assert not failed, f"modifier buttons failed: {failed}"
print("TEST_PASS every modifier button")

# --- modes, keyframes ---------------------------------------------------------
select_only(cube)
run("start_sculpting")
assert bpy.context.mode == "SCULPT", bpy.context.mode
run("start_sculpting")
assert bpy.context.mode == "OBJECT", bpy.context.mode
print("TEST_PASS sculpt toggle")

run("remember_pose")
assert cube.animation_data and cube.animation_data.action
assert len(cube.animation_data.action.fcurves) >= 3
print("TEST_PASS keyframe")

run("centre_world")
cube.location = (5, 5, 5)
run("centre_world")
assert tuple(cube.location) == (0.0, 0.0, 0.0)
print("TEST_PASS centre world")

# --- finish: exports, picture, save -------------------------------------------
for name in ("blender_buddy_model.glb", "blender_buddy_model.stl",
             "blender_buddy_model.obj", "blender_buddy_picture.png",
             "blender_buddy_my_model.blend"):
    p = os.path.join(HOME, name)
    if os.path.exists(p):
        os.remove(p)

run("send_web")
assert os.path.getsize(os.path.join(HOME, "blender_buddy_model.glb")) > 100
run("send_print")
assert os.path.getsize(os.path.join(HOME, "blender_buddy_model.stl")) > 100
run("send_obj")
assert os.path.getsize(os.path.join(HOME, "blender_buddy_model.obj")) > 100
print("TEST_PASS exports glb/stl/obj")

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 1
scene.render.resolution_x = 64
scene.render.resolution_y = 64
run("take_picture")
assert os.path.getsize(os.path.join(HOME, "blender_buddy_picture.png")) > 1000
print("TEST_PASS take the picture")

run("save_work")
assert os.path.exists(os.path.join(HOME, "blender_buddy_my_model.blend"))
print("TEST_PASS save your work")

bb.unregister()
print("ALL V0.2 TESTS PASSED")
