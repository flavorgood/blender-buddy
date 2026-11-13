"""Blender Buddy guided-project proof (the Donut package).

Run with:
  blender -b --factory-startup --python tests/test_tour.py

The donut package is the follow-along companion to Blender
Guru's NEW series ("Blender Donut Tutorial (2025)", Blender
5.0): one step per part, the video teaches, Buddy orients and
verifies. The projects TEACH: every step carries plain-words
instructions for doing it by hand in real Blender, names the
skill it teaches, and says what the scene is still missing.
There is no "do this step" button in the panel - the learner
does the work. This suite proves the other half: that each
step's scene check (the same checks the panel ticks from) is
satisfied by the step's reference build, and that no step's
check fires on the previous step's scene.

Part 7's Scatter on Surface modifier only exists in Blender
5.0+, so on older Blender this suite proves steps 1-6 and 8
by their reference builds, and proves step 7's check answers
False - quietly, without an error - there.
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context

assert hasattr(bpy.ops.buddy, "tour_start")
assert hasattr(bpy.ops.buddy, "tour_do")
print("TOUR_PASS operators present")

# The teaching contract: every step of every package explains how
# to do it by hand, names the skill, and says what is missing.
for pkg in bb.PACKAGES:
    assert pkg["steps"], pkg["id"]
    for step in pkg["steps"]:
        assert len(step["teach"]) >= 2, step["title"]
        assert all(isinstance(l, str) and l.strip() for l in step["teach"])
        assert step["skill"].strip() and step["missing"].strip()
print("TOUR_PASS every step teaches, names its skill, names what's missing")

# The panel must not offer to do the step - teaching is the point.
src = open(os.path.join(ROOT, "blender_buddy", "__init__.py")).read()
assert 'text="Do this step"' not in src
print("TOUR_PASS no do-it-for-you button in the panel")

# Every donut step carries its own part of the series: a real
# watch link, labelled in plain words, a different video per part.
donut = bb.PACKAGES_BY_ID["donut"]
video_urls = []
for step in donut["steps"]:
    video = step.get("video") or {}
    assert video.get("url", "").startswith(
        "https://www.youtube.com/watch?v="), step["title"]
    assert video.get("label", "").strip(), step["title"]
    video_urls.append(video["url"])
assert len(set(video_urls)) == 8, video_urls
print("TOUR_PASS every donut step links to its own video part")

HAS_SCATTER = bpy.app.version >= (5, 0, 0)

# The scatter check is safe where the feature does not exist:
# an icing with no scatter modifier answers False, not an error,
# on every version.
bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=12)
probe = ctx.object
probe.name = "Icing"
assert bb._check_scatter(ctx) is False
print("TOUR_PASS scatter check answers False (no error) "
      "without the modifier")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context

# fresh scene state: nothing proven yet
checks, current = bb.tour_state(ctx)
assert checks == [False] * 8 and current == 0, checks
print("TOUR_PASS empty scene proves nothing")

bpy.ops.buddy.tour_start(package="donut")
assert ctx.scene.buddy_tour_started is True
assert ctx.scene.buddy_tour_package == "donut"

# Test-box accommodation only: this GPU-less machine cannot run the
# EEVEE engine at all (it aborts), so the tour's picture steps render
# with Cycles here. On a real computer the default engine just works.
ctx.scene.render.engine = "CYCLES"
ctx.scene.cycles.samples = 16
ctx.scene.render.resolution_x = 320
ctx.scene.render.resolution_y = 240

steps = bb.TOUR_STEPS
for i in range(8):
    if i == 6 and not HAS_SCATTER:
        # Part 7's check-only behaviour on pre-5.0 Blender: the
        # step cannot tick, its check answers False without an
        # error, and the reference build declines in plain words
        # (tour_do reports it and cancels - nothing changes).
        checks, current = bb.tour_state(ctx)
        assert current == 6, checks
        assert bb._check_scatter(ctx) is False
        bpy.ops.buddy.tour_do(step=6)
        checks, current = bb.tour_state(ctx)
        assert current == 6 and not checks[6], checks
        print("TOUR_PASS step 7: Scatter on Surface waits for "
              "Blender 5.0 on this version")
        continue
    if i != 7 or HAS_SCATTER:
        checks, current = bb.tour_state(ctx)
        assert current == i, \
            f"before step {i}: state {checks}, current {current}"
    bpy.ops.buddy.tour_do(step=i)
    checks, current = bb.tour_state(ctx)
    assert checks[i], f"step {i} ({steps[i]['title']}) not proven: {checks}"
    print(f"TOUR_PASS step {i + 1}: {steps[i]['title']}")

checks, current = bb.tour_state(ctx)
if HAS_SCATTER:
    assert current == 8 and all(checks), checks
    print("TOUR_PASS all 8 steps proven by the scene")
else:
    assert checks[:6] == [True] * 6 and checks[6] is False \
        and checks[7] is True, checks
    print("TOUR_PASS steps 1-6 and 8 proven; step 7 awaits Blender 5.0")

scene = ctx.scene
names = {o.name for o in scene.objects}
assert {"Cup", "Mug", "Dough", "Icing", "Plate", "Table",
        "Coffee Foam"} <= names, names
assert "Cube" not in names, "the starter cube should be gone"
print("TOUR_PASS starter cube cleared, cup, mug and donut all present")

icing = scene.objects["Icing"]
assert any(m.type == "SOLIDIFY" for m in icing.modifiers)
assert any(m.type == "SHRINKWRAP" and m.target is scene.objects["Dough"]
           for m in icing.modifiers)
print("TOUR_PASS icing thickened and shrink-wrapped onto the dough")

mug = scene.objects["Mug"]
assert any(e.use_seam for e in mug.data.edges), "mug needs its seams"
foam = scene.objects["Coffee Foam"]
assert foam.data.materials and foam.data.materials[0] is not None
print("TOUR_PASS mug seamed for its unwrap, coffee foam in place")

if HAS_SCATTER:
    assert any(m.type == "NODES" and m.node_group is not None
               and "Scatter on Surface" in m.node_group.name
               for m in icing.modifiers)
    coll = bpy.data.collections.get("Sprinkle Types")
    assert coll is not None and len(coll.objects) >= 2
    assert icing.vertex_groups.get("Sprinkles") is not None
    print("TOUR_PASS scatter modifier, sprinkle variants and "
          "painted guide all present")

# Render the keepsake picture through the tour's own camera and
# lighting - the framing the beginner actually gets.
assert scene.camera is not None
scene.render.engine = "CYCLES"
scene.cycles.samples = 48
scene.render.resolution_x = 640
scene.render.resolution_y = 480
out = os.path.join(ROOT, "demo", "buddy_donut.png")
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
assert os.path.exists(out) and os.path.getsize(out) > 10000
print(f"TOUR_PASS donut rendered: {out}")

blend_out = os.path.join(ROOT, "demo", "buddy_donut.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"TOUR_PASS donut scene saved: {blend_out}")

# The wired colour maps must hold real pixels, not black -
# wiring alone once passed while every texture was empty (a
# colours-space change after the pixel write silently reset
# the buffers on both Blender versions).
_icing = bpy.data.objects["Icing"]
_bsdf = next(n for m in _icing.data.materials if m and m.use_nodes
             for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_tex = _bsdf.inputs["Base Color"].links[0].from_node.image
_px = list(_tex.pixels)
_reds = _px[0::4]
assert sum(_reds) / len(_reds) > 0.1, "icing colour map is black"
print("TOUR_PASS texture pixels: the icing colour map holds "
      "real colour, not an empty buffer")

# --- interrupt and resume ---------------------------------------
# Progress is the scene, nothing else: build two steps, save,
# reload the file fresh, and the tour must read its place back
# from the scene alone - steps 1-2 still ticked, the card
# resuming at step 3 (index 2).
import tempfile

bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="donut")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
checks, current = bb.tour_state(ctx)
assert checks[:2] == [True, True] and current == 2, checks
resume_path = os.path.join(tempfile.gettempdir(),
                           "buddy_resume_test.blend")
bpy.ops.wm.save_as_mainfile(filepath=resume_path)
bpy.ops.wm.open_mainfile(filepath=resume_path)
ctx = bpy.context
assert ctx.scene.buddy_tour_started is True
checks, current = bb.tour_state(ctx)
assert checks[:2] == [True, True] and current == 2, checks
key, _spec = bb._conduct_spec(ctx)
assert key == ("donut", 2), key
print("TOUR_PASS interrupt and resume: steps 1-2 still ticked "
      "after a fresh reload, the card resumes at step 3")

bb.unregister()
print("ALL TOUR TESTS PASSED")
