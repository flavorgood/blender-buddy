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
# The names HE assigns, arriving when he assigns them: Donut,
# Icing and Mug renamed in Part 3, Foam in Part 6, Table and
# Plate only in Part 8's housekeeping, and the finale's lights
# - Sun, Sky, Indoor Bounce - with the two window blockers.
assert {"Donut", "Icing", "Mug", "Foam", "Plate", "Table",
        "Sun", "Sky", "Indoor Bounce", "Blocker",
        "Blocker.001"} <= names, names
assert "Cube" not in names, "the starter cube should be gone"
assert "Cup" not in names, "the cup was renamed Mug in Part 3"
print("TOUR_PASS starter cube cleared; his names in place")

lighting = bpy.data.collections.get("Lighting")
assert lighting is not None
assert {"Sun", "Sky", "Indoor Bounce", "Blocker",
        "Blocker.001"} <= {o.name for o in lighting.objects}
print("TOUR_PASS lights and blockers filed in Lighting")

icing = scene.objects["Icing"]
dough = scene.objects["Donut"]
# Part 3's finish is APPLIED, in his order: no live
# Shrinkwrap or Solidify may remain on the icing. (The old
# build left them live - and the old test asserted exactly
# that wrong state.)
assert not any(m.type in ("SHRINKWRAP", "SOLIDIFY")
               for m in icing.modifiers), \
    [m.type for m in icing.modifiers]
print("TOUR_PASS icing finished the Part 3 way: applied")

# His subsurface recipe, read back off the food: Weight 1,
# Radius (1, 1, 1) on both, the icing's Scale retuned to the
# stated 0.03 in Part 8.
for obj, want_scale in ((icing, 0.03), (dough, None)):
    recipe = bb._sss_recipe(obj)
    assert recipe is not None and recipe[0] > 0.99, \
        (obj.name, recipe)
    assert all(abs(c - 1.0) < 0.01 for c in recipe[1]), \
        (obj.name, recipe)
    if want_scale is not None:
        assert abs(recipe[2] - want_scale) < 0.005, \
            (obj.name, recipe)
print("TOUR_PASS subsurface reads his recipe: weight 1, "
      "radius 1 1 1, icing scale 0.03")

mug = scene.objects["Mug"]
assert sum(1 for e in mug.data.edges if e.use_seam) >= 10, \
    "the mug needs his seam layout, not a stray edge"
foam = scene.objects["Foam"]
assert foam.data.materials and foam.data.materials[0] is not None
_fzs = [v.co.z for v in foam.data.vertices]
assert max(_fzs) - min(_fzs) > 0.002, \
    "the foam is inset with a dipped middle, never a flat disc"
plate = scene.objects["Plate"]
table = scene.objects["Table"]
assert icing.parent is dough and dough.parent is plate
assert foam.parent is mug
assert plate.parent is table and mug.parent is table
print("TOUR_PASS mug seamed, foam built and dipped, "
      "the set parented his way")

if HAS_SCATTER:
    assert any(m.type == "NODES" and m.node_group is not None
               and "Scatter on Surface" in m.node_group.name
               for m in icing.modifiers)
    _mod = next(m for m in icing.modifiers if m.type == "NODES")
    _inputs = bb._mod_inputs(_mod)

    def _ival(name):
        prop = _inputs.get(name)
        return getattr(prop, "value", None) if prop else None

    assert _ival("Instance Type") == "Collection"
    _coll = _ival("Collection")
    assert _coll is not None and _coll.name == "Sprinkles"
    assert len(_coll.objects) >= 2
    assert _ival("Pick Instance") is True
    assert _ival("Density Method") == "Density"
    assert abs(float(_ival("Density")) - 900.0) < 1.0
    assert _ival("Distribution Method") == "Poisson Disk"
    _mask = _inputs.get("Distribution Mask")
    assert getattr(_mask, "type", None) == "ATTRIBUTE"
    assert _mask.attribute_name == "Group"
    assert icing.vertex_groups.get("Group") is not None
    print("TOUR_PASS scatter modifier reads his settings "
          "back by name: collection, 900, Poisson Disk, "
          "painted Group as the mask attribute")

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

# --- the visual gate -------------------------------------------
# A render that EXISTS is not a render that WORKED. v3.2.0
# shipped a step-8 frame that measured mean luminance 0.053
# with 65% of its pixels near-black - a black donut silhouette
# with glowing sprinkles - and every test passed, because the
# only assertion was that a file existed. Never again: the
# keepsake render must also be a LIT picture. Thresholds sit
# far from both sides of the evidence: the black frame (0.053
# mean, 0.655 near-black) fails both by multiples; the lit
# reference renders measure 0.24-0.51 mean with ~0.00
# near-black.
_gate = bpy.data.images.load(out)
_px = list(_gate.pixels)
_n = len(_px) // 4
_lums = [0.2126 * _px[4 * i] + 0.7152 * _px[4 * i + 1]
         + 0.0722 * _px[4 * i + 2] for i in range(_n)]
_mean = sum(_lums) / _n
_black = sum(1 for lum in _lums if lum < 0.02) / _n
assert _mean > 0.15, \
    f"the final render is too dark: mean luminance {_mean:.3f}"
assert _black < 0.25, \
    f"the final render is mostly black: {_black:.3f} near-black"
print(f"TOUR_PASS visual gate: the final render is a lit "
      f"picture (mean luminance {_mean:.3f}, "
      f"near-black {_black:.3f})")

blend_out = os.path.join(ROOT, "demo", "buddy_donut.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"TOUR_PASS donut scene saved: {blend_out}")

# The wired maps must hold real pixels, not black - wiring
# alone once passed while every texture was empty (a
# colours-space change after the pixel write silently reset
# the buffers on both Blender versions). The icing's own
# colour picture is DISCONNECTED by his Part 5 repair, so the
# pixel proof reads the maps his wiring keeps: the table's
# colour map and the icing's roughness map.
def _map_mean(obj_name, socket):
    obj = bpy.data.objects[obj_name]
    for mat in obj.data.materials:
        if mat is None or not mat.use_nodes:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        # Follow the chain back from the socket - Part 6's
        # colour surgery puts curve/HSV nodes between the
        # table's colour picture and the Principled.
        stack = [link.from_node
                 for link in bsdf.inputs[socket].links]
        seen = set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node.type == "TEX_IMAGE" and node.image is not None:
                px = list(node.image.pixels)
                reds = px[0::4]
                return sum(reds) / max(1, len(reds))
            for sock in node.inputs:
                stack.extend(link.from_node
                             for link in sock.links)
    return 0.0


assert _map_mean("Table", "Base Color") > 0.05, \
    "the table colour map is empty"
assert _map_mean("Icing", "Roughness") > 0.05, \
    "the icing roughness map is empty"
print("TOUR_PASS texture pixels: wired maps hold real data")

# --- names are not the proof --------------------------------
# Every check finds its objects by role, shape, material and
# structure - so renaming EVERY object to junk must leave
# the ticks standing. (His Part 8 names are taught in the
# lessons, never gated on.)
_saved_names = {}
for _i, _obj in enumerate(scene.objects):
    _saved_names[_obj] = _obj.name
    _obj.name = f"Junk{_i}"
checks, current = bb.tour_state(ctx)
if HAS_SCATTER:
    assert all(checks) and current == 8, checks
else:
    assert checks[:6] == [True] * 6 and checks[7] is True, checks
for _obj, _name in _saved_names.items():
    _obj.name = _name
print("TOUR_PASS renamed to junk, the ticks stand: "
      "role-based checks")

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

# --- negative proofs -----------------------------------------
# The fidelity audit's five-first fixes, proven from the other
# side: a scene that did NOT follow his procedure must not
# tick. Each negative runs in its own fresh scene.
def _fresh_tour():
    bpy.ops.wm.read_factory_settings(use_empty=False)
    c = bpy.context
    bpy.ops.buddy.tour_start(package="donut")
    c.scene.render.engine = "CYCLES"
    c.scene.cycles.samples = 16
    c.scene.render.resolution_x = 320
    c.scene.render.resolution_y = 240
    return c


# (1) Step 1's old false pass: open Blender, touch nothing,
# Ctrl+S. The save alone must not tick - his ring and cup
# are the proof.
c = _fresh_tour()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(
    tempfile.gettempdir(), "buddy_neg_empty.blend"))
assert bb._check_first_cup(c) is False
print("TOUR_NEGATIVE save alone does not tick step 1")

# (2) Step 2: the cup alone is not a mug. And once the mug
# exists, a second PLAIN cup standing beside it kills the
# tick - a separate second mesh is not his procedure; the
# cup ITSELF becomes the mug.
c = _fresh_tour()
bpy.ops.buddy.tour_do(step=0)
assert bb._check_mug_reference(c) is False
bpy.ops.buddy.tour_do(step=1)
assert bb._check_mug_reference(c) is True
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.13, depth=0.24, vertices=14,
    location=(0.45, 0.0, 0.0))
_extra = c.object
import bmesh as _bm
_b = _bm.new()
_b.from_mesh(_extra.data)
_b.faces.ensure_lookup_table()
_top = max(_b.faces, key=lambda f: f.calc_center_median().z)
_bm.ops.delete(_b, geom=[_top], context="FACES")
_b.to_mesh(_extra.data)
_b.free()
assert bb._check_mug_reference(c) is False
print("TOUR_NEGATIVE a plain second cup beside the mug "
      "does not tick step 2")

# (3) Step 3's half-done state: put a live modifier back on
# the finished icing and the tick dies - his finish is the
# APPLIED state, exactly where the old check stopped.
c = _fresh_tour()
for _s in range(3):
    bpy.ops.buddy.tour_do(step=_s)
assert bb._check_icing_hug(c) is True
_icing = bb._find_icing(c, bb._find_dough(c))
_icing.modifiers.new("Shrinkwrap", "SHRINKWRAP")
assert bb._check_icing_hug(c) is False
print("TOUR_NEGATIVE live modifiers on the icing "
      "do not tick step 3")

# (4) The subsurface recipe: his is Weight 1, Radius
# (1, 1, 1). The old epsilon check passed on anything above
# zero - a weight of 0.25 must not tick step 4.
c = _fresh_tour()
for _s in range(4):
    bpy.ops.buddy.tour_do(step=_s)
assert bb._check_first_picture(c) is True
_icing = bb._find_icing(c, bb._find_dough(c))
_bsdf = _icing.data.materials[0].node_tree.nodes["Principled BSDF"]
_bsdf.inputs["Subsurface Weight"].default_value = 0.25
assert bb._check_first_picture(c) is False
print("TOUR_NEGATIVE subsurface weight 0.25 "
      "does not tick step 4")

# (5) Step 5 is per-surface: wiring ONLY the table, fully,
# must not carry the still-bare plate, dough and icing -
# the old check pooled its clauses across objects.
_bsdf.inputs["Subsurface Weight"].default_value = 1.0
_table = bb._find_table(c, bb._find_dough(c))
bb._apply_pbr(_table, bb._make_texture_set(
    "Negative Table", (0.3, 0.3, 0.3), 41, 0.5))
assert bb._check_real_surfaces(c) is False
print("TOUR_NEGATIVE one wired surface does not tick step 5")

# (6) Step 7 (Blender 5 only): a Scatter on Surface modifier
# at its DEFAULTS, plus an unpainted group that happens to
# carry his group's name, must not tick - the wiring and
# the paint are the proof.
if HAS_SCATTER:
    c = _fresh_tour()
    for _s in range(3):
        bpy.ops.buddy.tour_do(step=_s)
    _icing = bb._find_icing(c, bb._find_dough(c))
    _mod = _icing.modifiers.new("Scatter on Surface", "NODES")
    _mod.node_group = bb._scatter_group()
    _icing.vertex_groups.new(name="Group")
    assert bb._check_scatter(c) is False
    print("TOUR_NEGATIVE a default scatter modifier "
          "does not tick step 7")

# (7) Step 8's rig is specific: the factory lamp plus one
# more default light is not it.
c = _fresh_tour()
bpy.ops.object.light_add(type="POINT", location=(1, 1, 1))
assert bb._check_final_picture(c) is False
print("TOUR_NEGATIVE two default lights do not tick step 8")

bb.unregister()
print("ALL TOUR TESTS PASSED")
