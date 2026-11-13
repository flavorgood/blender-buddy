"""Blender Buddy survival-section proof (v1.1).

Run with:
  blender -b --factory-startup --python tests/test_survival.py

The "Move around & find things" drawer is the day-1 survival kit:
the research says getting lost - not modelling - is what makes
beginners quit in the first hour. This suite proves the drawer
sits second, holds the nine rescue tools in order, that every
Blender tool it names really exists in this Blender, and that its
two custom rescues do their substance: hidden things come back,
and a scene with no camera gets one where you're looking.
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context

# The drawer exists, sits second, and the old catch-all is gone.
assert bb.SECTIONS[1] == "2. Move around & find things", bb.SECTIONS[:3]
assert not any("Find your way around" in s for s in bb.SECTIONS)
ids = [a["id"] for a in bb.ACTIONS
       if a["section"] == "2. Move around & find things"]
assert ids == ["look_at_picked", "see_everything", "find_everything",
               "look_camera", "camera_here", "walk_mode",
               "look_front", "look_top", "look_side"], ids
print("SURVIVAL_PASS drawer second, nine rescue tools in order")

# Every Blender operator the drawer names really exists here.
# NOTE: hasattr() on bpy.ops proves nothing - bpy.ops invents a
# wrapper for names that were never registered (this is how the
# nonexistent view3d.walk_navigation passed in v1.1 and the button
# shipped broken). The live index is built from the real registry,
# so membership in it is the only honest existence test.
REAL_OPS = {e["idname"] for e in bb.build_index()}
for act in bb.ACTIONS:
    if act["section"] != "2. Move around & find things":
        continue
    if act["kind"] == "op":
        assert act["target"] in REAL_OPS, act["target"]
    if act["kind"] == "custom":
        assert act["target"] in bb._CUSTOM, act["target"]
print("SURVIVAL_PASS every named tool exists in this Blender")

# No duplicate action ids anywhere after the great renumber.
all_ids = [a["id"] for a in bb.ACTIONS]
assert len(all_ids) == len(set(all_ids)), "duplicate action ids"
print(f"SURVIVAL_PASS {len(all_ids)} actions, ids unique")

# Find everything: a hidden object comes back.
bpy.ops.mesh.primitive_cube_add()
cube = ctx.object
cube.hide_viewport = True
cube.hide_set(True)
assert cube.hide_viewport and cube.hide_get()
bpy.ops.buddy.action(action_id="find_everything")
assert not cube.hide_viewport and not cube.hide_get()
print("SURVIVAL_PASS find everything unhides the lost cube")

# Camera here: a scene with no camera gets one.
for obj in list(ctx.scene.objects):
    if obj.type == "CAMERA":
        bpy.data.objects.remove(obj, do_unlink=True)
ctx.scene.camera = None
bpy.ops.buddy.action(action_id="camera_here")
assert ctx.scene.camera is not None
print("SURVIVAL_PASS camera-here gives a cameraless scene a camera")

bb.unregister()
print("ALL SURVIVAL TESTS PASSED")
