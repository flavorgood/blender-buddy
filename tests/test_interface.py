"""Blender Buddy v3 interface proof: Buddy inside Blender itself.

Proves the machinery of the complete redesign: every step of
every job has a screen it conducts to; the pie operator and
its key exist; Buddy's plain-words tools are registered in
Blender's OWN toolbar table; the header hook and the
step-watching handler are in place; and the template source
ships with the add-on. The screens themselves (built from a
real window) are proven by the GUI screenshots - a headless
run has no window to rearrange, and this suite says so rather
than pretending otherwise.

Run: blender -b --factory-startup --python tests/test_interface.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bpy  # noqa: E402
import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context

# --- every step of every job conducts to a real Buddy screen ----
assert bb.BUDDY_SCREENS == ("Buddy Start", "Buddy Model",
                            "Buddy Look", "Buddy Finish")
for pkg in bb.PACKAGES:
    for i, step in enumerate(pkg["steps"]):
        spec = bb._STEP_SCREENS.get((pkg["id"], i))
        assert spec is not None, (pkg["id"], i, step["title"])
        assert spec[0] in bb.BUDDY_SCREENS, spec
print("INTERFACE_PASS every step of every job has a screen")

# --- the pie: operator, menu, and the ` key -----------------------
assert hasattr(bpy.ops.buddy, "pie")
assert hasattr(bpy.ops.buddy, "build_screens")
km = ctx.window_manager.keyconfigs.addon.keymaps.get("3D View")
items = [i for k in ctx.window_manager.keyconfigs.addon.keymaps
         for i in k.keymap_items if i.idname == "buddy.pie"]
assert items and items[0].type == "ACCENT_GRAVE", items
print("INTERFACE_PASS pie operator + ` keymap in place")

# --- Buddy's tools live in Blender's own toolbar table ------------
ids = bb._known_tool_ids()
assert ids is not None
for tid in ("buddy.extrude", "buddy.loop_cut", "buddy.knife"):
    assert tid in ids, tid
print("INTERFACE_PASS plain-words tools registered in Blender's "
      "own toolbar (Edit Mode)")

# --- step watcher (the header button is proven by the GUI shots -
# Blender exposes no read-back list of appended header draws) ------
assert bb._conduct_check in bpy.app.handlers.depsgraph_update_post
print("INTERFACE_PASS step watcher is on the depsgraph handler")

# --- conducting is safe with no window (headless) ------------------
bb._conduct_check()          # must not raise
assert bb._conduct_apply() is None
print("INTERFACE_PASS conducting no-ops cleanly without a window")

# --- template source ships beside the add-on -----------------------
src = bb._template_source()
if src is not None:
    assert os.path.isfile(os.path.join(
        src, "__init__.py")), "template needs its __init__.py"
    print("INTERFACE_PASS template source present:", src)
else:
    print("INTERFACE_PASS no bundled template beside this copy "
          "(single-file install) - install step will skip it")

# --- Start screen + step strip live at the top of the main panel --
# (Blender would not promise a second top-level panel above the
# main one, so both draw as the main panel's first content.)
assert hasattr(bb, "_draw_start") and hasattr(bb, "_draw_strip")
names = [c.__name__ for c in bb.CLASSES]
assert "VIEW3D_PT_buddy_strip" not in names
assert "VIEW3D_PT_buddy_start" not in names
print("INTERFACE_PASS Start screen + step strip draw inside the "
      "main panel")

# --- the Start screen states the honest scope, up high ------------
# (Owner, 2026-11-19: Buddy's scope is stated where learners see
# it - what is covered, what is a first piece, and what is not
# taught yet. Sculpting's first piece arrived in v3.3.0; animation
# and the other crafts remain untaught and must say so.) Drive the
# real draw path with a recording layout and read back what a
# learner would read: the coverage box must be drawn, carry the
# truths, and sit BEFORE the package shelf - visible without
# expanding or scrolling past the jobs.
class _FakeOp:
    pass


class _FakeLayout:
    def __init__(self, events):
        self._events = events

    def label(self, text="", icon="NONE"):
        self._events.append(("label", text))

    def box(self):
        self._events.append(("box", None))
        return _FakeLayout(self._events)

    def operator(self, idname, text="", icon="NONE"):
        self._events.append(("op", text))
        return _FakeOp()


_events = []
bb._draw_start(_FakeLayout(_events), ctx)
_labels = [t for kind, t in _events if kind == "label"]
_joined = " ".join(_labels)
assert bb._COVERAGE_TITLE in _labels, _labels
for _line in bb._COVERAGE_LINES:
    assert " ".join(_line.split()) in " ".join(_joined.split()), _line
assert "Sculpting has its first guided piece" in _joined, _joined
assert "not the whole of it" in _joined, _joined
assert "Animation and the other crafts are not taught yet" in _joined, _joined
assert "one at a time" in _joined, _joined
_title_at = _events.index(("label", bb._COVERAGE_TITLE))
_first_pkg_at = next(i for i, (kind, t) in enumerate(_events)
                     if kind == "op" and t.startswith("Start:"))
assert _title_at < _first_pkg_at, "coverage box must precede the shelf"
print("INTERFACE_PASS Start screen draws the honest coverage box "
      "before the package shelf")

# --- the hint tells the truth about the picked thing ---------------
bpy.ops.mesh.primitive_cube_add()
cube = ctx.object
assert "start shaping" in bb._hint(ctx).lower()
bpy.ops.object.light_add(type="SUN")
hint = bb._hint(ctx)
assert "shines" in hint and "shaping" not in hint.lower(), hint
bpy.ops.object.camera_add()
hint = bb._hint(ctx)
assert "picture" in hint and "shaping" not in hint.lower(), hint
assert "section" not in hint.lower(), hint
print("INTERFACE_PASS the hint is per-kind and never impossible")

# --- conducting never fires mid-build ------------------------------
bb._BUILDING = True
bb._CONDUCT["key"] = None
bb._conduct_check()
assert bb._CONDUCT["key"] is None, "key must stay unconsumed"
assert bb._conduct_apply() is None
bb._BUILDING = False
print("INTERFACE_PASS conducting stays out of a running build")

bb.unregister()
assert bb._conduct_check not in bpy.app.handlers.depsgraph_update_post
ids = bb._known_tool_ids()
assert "buddy.extrude" not in (ids or set()), "tools must leave with Buddy"
print("INTERFACE_PASS unregister removes the furniture too")
print("ALL INTERFACE TESTS PASSED")
