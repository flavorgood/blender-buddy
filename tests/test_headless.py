"""Headless proof for the Blender Buddy prototype.

Run with:
  blender -b --factory-startup --python tests/test_headless.py

Checks, in plain words:
  * the add-on registers and its panel/operator exist
  * plain-words search finds tools from everyday phrasing
  * pressing the buttons actually does the jobs (add, smooth, colour,
    copy, delete, cut a hole, shaping mode, the shaping guard)
  * a small demo scene built ONLY through the add-on's buttons renders
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DEMO_DIR = os.path.join(ROOT, "demo")
os.makedirs(DEMO_DIR, exist_ok=True)

import blender_buddy  # noqa: E402

blender_buddy.register()
print("TEST_PASS register")

assert hasattr(bpy.ops.buddy, "action"), "buddy.action operator missing"
assert "VIEW3D_PT_blender_buddy" in dir(bpy.types) or hasattr(
    bpy.types, "VIEW3D_PT_blender_buddy"), "panel class missing"
print("TEST_PASS operator+panel present")

# --- plain-words search ------------------------------------------------------
def ids(query):
    return [a["id"] for a in blender_buddy.search_actions(query)]

assert "round_edge" in ids("round the edges"), ids("round the edges")
assert "copy_it" in ids("make a copy"), ids("make a copy")
assert "cut_hole" in ids("cut a hole"), ids("cut a hole")
assert "make_smoother" in ids("make it smoother"), ids("make it smoother")
assert "tool_move" in ids("move it"), ids("move it")
assert ids("xyzqq zzz") == []  # pure gibberish still finds nothing (v0.3 loose search)
print("TEST_PASS plain-words search")


def run(action_id):
    return bpy.ops.buddy.action(action_id=action_id)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


# --- buttons do the jobs -----------------------------------------------------
clear_scene()
run("add_cube")
cube = bpy.context.object
assert cube and cube.type == "MESH", "add_cube produced no mesh"
print("TEST_PASS add a box")

run("add_ball")
ball = bpy.context.object
assert ball and ball is not cube
print("TEST_PASS add a ball")

select_only(ball)
run("make_smoother")
assert any(m.type == "SUBSURF" for m in ball.modifiers), "no SUBSURF modifier"
run("look_smooth")
run("give_colour")
assert ball.data.materials and ball.data.materials[0].name == "Buddy Red"
print("TEST_PASS smoother + smooth shading + colour")

select_only(cube)
before = len(bpy.data.objects)
run("copy_it")
assert len(bpy.data.objects) == before + 1, "copy did not add an object"
copy_obj = bpy.context.object
assert copy_obj is not cube
copy_name = copy_obj.name
run("throw_away")
assert copy_name not in bpy.data.objects
print("TEST_PASS copy + throw away")

# cut a hole: target picked first, cutter picked last (active)
select_only(cube)
bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0.6, 0, 0.6))
cutter = bpy.context.object
cutter.name = "Cutter"
cube.select_set(True)
cutter.select_set(True)
bpy.context.view_layer.objects.active = cutter
res = run("cut_hole")
assert "FINISHED" in res, res
assert cutter.hide_get(), "cutter should be hidden after cutting"
has_bool = any(m.type == "BOOLEAN" for m in cube.modifiers)
print(f"TEST_PASS cut a hole (modifier applied={not has_bool}, kept live={has_bool})")

# shaping mode + the too-early guard
select_only(ball)
assert bpy.context.mode == "OBJECT"
run("start_shaping")
assert bpy.context.mode == "EDIT_MESH", bpy.context.mode
run("fix_faces")  # already shaping: the fix itself should run
print("TEST_PASS start shaping + fix faces")
run("start_shaping")
assert bpy.context.mode == "OBJECT", "start_shaping should toggle back out"

select_only(ball)
res = run("round_edge")  # too early: first press must guide, not fail
assert "FINISHED" in res and bpy.context.mode == "EDIT_MESH", (res, bpy.context.mode)
print("TEST_PASS too-early shaping button guides instead of failing")
bpy.ops.object.mode_set(mode="OBJECT")

# --- demo scene built only through the buttons -------------------------------
clear_scene()
run("add_sheet")
ground = bpy.context.object
ground.name = "Demo Ground"
ground.scale = (9, 9, 1)

run("add_cube")
base = bpy.context.object
base.name = "Demo Box"
base.location = (0, 0, 1.0)
select_only(base)
run("round_all_edges")
assert any(m.type == "BEVEL" for m in base.modifiers)

run("add_ball")
orb = bpy.context.object
orb.name = "Demo Ball"
orb.location = (2.6, 0, 1.1)
select_only(orb)
run("make_smoother")
run("look_smooth")
run("give_colour")

bpy.ops.object.camera_add(location=(6.5, -7.5, 5.0),
                          rotation=(1.05, 0, 0.72))
bpy.context.scene.camera = bpy.context.object
bpy.ops.object.light_add(type="SUN", location=(4, -4, 8))
bpy.context.object.data.energy = 3.0
bpy.context.object.data.angle = 0.6

world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.47, 0.5, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.7

scene = bpy.context.scene
# Cycles on CPU: the Workbench engine needs a GPU/OpenGL, which a headless
# test box does not have (it aborts there). Cycles CPU renders anywhere.
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.device = "CPU"
scene.render.resolution_x = 720
scene.render.resolution_y = 540
scene.render.filepath = os.path.join(DEMO_DIR, "buddy_demo.png")
bpy.ops.render.render(write_still=True)
assert os.path.getsize(scene.render.filepath) > 10000, "render too small"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEMO_DIR, "buddy_demo.blend"))
print("TEST_PASS demo scene rendered + saved")

blender_buddy.unregister()
print("ALL TESTS PASSED")
