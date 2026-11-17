"""Blender Buddy v3.1 plain-words layer proof.

The redesign is for the average person, and the gaps are the
concepts Blender never explains - modes, the origin, the 3D
cursor, picked vs in-charge. This suite proves: the
where-you-are line speaks plain words for every mode that
matters and never hides behind Blender's bare mode names; the
traps (spin point far from the thing, target far away, size
not locked in, mirror flip, everything hidden) are detected
from the live scene; each fix operator removes its trap; and
"Got it" mutes one trap without muting another thing's.

Run: blender -b --factory-startup --python tests/test_plain_layer.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context


def wipe():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    ctx.scene.cursor.location = (0.0, 0.0, 0.0)
    ctx.window_manager.buddy_muted = "[]"


def keys():
    return [t["key"] for t in bb._traps(ctx)]


# --- the where-you-are line, in plain words -------------------
wipe()
headline, sub = bb._where_am_i(ctx)
assert "whole things" in headline and "Object Mode" not in headline
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
headline, sub = bb._where_am_i(ctx)
assert "whole things" in headline and "Cube" in headline, headline
bpy.ops.object.mode_set(mode="EDIT")
headline, sub = bb._where_am_i(ctx)
assert "reshaping" in headline and "tools changed" in sub, headline
assert "Edit Mode" not in headline
bpy.ops.buddy.mode_back()
assert ctx.mode == "OBJECT"
headline, sub = bb._where_am_i(ctx)
assert "whole things" in headline
bpy.ops.object.mode_set(mode="SCULPT")
headline, sub = bb._where_am_i(ctx)
assert "sculpting" in headline and "clay" in sub, headline
bpy.ops.object.mode_set(mode="OBJECT")
print("PLAIN_PASS where-you-are line: modes in plain words, way back works")

# picked vs in-charge
bpy.ops.mesh.primitive_cube_add(location=(3, 0, 0))
other = ctx.object
cube.select_set(True)
ctx.view_layer.objects.active = cube
headline, sub = bb._where_am_i(ctx)
assert "in charge" in headline and "2 things are picked" in sub, headline
print("PLAIN_PASS picked vs in-charge is said out loud")

# --- baseline: a plain cube in the middle trips nothing -------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
assert bb._visible_traps(ctx) == [], bb._visible_traps(ctx)
print("PLAIN_PASS a plain cube in the middle trips no traps")

# --- the spin point, sitting away from the thing ---------------
cube.data.transform(Matrix.Translation((3.0, 0.0, 0.0)))
ctx.view_layer.update()
assert any(k.startswith("origin_far|") for k in keys()), keys()
trap = next(t for t in bb._traps(ctx)
            if t["key"].startswith("origin_far|"))
assert "spin point" in trap["text"] and "orange dot" in trap["text"]
bpy.ops.buddy.origin_center()
ctx.view_layer.update()
centre, size, lo, hi = bb._bbox_world(cube)
assert (cube.matrix_world.translation - centre).length < 0.01
assert not any(k.startswith("origin_far|") for k in keys())
print("PLAIN_PASS spin-point trap fires, and the middle fix clears it")

# spin point at the bottom
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
tall = ctx.object
tall.data.transform(Matrix.Translation((0.0, 0.0, 2.0)))
ctx.view_layer.update()
bpy.ops.buddy.origin_bottom()
ctx.view_layer.update()
centre, size, lo, hi = bb._bbox_world(tall)
assert abs(tall.matrix_world.translation.z - lo.z) < 0.01
assert abs(lo.z - 1.0) < 0.01, lo  # the thing itself never moved
assert tuple(ctx.scene.cursor.location) == (0.0, 0.0, 0.0)
print("PLAIN_PASS spin point to the bottom; the thing and the target stay put")

# --- the target, a long way from the middle ----------------------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
ctx.scene.cursor.location = (10.0, 0.0, 0.0)
assert "cursor_far" in keys(), keys()
trap = next(t for t in bb._traps(ctx) if t["key"] == "cursor_far")
assert "target" in trap["text"] and "red-and-white" in trap["text"]
bpy.ops.buddy.cursor_to_picked()
assert (ctx.scene.cursor.location
        - cube.matrix_world.translation).length < 0.001
assert "cursor_far" not in keys()
ctx.scene.cursor.location = (9.0, 9.0, 9.0)
bpy.ops.buddy.cursor_home()
assert tuple(ctx.scene.cursor.location) == (0.0, 0.0, 0.0)
print("PLAIN_PASS target trap fires; both target fixes land")

# --- size stretched but not locked in ------------------------------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
cube.scale = (2.0, 1.0, 1.0)
assert any(k.startswith("scale_open|") for k in keys()), keys()
bpy.ops.buddy.lock_in()
assert all(abs(s - 1.0) < 0.001 for s in cube.scale), cube.scale
assert cube.dimensions.x > 3.9, cube.dimensions  # the size it showed
assert not any(k.startswith("scale_open|") for k in keys())
print("PLAIN_PASS unlocked-size trap fires; locking in keeps the shown size")

# --- the mirror flip ------------------------------------------------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
cube.scale = (-1.0, 1.0, 1.0)
assert any(k.startswith("mirrored|") for k in keys()), keys()
print("PLAIN_PASS the minus-size flip has its own plain warning")

# --- everything hidden ------------------------------------------------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
a = ctx.object
bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
b = ctx.object
for o in (a, b):
    o.hide_viewport = True
    o.hide_set(True)
assert "all_hidden" in keys(), keys()
bpy.ops.buddy.show_everything()
assert bb._is_shown(a) and bb._is_shown(b)
assert "all_hidden" not in keys()
print("PLAIN_PASS everything-hidden trap fires; show everything clears it")

# --- "Got it" mutes one trap, not the next thing's ---------------------
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
first = ctx.object
first.data.transform(Matrix.Translation((3.0, 0.0, 0.0)))
bpy.ops.mesh.primitive_cube_add(location=(0, 4, 0))
second = ctx.object
second.data.transform(Matrix.Translation((3.0, 0.0, 0.0)))
ctx.view_layer.update()
ctx.view_layer.objects.active = first
trap = next(t for t in bb._visible_traps(ctx)
            if t["key"].startswith("origin_far|"))
bpy.ops.buddy.mute_trap(trap_key=trap["key"])
assert trap["key"] not in [t["key"] for t in bb._visible_traps(ctx)]
assert trap["key"] in keys()  # still true of the scene - just muted
ctx.view_layer.objects.active = second
assert any(t["key"].startswith("origin_far|")
           for t in bb._visible_traps(ctx))
print("PLAIN_PASS 'Got it' mutes that thing's warning, not the next one's")

print("ALL PLAIN-LAYER TESTS PASSED")
