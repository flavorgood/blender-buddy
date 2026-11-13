"""Blender Buddy guided-project proof (the Donut package).

Run with:
  blender -b --factory-startup --python tests/test_tour.py

The projects TEACH: every step carries plain-words instructions
for doing it by hand in real Blender, names the skill it teaches,
and says what the scene is still missing. There is no "do this
step" button in the panel - the learner does the work. This suite
proves the other half: that each step's scene check (the same
checks the panel ticks from) is satisfied by the step's reference
build, that the checks also accept the taught by-hand routes
(particle sprinkles), and that every step actually carries its
teaching content. Finishes by rendering the donut as the demo
picture.
"""
import math
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

# The taught sprinkles route counts: a particle system on the icing.
bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=12)
probe = ctx.object
probe.name = "Icing"
probe.modifiers.new("Scatter", "PARTICLE_SYSTEM")
assert bb._check_sprinkles(ctx), "particle sprinkles must tick the step"
print("TOUR_PASS sprinkles by particles (the taught way) prove the step")
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
# EEVEE engine at all (it aborts), so the tour's picture step renders
# with Cycles here. On a real computer the default engine just works.
ctx.scene.render.engine = "CYCLES"
ctx.scene.cycles.samples = 16
ctx.scene.render.resolution_x = 320
ctx.scene.render.resolution_y = 240

for i in range(8):
    checks, current = bb.tour_state(ctx)
    assert current == i, f"before step {i}: state {checks}, current {current}"
    bpy.ops.buddy.tour_do(step=i)
    checks, current = bb.tour_state(ctx)
    assert checks[i], f"step {i} ({bb.TOUR_STEPS[i]['title']}) not proven: {checks}"
    print(f"TOUR_PASS step {i + 1}: {bb.TOUR_STEPS[i]['title']}")

checks, current = bb.tour_state(ctx)
assert current == 8 and all(checks), checks
print("TOUR_PASS all 8 steps proven by the scene")

scene = ctx.scene
names = {o.name for o in scene.objects}
assert {"Dough", "Icing", "Sprinkles", "Plate", "Table", "Mug"} <= names, names
assert "Cube" not in names, "the starter cube should be gone - the donut is the scene"
print("TOUR_PASS starter cube cleared, like the tutorial does")
sprinkles = scene.objects["Sprinkles"]
assert len(sprinkles.data.vertices) > 4000, len(sprinkles.data.vertices)
icing = scene.objects["Icing"]
assert any(m.type == "SOLIDIFY" for m in icing.modifiers), \
    "icing must be the tutorial's method: top of the dough, thickened"
drip = min(v.co.z for v in icing.data.vertices)
assert -0.30 < drip < -0.03, f"icing rim must drip down the side, min z {drip}"
dough = scene.objects["Dough"]
assert len(dough.data.materials) == 2, "dough needs its pale fry line"
assert any(p.material_index == 1 for p in dough.data.polygons)
print("TOUR_PASS solidify icing with drips, fry-line dough, scene set")

# Render the keepsake picture through the TOUR's own camera and
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

bb.unregister()
print("ALL TOUR TESTS PASSED")
