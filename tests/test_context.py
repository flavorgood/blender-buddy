"""Blender Buddy v2.0 context tests: the redesign rule - "no
need for tools that are not needed or not usable at the moment".

Proves: tools appear only when the scene/mode/picked thing can
actually use them; the "For right now" deck follows the
moment; empty drawers hide; the Donut lives in its own drawer
now; the floating card is off by default; and Codex is found
wherever it landed, with a Test button that reports plainly.

Run: blender -b --factory-startup --python tests/test_context.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bpy  # noqa: E402
import blender_buddy as bb  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=False)
bb.register()
ctx = bpy.context
A = bb.ACTIONS_BY_ID

def avail(aid):
    return bb._action_available(A[aid], ctx)

# --- empty scene: only starting tools exist ----------------------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
ctx.view_layer.update()
assert ctx.object is None
assert avail("add_cube"), "add tools show with nothing picked"
assert avail("see_everything") and avail("take_picture")
assert not avail("tool_move"), "no move tool with nothing picked"
assert not avail("mirror_it"), "no modifiers with nothing picked"
assert not avail("pull_face"), "no edit tools outside Edit Mode"
deck = bb._now_deck(ctx)
assert deck and deck[0]["id"] == "add_cube", [d["id"] for d in deck]
print("CONTEXT_PASS empty scene: deck starts with adding, "
      f"{len(bb._available_actions(ctx))} of {len(bb.ACTIONS)} tools shown")

# --- a mesh picked, Object Mode: shaping/modifier tools appear ---
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = ctx.object
assert cube and cube.type == "MESH"
assert avail("tool_move") and avail("start_shaping")
assert avail("mirror_it"), "modifiers show for a picked mesh"
assert avail("give_colour")
assert not avail("pull_face"), "edit tools wait for Edit Mode"
assert not avail("make_permanent"), "nothing to make permanent yet"
assert not avail("glue_together"), "glue needs two picked things"
deck = bb._now_deck(ctx)
assert deck[0]["id"] == "tool_move", [d["id"] for d in deck]
shape = bb._section_actions("4. Shape it", ctx)
assert [a["id"] for a in shape] == ["start_shaping"], [a["id"] for a in shape]
print("CONTEXT_PASS object mode: deck leads with move, "
      "shape drawer holds only the way in")

# --- a modifier appears -> make_permanent becomes usable ---------
bpy.ops.buddy.action(action_id="make_smoother")
assert len(cube.modifiers) == 1
assert avail("make_permanent"), "apply shows once a modifier exists"

# --- two picked -> glue and hole-cutting appear ------------------
bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 0))
bpy.ops.object.select_all(action="SELECT")
assert len(ctx.selected_objects) == 2
assert avail("glue_together") and avail("cut_hole")
print("CONTEXT_PASS two picked: combine tools appear")

# --- Edit Mode: the shaping bench appears, the rest steps back ---
bpy.ops.object.mode_set(mode="EDIT")
assert avail("pull_face") and avail("loop_cut") and avail("fix_faces")
assert not avail("add_cube"), "add-shape steps back while shaping"
assert avail("mirror_it"), "modifiers genuinely work while editing a mesh"
deck = bb._now_deck(ctx)
assert deck[0]["id"] == "pull_face", [d["id"] for d in deck]
bpy.ops.object.mode_set(mode="OBJECT")
print("CONTEXT_PASS edit mode: deck leads with shaping tools")

# --- Sculpt Mode: the object-level tools step back ----------------
bpy.ops.object.mode_set(mode="SCULPT")
assert not avail("mirror_it"), "modifiers step back while sculpting"
assert avail("paint_it"), "painting is one step from sculpting"
bpy.ops.object.mode_set(mode="OBJECT")
print("CONTEXT_PASS sculpt mode: only the sculpt bench remains")

# --- a camera picked: mesh tools vanish --------------------------
bpy.ops.object.camera_add(location=(4, -4, 3))
cam = next(o for o in ctx.scene.objects if o.type == "CAMERA")
bpy.ops.object.select_all(action="DESELECT")
cam.select_set(True)
ctx.view_layer.objects.active = cam
assert not avail("mirror_it") and not avail("start_shaping")
assert not avail("give_colour")
print("CONTEXT_PASS camera picked: mesh tools are gone")

# --- the Donut is a drawer now, not a fixture --------------------
names = [c.__name__ for c in bb.CLASSES]
assert "VIEW3D_PT_buddy_projects" in names
cls = next(c for c in bb.CLASSES if c.__name__ == "VIEW3D_PT_buddy_projects")
assert "DEFAULT_CLOSED" in cls.bl_options
src = open(os.path.join(os.path.dirname(__file__), "..",
                        "blender_buddy", "__init__.py")).read()
main_draw = src.split("class VIEW3D_PT_blender_buddy")[1].split("def _make_section_panel")[0]
assert 'text="Learn by doing: guided projects"' not in main_draw, \
    "project shelf still drawn at the top of the main panel"
print("CONTEXT_PASS donut demoted to its own closed drawer")

# --- floating card off by default --------------------------------
prop = bb.BUDDY_Preferences.__annotations__["expert_float"]
assert prop.keywords["default"] is False, "floating card should default off"
print("CONTEXT_PASS floating card off by default")

# --- Codex: found wherever it landed, Test reports plainly -------
real_which = bb.shutil.which
bb.shutil.which = lambda name: "/usr/bin/codex" if name == "codex" else None
assert bb._find_codex() == "/usr/bin/codex"
assert bb._expert_ready({"service": "CODEX"}) is True
bb.shutil.which = lambda name: None
assert bb._find_codex() is None
assert bb._expert_ready({"service": "CODEX"}) is False
real_settings = bb._expert_settings
bb._expert_settings = lambda: {"key": "", "url": "", "model": "",
                               "float": False, "service": "CODEX"}

res = bpy.ops.buddy.test_expert()
bb._expert_settings = real_settings
bb.shutil.which = real_which
assert res == {"FINISHED"}
status = ctx.window_manager.buddy_expert_status
assert "couldn't locate" in status, status
print("CONTEXT_PASS codex test button:", status[:70])

bb.unregister()
print("ALL CONTEXT TESTS PASSED")
