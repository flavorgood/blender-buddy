"""Blender Buddy card-walk regression.

Run with:
  blender -b --factory-startup --python tests/test_card_walk.py

WHY THIS SUITE EXISTS: the cold card-only walkthrough of the
donut package (redesign/TEACH_WALKTHROUGH_GAPS.md) found that
a learner following the step cards exactly was stranded in
Part 2 - the step checks had been calibrated on the reference
build's dense mesh, and on the learner's own low-vertex cage
the handle's vertices poisoned the container test, un-ticking
steps 1 AND 2 at once. The reference builds in test_tour.py
can never catch that class of failure: they prove the checks
accept the BUILDER's scene, not the scene the CARD produces.

So this suite builds the scene the card's own procedure
produces - the 14-vertex cup, the rings placed one at a time,
the handle extruded out of the cup's wall and sewn back by
hand - with plain bmesh, step by step, and proves:

  * step 1 ticks only when the whole Part 1 procedure is in
    the mesh (open top, Solidify, Subsurf, inset, two loop
    cuts - each omission fails it, the closed cap included);
  * steps 1, 2 and 3 tick IN ORDER on the cumulative scene,
    and step 1 STAYS ticked after the handle is grown and
    joined (the stranding regression);
  * the mid-states fail the right step only: handle grown but
    Solidify not yet applied (step 2 waits, step 1 holds);
    handle grown but the join left open (step 2 waits);
    a plain second cup beside the finished mug (step 2
    refuses - the mug is the cup, not its neighbour);
  * step 3 ticks on the finished icing and un-ticks the
    moment a live Shrinkwrap returns (the half-done state);
  * the panel's word wrap never loses a word of the teach
    text at any real sidebar width (gap class X1): every
    line the wrap produces, joined back up, is the original
    text word for word, and every line measures inside the
    panel space the deepest card actually gets.

The negatives for steps 4, 5, 7 and 8 (wrong subsurface
recipe, one wired surface, default scatter, two-lights rig)
live in test_tour.py and are re-proven there on the same
bytes; this suite covers the walked steps, 1-3.

Round 2 (the cold re-walk of v3.2.1, walk101): the three
check-integrity majors are rebuilt by construction below -
a zero-thickness inset and a stale save must not tick
step 1; the Solidify Apply moment, plain and on a messy
cage, must not tick step 2; and the join ladder (touching
waits, the 4-corner sew ticks, deleting the inside faces
keeps the tick, the bridge path ticks throughout, a capped
handle hanging in mid-air does not) - plus the preserved
walked scene itself, which must read exactly as it stands:
step 1 ticked, standing at step 2.
"""
import math
import os
import sys

import bmesh
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context


# --- scene plumbing ------------------------------------------------

def wipe():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for coll in (bpy.data.meshes, bpy.data.curves,
                 bpy.data.cameras, bpy.data.lights):
        pass  # orphan datablocks do not affect the checks


def _bm(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def _push(obj, bm):
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def _save(path):
    bpy.ops.wm.save_as_mainfile(filepath=path)


def _current():
    """The tour's standing, computed the way tour_state does
    it - the first step whose check fails - directly from the
    donut package's checks (no tour needs to be running for
    the scene to be graded)."""
    pkg = bb.PACKAGES_BY_ID["donut"]
    for i, step in enumerate(pkg["steps"]):
        try:
            if not step["check"](ctx):
                return i
        except Exception:
            return i
    return len(pkg["steps"])


# --- the card's procedure, step by step ----------------------------

def make_dough():
    bpy.ops.mesh.primitive_torus_add(
        major_segments=48, minor_segments=18,
        major_radius=0.1, minor_radius=0.057)
    dough = ctx.object
    dough.name = "Torus"
    for poly in dough.data.polygons:
        poly.use_smooth = True
    return dough


def make_cup_raw():
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=14, radius=0.13, depth=0.24,
        location=(0.23, 0.19, 0.0))
    cup = ctx.object
    cup.name = "Cylinder"
    return cup


def open_top(cup):
    bm = _bm(cup)
    top = [f for f in bm.faces if f.normal.z > 0.9]
    assert len(top) == 1
    bmesh.ops.delete(bm, geom=top, context="FACES")
    _push(cup, bm)


def _wall_edge(e):
    """A wall edge running up the cup: its endpoints share an
    angle around the axis (ring scales slant the wall, so
    'vertical' means same-angle, not same x/y) and differ in
    height."""
    a, b = e.verts[0].co, e.verts[1].co
    if abs(a.z - b.z) < 1e-6:
        return False
    cross = a.x * b.y - a.y * b.x
    dot = a.x * b.x + a.y * b.y
    return abs(cross) < 1e-7 and dot > 0


def add_ring(cup, z_target, band):
    """One loop cut the card's way: subdivide the wall's
    vertical edges inside `band` (a predicate on the edge's
    endpoint heights) and slide the new ring to z_target."""
    bm = _bm(cup)
    edges = [e for e in bm.edges
             if _wall_edge(e)
             and band(e.verts[0].co.z, e.verts[1].co.z)]
    assert edges, "no vertical wall edges in the band"
    out = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1)
    for g in out["geom_inner"]:
        if isinstance(g, bmesh.types.BMVert):
            g.co.z = z_target
    _push(cup, bm)


def inset_bottom(cup, thickness=0.02):
    bm = _bm(cup)
    bottom = [min(bm.faces,
                  key=lambda f: f.calc_center_median().z)]
    bmesh.ops.inset_region(bm, faces=bottom, thickness=thickness,
                           depth=0.0, use_even_offset=True)
    _push(cup, bm)


def ring_scale(cup, z, factor, tol=0.004):
    bm = _bm(cup)
    hit = 0
    for v in bm.verts:
        if abs(v.co.z - z) < tol:
            v.co.x *= factor
            v.co.y *= factor
            hit += 1
    assert hit >= 10, (z, hit)
    _push(cup, bm)


def ring_slide(cup, z_from, z_to, tol=0.004):
    bm = _bm(cup)
    hit = 0
    for v in bm.verts:
        if abs(v.co.z - z_from) < tol:
            v.co.z = z_to
            hit += 1
    assert hit >= 10, (z_from, hit)
    _push(cup, bm)


def finish_part1(cup, cuts=True, inset=True):
    """The card's Part 1, in the card's order: open the top,
    Solidify, Subsurf, the two loop cuts one at a time, the
    inset. `cuts`/`inset` exist so the omissions can be
    proven to fail the tick."""
    open_top(cup)
    solid = cup.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.006
    sub = cup.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 2
    if cuts:
        add_ring(cup, 0.10, lambda z0, z1: True)
        add_ring(cup, -0.10, lambda z0, z1: (z0 + z1) / 2 < 0.0)
    if inset:
        inset_bottom(cup)


def reshape_cup(cup):
    """The card's Part 2 profile work: Alt+click rings, S to
    size them, GG to slide the belly ring, the foot."""
    ring_scale(cup, 0.12, 0.94)          # top ring in a touch
    ring_scale(cup, 0.10, 0.97)          # the ring below, halfway
    ring_slide(cup, -0.10, -0.072)       # belly ring to ~20% height
    ring_scale(cup, -0.072, 1.06)        # ...and out to the curve
    ring_scale(cup, -0.12, 0.93)         # bottom face in a little
    # The foot: extrude the whole underside down a touch.
    bm = _bm(cup)
    under = [f for f in bm.faces
             if f.calc_center_median().z < -0.119]
    assert under
    out = bmesh.ops.extrude_face_region(bm, geom=under)
    verts = {v for g in out["geom"]
             if isinstance(g, bmesh.types.BMFace)
             for v in g.verts}
    bmesh.ops.translate(bm, verts=list(verts),
                        vec=(0.0, 0.0, -0.010))
    _push(cup, bm)
    # Two guard rings at the very bottom.
    add_ring(cup, -0.125, lambda z0, z1: max(z0, z1) < -0.115)
    add_ring(cup, -0.115,
             lambda z0, z1: -0.121 < min(z0, z1)
             and max(z0, z1) < -0.05)


def apply_solidify(cup):
    bb._set_active(ctx, cup)
    if bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bb._apply_modifier(ctx, cup, "Solidify")


def _extrude_step(bm, face, delta):
    from mathutils import Vector
    out = bmesh.ops.extrude_face_region(bm, geom=[face])
    faces = [g for g in out["geom"]
             if isinstance(g, bmesh.types.BMFace)]
    verts = {v for f in faces for v in f.verts}
    bmesh.ops.translate(bm, verts=list(verts), vec=Vector(delta))
    d = Vector(delta).normalized()
    end = max(faces,
              key=lambda f: f.calc_center_median().dot(d))
    return end, faces


def _sew(bm, verts_a, verts_b):
    """The card's hand-built join, literally: four new faces,
    one per side, each spanning a rim edge of the handle's
    end and the matching rim edge of the body's opening
    (select two points, press F - four times around)."""
    va = list(verts_a)
    vb = list(verts_b)
    k = min(range(len(vb)),
            key=lambda i: (vb[i].co - va[0].co).length)
    vb = vb[k:] + vb[:k]
    if (va[1].co - vb[-1].co).length \
            < (va[1].co - vb[1].co).length:
        vb = [vb[0]] + vb[1:][::-1]
    n = len(va)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((va[i], va[j], vb[j], vb[i]))


def grow_handle(cup, join=True):
    """The card's handle: one dead-centre side face extruded
    out of the wall, walked over and down with E/G/R steps,
    then - the card's main join - the two internal faces
    deleted and the joint built by hand with four F faces.
    The Ctrl+R ring near the handle's base is the card's own
    thinning move, done first here so the start face is
    handle-sized."""
    add_ring(cup, 0.03,
             lambda z0, z1: -0.073 < min(z0, z1)
             and max(z0, z1) < 0.101)
    bm = _bm(cup)
    bm.faces.ensure_lookup_table()
    wall = [f for f in bm.faces
            if f.normal.x > 0.5
            and abs(f.calc_center_median().y) < 0.05]
    assert wall, "no outer side face to grow from"
    start = max((f for f in wall
                 if f.calc_center_median().z < 0.10),
                key=lambda f: f.calc_center_median().z)
    grown = []
    end, faces = _extrude_step(bm, start, (0.055, 0.0, 0.010))
    grown += faces
    end, faces = _extrude_step(bm, end, (0.010, 0.0, 0.055))
    grown += faces
    end, faces = _extrude_step(bm, end, (-0.010, 0.0, -0.050))
    grown += faces
    end, faces = _extrude_step(bm, end, (-0.020, 0.0, -0.075))
    grown += faces
    bm.faces.ensure_lookup_table()
    centre = end.calc_center_median()
    landing = min(
        (f for f in bm.faces
         if f.normal.x > 0.5 and f not in grown
         and f.calc_center_median().x < 0.145),
        key=lambda f: (f.calc_center_median() - centre).length)
    end_verts = list(end.verts)
    land_verts = list(landing.verts)
    bmesh.ops.delete(bm, geom=[end, landing], context="FACES")
    if join:
        _sew(bm, end_verts, land_verts)
    _push(cup, bm)
    if join:
        assert bb._join_closed(cup), "the sewn joint must close"


def build_icing(dough):
    """The card's Part 3 up to the finished state: copy the
    dough, delete the bottom half's faces, Solidify (Offset
    1) -> Subsurf -> Shrinkwrap, stack reordered his way,
    drips pulled, then all three applied top to bottom."""
    bb._set_active(ctx, dough)
    bpy.ops.object.duplicate()
    icing = ctx.object
    icing.name = "Icing"
    bm = _bm(icing)
    under = [f for f in bm.faces
             if f.calc_center_median().z < -0.001]
    bmesh.ops.delete(bm, geom=under, context="FACES")
    # Drips: pull two boundary-edge runs down before the
    # stack goes on (his order varies; the graded shape is
    # a rim with real z-spread and low points).
    bm.edges.ensure_lookup_table()
    rim = [v for e in bm.edges if len(e.link_faces) == 1
           for v in e.verts]
    low = sorted({id(v): v for v in rim}.values(),
                 key=lambda v: math.atan2(v.co.y, v.co.x))
    for i, v in enumerate(low):
        if i % 6 == 0:
            v.co.z -= 0.018
        elif i % 6 == 3:
            v.co.z -= 0.010
    _push(icing, bm)
    thick = icing.modifiers.new("Solidify", "SOLIDIFY")
    thick.offset = 1.0
    thick.thickness = 0.003
    sub = icing.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 2
    wrap = icing.modifiers.new("Shrinkwrap", "SHRINKWRAP")
    wrap.target = dough
    bb._ensure_mod_order(
        ctx, icing, ["Shrinkwrap", "Solidify", "Subdivision"])
    for name in ("Shrinkwrap", "Solidify", "Subdivision"):
        mod = next((m for m in icing.modifiers if name in m.name),
                   None)
        assert mod is not None, name
        bb._apply_modifier(ctx, icing, mod.name)
    return icing


# --- Part 1: the tick is the whole procedure ------------------------

TMP = os.path.join(ROOT, "tests", "_card_walk_tmp.blend")

wipe()
dough = make_dough()
cup = make_cup_raw()
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS raw shapes do not tick step 1")

# The closed cap must be caught: everything done, top never
# opened - no tick. (The old probe's blind spot: a cap's
# verts all sit on the rim, so it read as open.)
wipe()
dough = make_dough()
cup = make_cup_raw()
solid = cup.modifiers.new("Solidify", "SOLIDIFY")
solid.thickness = 0.006
sub = cup.modifiers.new("Subdivision", "SUBSURF")
sub.levels = 2
add_ring(cup, 0.10, lambda z0, z1: True)
add_ring(cup, -0.10, lambda z0, z1: (z0 + z1) / 2 < 0.0)
inset_bottom(cup)
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS a closed cap does not tick step 1")

# No Solidify, no Subsurf - no tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
open_top(cup)
add_ring(cup, 0.10, lambda z0, z1: True)
add_ring(cup, -0.10, lambda z0, z1: (z0 + z1) / 2 < 0.0)
inset_bottom(cup)
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS no walls and no smoother: no step 1 tick")

# One loop cut only - no tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
open_top(cup)
solid = cup.modifiers.new("Solidify", "SOLIDIFY")
solid.thickness = 0.006
sub = cup.modifiers.new("Subdivision", "SUBSURF")
sub.levels = 2
add_ring(cup, 0.10, lambda z0, z1: True)
inset_bottom(cup)
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS one loop cut is not the cup he leaves")

# No inset - no tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup, inset=False)
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS no inset: no step 1 tick")

# The full card procedure - ticks.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
_save(TMP)
assert bb._check_first_cup(ctx)
assert _current() == 1
print("CARDWALK_PASS step 1 ticks on the card's own cup, "
      "and the tour stands at step 2")

# --- Part 2: the stranding regression -------------------------------

reshape_cup(cup)
_save(TMP)
assert bb._check_first_cup(ctx), "reshape must keep step 1"
apply_solidify(cup)
grow_handle(cup, join=True)
_save(TMP)
assert bb._check_first_cup(ctx), \
    "step 1 un-ticked after the handle - THE STRANDING"
assert bb._check_mug_reference(ctx)
assert _current() == 2
print("CARDWALK_PASS steps 1 and 2 tick in order on the "
      "learner's cage, and step 1 survives the handle")

# Mid-state: handle grown and joined, Solidify never applied
# - step 2 waits, step 1 holds.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
grow_handle(cup, join=True)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx)
print("CARDWALK_PASS un-applied Solidify: step 2 waits, "
      "step 1 holds")

# The join left open - step 2 waits.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
grow_handle(cup, join=False)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx)
print("CARDWALK_PASS an unjoined handle does not tick step 2")

# A plain second cup beside the finished mug - step 2 refuses.
bpy.ops.mesh.primitive_cylinder_add(
    vertices=14, radius=0.13, depth=0.24, location=(0.5, 0, 0))
plain = ctx.object
bm = _bm(plain)
top = [f for f in bm.faces if f.normal.z > 0.9]
bmesh.ops.delete(bm, geom=top, context="FACES")
_push(plain, bm)
assert not bb._check_mug_reference(ctx)
print("CARDWALK_PASS a plain neighbour cup un-ticks step 2")

# --- Part 3: finished ticks, half-done does not ---------------------

wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
grow_handle(cup, join=True)
icing = build_icing(dough)
_save(TMP)
assert bb._check_icing_hug(ctx)
assert _current() == 3
print("CARDWALK_PASS steps 1, 2, 3 tick in order on the "
      "card-built scene")

wrap = icing.modifiers.new("Shrinkwrap", "SHRINKWRAP")
wrap.target = dough
assert not bb._check_icing_hug(ctx)
print("CARDWALK_PASS a live Shrinkwrap un-ticks step 3 "
      "(the half-done state)")

# --- Round 2: the re-walk's three majors, by construction ------------
# The cold re-walk of v3.2.1 failed acceptance on check
# integrity: step 1 ticked at the bare I keystroke with a
# stale save on disk, step 2 ticked at the Solidify Apply
# with no handle at all, and step 2 un-ticked when the
# card's own bridge move deleted the two joint faces. Each
# state is rebuilt here so it can never pass silently again.


def grow_capped(cup):
    """grow_handle's path with both cap faces kept - the
    handle's end still closed, the body's landing face
    still in place: the state the card's join starts from.
    Returns the two faces' centres for re-location."""
    add_ring(cup, 0.03,
             lambda z0, z1: -0.073 < min(z0, z1)
             and max(z0, z1) < 0.101)
    bm = _bm(cup)
    bm.faces.ensure_lookup_table()
    wall = [f for f in bm.faces
            if f.normal.x > 0.5
            and abs(f.calc_center_median().y) < 0.05]
    start = max((f for f in wall
                 if f.calc_center_median().z < 0.10),
                key=lambda f: f.calc_center_median().z)
    grown = []
    end, faces = _extrude_step(bm, start, (0.055, 0.0, 0.010))
    grown += faces
    end, faces = _extrude_step(bm, end, (0.010, 0.0, 0.055))
    grown += faces
    end, faces = _extrude_step(bm, end, (-0.010, 0.0, -0.050))
    grown += faces
    end, faces = _extrude_step(bm, end, (-0.020, 0.0, -0.075))
    grown += faces
    bm.faces.ensure_lookup_table()
    centre = end.calc_center_median()
    landing = min(
        (f for f in bm.faces
         if f.normal.x > 0.5 and f not in grown
         and f.calc_center_median().x < 0.145),
        key=lambda f: (f.calc_center_median() - centre).length)
    out = (end.calc_center_median().copy(),
           landing.calc_center_median().copy())
    _push(cup, bm)
    return out


def _face_at(bm, centre):
    bm.faces.ensure_lookup_table()
    return min(bm.faces,
               key=lambda f: (f.calc_center_median()
                              - centre).length)


def grow_touching(cup):
    """The walked fixture's shape, by construction
    (re-walk #2, gap #3): the handle grown in the card's
    E/G/R rhythm - six segments, each TILTED about the
    end face's centre as it is placed, the way a hand
    arcs the ear over - so the descent hugs the wall and
    the tube's wall-side verts chain back to the root
    along the surface; then the end face pulled to the
    body until it rests on the wall face it covers. Cap
    ON, wall face present, NO join faces: the handle
    touches the body and shares no topology with it.
    Returns the end face's and the landing face's vert
    index sets in the pushed mesh."""
    from mathutils import Matrix
    add_ring(cup, 0.03,
             lambda z0, z1: -0.073 < min(z0, z1)
             and max(z0, z1) < 0.101)
    bm = _bm(cup)
    bm.faces.ensure_lookup_table()
    wall = [f for f in bm.faces
            if f.normal.x > 0.5
            and abs(f.calc_center_median().y) < 0.05]
    start = max((f for f in wall
                 if f.calc_center_median().z < 0.10),
                key=lambda f: f.calc_center_median().z)
    grown = []
    end = start
    steps = [((0.018, 0.0, 0.008), -15.0),
             ((0.014, 0.0, -0.006), -15.0),
             ((0.006, 0.0, -0.022), -15.0),
             ((0.006, 0.0, -0.030), -15.0),
             ((0.006, 0.0, -0.024), 15.0),
             ((-0.030, 0.0, -0.002), 45.0)]
    for delta, tilt in steps:
        end, faces = _extrude_step(bm, end, delta)
        grown += faces
        centre = end.calc_center_median()
        m = (Matrix.Translation(centre)
             @ Matrix.Rotation(math.radians(tilt), 4, "Y")
             @ Matrix.Translation(-centre))
        for v in end.verts:
            v.co = m @ v.co
    bm.faces.ensure_lookup_table()
    centre = end.calc_center_median()
    landing = min(
        (f for f in bm.faces
         if f.normal.x > 0.5 and f not in grown
         and f.calc_center_median().x < 0.145),
        key=lambda f: (f.calc_center_median() - centre).length)
    target = (landing.calc_center_median()
              + landing.normal * 0.004)
    delta = target - end.calc_center_median()
    bmesh.ops.translate(bm, verts=list(end.verts), vec=delta)
    end_verts = {v.index for v in end.verts}
    land_verts = {v.index for v in landing.verts}
    _push(cup, bm)
    return end_verts, land_verts


def grow_hugging_joined(cup):
    """grow_touching's growth - the same six tilted
    E/G/R steps, so the descent hugs the wall and its
    wall-side faces lie inside the line - carried
    through the card's own ending: the end pulled to
    the body, the two inside faces deleted, the joint
    sewn by hand, rim to rim. The pairing round 3
    never built: its suite paired the hugging descent
    only with an UNJOINED end (where the expected
    verdict is False) and a joined end only with a
    descent arcing away from the wall, so the veto's
    misfire - a mid-descent tube face mistaken for the
    end cap - produced the expected answer for the
    wrong reason in the one and was never triggered
    in the other. On the walked mug (walk105) the
    same misfire refused a finished bridge; this
    construction is that geometry with the card's
    hand sew, and it must TICK.

    One geometry choice mirrors W1's walked scene, not
    grow_touching's shortcut: grow_touching lands the
    end on the wall face directly below the root face
    - the two share a ring of verts. W1's walked
    handle landed clear of its root, so here the end
    is pulled to the nearest wall face that shares NO
    vert with the root face. The sharing shape is NOT
    a case the card's arc never produces - fix round
    4's first writing called it one, and W2 refuted
    that: the card's own procedure produces it (grow
    pick = the tall-band face; the handle lands on
    the belly band directly below its root, so the
    patch's top pair IS the root face's bottom pair).
    (Measured in fix round 4: with root and landing
    sharing verts, the shared verts are spanning-face
    targets at both ends at once and - while they sat
    inside the tube's measured set - the tube graph's
    diameter collapsed onto mid-descent verts, and
    the end ring was never an end of the tube at all.
    Fix round 5 excludes the anchored verts from the
    measured set, which repairs the class; W2's
    walked mug is locked with the walk107 checkpoints
    below.)"""
    from mathutils import Matrix
    add_ring(cup, 0.03,
             lambda z0, z1: -0.073 < min(z0, z1)
             and max(z0, z1) < 0.101)
    bm = _bm(cup)
    bm.faces.ensure_lookup_table()
    wall = [f for f in bm.faces
            if f.normal.x > 0.5
            and abs(f.calc_center_median().y) < 0.05]
    start = max((f for f in wall
                 if f.calc_center_median().z < 0.10),
                key=lambda f: f.calc_center_median().z)
    start_vs = {v.index for v in start.verts}
    grown = []
    end = start
    steps = [((0.018, 0.0, 0.008), -15.0),
             ((0.014, 0.0, -0.006), -15.0),
             ((0.006, 0.0, -0.022), -15.0),
             ((0.006, 0.0, -0.030), -15.0),
             ((0.006, 0.0, -0.024), 15.0),
             ((-0.030, 0.0, -0.002), 45.0)]
    for delta, tilt in steps:
        end, faces = _extrude_step(bm, end, delta)
        grown += faces
        centre = end.calc_center_median()
        m = (Matrix.Translation(centre)
             @ Matrix.Rotation(math.radians(tilt), 4, "Y")
             @ Matrix.Translation(-centre))
        for v in end.verts:
            v.co = m @ v.co
    bm.faces.ensure_lookup_table()
    centre = end.calc_center_median()
    # Wall faces only: a face is the cup's wall when it
    # shares no vert with the root face or with anything
    # the growth made. (The grown list alone does not
    # exclude every tube face - a descent side face can
    # escape it - and a tube face picked as the
    # "landing" would sew the handle to itself.)
    grown_vs = {v.index for f in grown for v in f.verts}
    landing = min(
        (f for f in bm.faces
         if f.normal.x > 0.5
         and f.calc_center_median().x < 0.145
         and not {v.index for v in f.verts}
         & (start_vs | grown_vs)),
        key=lambda f: (f.calc_center_median() - centre).length)
    target = (landing.calc_center_median()
              + landing.normal * 0.004)
    delta = target - end.calc_center_median()
    bmesh.ops.translate(bm, verts=list(end.verts), vec=delta)
    end_verts = list(end.verts)
    land_verts = list(landing.verts)
    bmesh.ops.delete(bm, geom=[end, landing],
                     context="FACES")
    _sew(bm, end_verts, land_verts)
    _push(cup, bm)


# (M1) The bare I keystroke: an inset region created at
# zero thickness has the finished face structure but no
# inner face inside the wall - no tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup, inset=False)
inset_bottom(cup, thickness=0.0)
_save(TMP)
assert not bb._check_first_cup(ctx)
print("CARDWALK_PASS a zero-thickness inset (the bare I "
      "keystroke) does not tick step 1")

# (M1) A stale save: the file holds the unfinished cup,
# the live scene is then finished WITHOUT saving - no
# tick. Saving the finished scene ticks it.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup, inset=False)
_save(TMP)
inset_bottom(cup)
assert not bb._check_first_cup(ctx)
_save(TMP)
assert bb._check_first_cup(ctx)
print("CARDWALK_PASS a stale save does not tick step 1; "
      "saving the finished cup does")

# (M2) The Apply moment itself: reshaped cup, foot,
# Solidify just applied, Subsurf live, NO handle - the
# exact state the re-walk watched tick. No tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx), \
    "step 2 ticked at the Apply with no handle at all"
print("CARDWALK_PASS the Solidify Apply alone does not "
      "tick step 2 (no handle)")

# (M2) The walked mesh's class at the same moment: the
# belly ring only PARTLY picked (his loop cut followed
# the ring his cursor actually caught), the foot flared
# on one side - still no handle, still no tick.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
ring_scale(cup, 0.12, 0.94)
ring_scale(cup, 0.10, 0.97)
ring_slide(cup, -0.10, -0.072)
bm = _bm(cup)
ring = [v for v in bm.verts if abs(v.co.z + 0.072) < 0.004]
sel = [v for v in ring
       if math.atan2(v.co.y, v.co.x) > -0.8]
mx = sorted(v.co.x for v in sel)[len(sel) // 2]
my = sorted(v.co.y for v in sel)[len(sel) // 2]
for v in sel:
    v.co.x = mx + (v.co.x - mx) * 1.06
    v.co.y = my + (v.co.y - my) * 1.06
_push(cup, bm)
ring_scale(cup, -0.12, 0.93)
bm = _bm(cup)
under = [f for f in bm.faces
         if f.calc_center_median().z < -0.119]
out = bmesh.ops.extrude_face_region(bm, geom=under)
verts = {v for g in out["geom"]
         if isinstance(g, bmesh.types.BMFace) for v in g.verts}
bmesh.ops.translate(bm, verts=list(verts),
                    vec=(0.0, 0.0, -0.010))
_push(cup, bm)
add_ring(cup, -0.125, lambda z0, z1: max(z0, z1) < -0.115)
add_ring(cup, -0.115,
         lambda z0, z1: -0.121 < min(z0, z1)
         and max(z0, z1) < -0.05)
bm = _bm(cup)
for v in bm.verts:
    if v.co.z < -0.115 and v.co.x > 0.05:
        v.co.x *= 1.10
_push(cup, bm)
apply_solidify(cup)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx), \
    "a partial belly and a flared foot are not a handle"
print("CARDWALK_PASS a messy handle-less mug (partial "
      "belly, flared foot) does not tick step 2")

# (M3) The join ladder, in the card's own order.
# State A: handle grown, end resting on the body, cap
# still on, nothing sewn - touching is not joined.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
end_c, land_c = grow_capped(cup)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx), \
    "a capped end resting on the body is not a join"
# State B: the four F faces sewn, caps still on - the
# 4-corner join by construction ticks step 2.
bm = _bm(cup)
end_f = _face_at(bm, end_c)
land_f = _face_at(bm, land_c)
_sew(bm, list(end_f.verts), list(land_f.verts))
_push(cup, bm)
_save(TMP)
assert bb._check_mug_reference(ctx), \
    "the 4-corner sewn join must tick step 2"
# State C: the card's last move - delete the two inside
# faces - must not revoke the tick (the re-walk watched
# exactly this un-tick strand the tour).
bm = _bm(cup)
end_f = _face_at(bm, end_c)
land_f = _face_at(bm, land_c)
bmesh.ops.delete(bm, geom=[end_f, land_f], context="FACES")
_push(cup, bm)
_save(TMP)
assert bb._check_mug_reference(ctx), \
    "deleting the inside faces un-ticked step 2"
print("CARDWALK_PASS the join ladder: touching waits, "
      "the 4-corner sew ticks, deleting the inside "
      "faces keeps the tick")

# (M3) The bridge path: both faces deleted with the rims
# pulled to the body - ticked already (the rims face
# each other across no gap), and still ticked once
# Bridge Edge Loops closes them.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
end_c, land_c = grow_capped(cup)
bm = _bm(cup)
end_f = _face_at(bm, end_c)
land_f = _face_at(bm, land_c)
end_loop = list(end_f.verts)
pull = (land_f.calc_center_median()
        - end_f.calc_center_median()) * 0.75
bmesh.ops.delete(bm, geom=[end_f, land_f], context="FACES")
bmesh.ops.translate(bm, verts=end_loop, vec=pull)
_push(cup, bm)
_save(TMP)
assert bb._check_mug_reference(ctx), \
    "bridge-ready rims (faces deleted) un-ticked step 2"
bm = _bm(cup)
bm.edges.ensure_lookup_table()
rim_edges = [e for e in bm.edges if len(e.link_faces) == 1]
by_vert = {}
for e in rim_edges:
    for v in e.verts:
        by_vert.setdefault(v.index, []).append(e)
loops, seen = [], set()
for e in rim_edges:
    if e.index in seen:
        continue
    comp, stack = [], [e]
    while stack:
        g = stack.pop()
        if g.index in seen:
            continue
        seen.add(g.index)
        comp.append(g)
        for v in g.verts:
            stack.extend(by_vert.get(v.index, ()))
    loops.append(comp)
joint = [{v.index for e in c for v in e.verts}
         for c in loops
         if max(v.co.z for e in c for v in e.verts) < 0.10]
assert len(joint) == 2, [len(c) for c in loops]


def rim_cycle(vset):
    # The rim's full cycle: one of its edges borders two
    # overlapping faces (the grown tube doubles a face
    # along the root rim), so a face-count filter drops
    # it; the cycle is every edge inside the rim's verts.
    return [e for e in bm.edges
            if e.verts[0].index in vset
            and e.verts[1].index in vset]


bmesh.ops.bridge_loops(
    bm, edges=rim_cycle(joint[0]) + rim_cycle(joint[1]))
_push(cup, bm)
_save(TMP)
assert bb._check_mug_reference(ctx), \
    "Bridge Edge Loops un-ticked step 2"
print("CARDWALK_PASS the bridge path: rims at the body "
      "tick, Bridge Edge Loops keeps the tick")

# (M3) A handle grown and left hanging in mid-air, end
# capped, never brought back: no tick. (The old join
# test passed this state - a capped tube's only open
# loop is the mouth.)
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
add_ring(cup, 0.03,
         lambda z0, z1: -0.073 < min(z0, z1)
         and max(z0, z1) < 0.101)
bm = _bm(cup)
bm.faces.ensure_lookup_table()
wall = [f for f in bm.faces
        if f.normal.x > 0.5
        and abs(f.calc_center_median().y) < 0.05]
start = max((f for f in wall
             if f.calc_center_median().z < 0.10),
            key=lambda f: f.calc_center_median().z)
end, _f = _extrude_step(bm, start, (0.055, 0.0, 0.010))
end, _f = _extrude_step(bm, end, (0.010, 0.0, 0.055))
_push(cup, bm)
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._check_mug_reference(ctx), \
    "a handle hanging in mid-air ticked step 2"
print("CARDWALK_PASS a capped handle hanging in "
      "mid-air does not tick step 2")

# --- Round 3: the contact tick ---------------------------------------
# Re-walk #2's gap #3, by construction: the handle grown
# home along the wall and pulled to touch - cap on, the
# wall face it covers still present, no join faces - and
# the step ticked anyway, on a bare re-evaluation event.
# The round-2 distance clause read the handle's own
# approach (root rim to descent rings, three or more
# wall-graph steps apart along the surface) as a second
# attachment. This state must wait for a real join.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
end_vs, land_vs = grow_touching(cup)
me = cup.data
polys = [set(p.vertices) for p in me.polygons]
assert end_vs in polys, "the end cap must still be on"
assert land_vs in polys, \
    "the wall face the end covers must still be present"
mixing = [p for p in polys if p & end_vs and p & land_vs]
assert not mixing, "no face may mix end and wall verts"
verts = me.vertices
centre_gap = (
    sum((verts[i].co for i in end_vs),
        verts[0].co * 0.0) / len(end_vs)
    - sum((verts[i].co for i in land_vs),
          verts[0].co * 0.0) / len(land_vs)).length
assert centre_gap < 0.008, centre_gap
_save(TMP)
assert bb._check_first_cup(ctx)
assert not bb._handle_returns(cup), \
    "the touching end read as a returned handle"
assert not bb._check_mug_reference(ctx), \
    "a touching but unsewn handle ticked step 2"
print("CARDWALK_PASS a handle grown home along the wall "
      "and left touching - cap on, wall face present, no "
      "join faces - does not tick step 2")

# --- Round 4: the hugging descent, joined ------------------------------
# The confirmation walk (walk105) failed step 2 the other
# way: the touching tick was dead, but so was the TRUE
# tick - a mug joined by the card's own bridge read False,
# because round 3's veto scanned for a cap-shaped FACE
# and found one in the middle of the handle's descent
# (the tube's rectangular cross-section means cutting
# one face's verts can never strand the end, so the
# articulation clause waves every mid-tube face
# through). The veto now asks the question at the tube's
# two ends: an end is attached when its rim shares an
# edge with a wall-ring vert, and exactly one end
# attached is the dead end. The state that pairing
# produces - hugging descent AND a finished join - is
# built here so the misfire can never hide behind a
# correct-for-the-wrong-reason negative again.
wipe()
dough = make_dough()
cup = make_cup_raw()
finish_part1(cup)
reshape_cup(cup)
apply_solidify(cup)
grow_hugging_joined(cup)
_save(TMP)
assert bb._check_first_cup(ctx)
assert bb._handle_returns(cup), \
    "a hugging descent with a sewn end read as unreturned"
assert bb._check_mug_reference(ctx), \
    "a handle grown home along the wall AND sewn " \
    "did not tick step 2"
print("CARDWALK_PASS a handle grown home along the wall "
      "and sewn at the end ticks step 2 (the walked "
      "pairing: hugging descent, joined end)")

# --- X1: the wrap never loses a word ---------------------------------

texts = []
for pkg in bb.PACKAGES:
    for step in pkg["steps"]:
        texts.extend(step["teach"])
        texts.append(step["skill"])
        texts.append(step["missing"])
for width_px in (250, 300, 360, 490):
    bb._WRAP_PX = width_px
    budget = (width_px - 72) * 0.92
    for text in texts:
        lines = bb._wrap_lines(text, width=44)
        joined = " ".join(" ".join(lines).split())
        assert joined == " ".join(text.split()), \
            (width_px, text[:60], lines)
        for line in lines:
            px = bb._text_px(line)
            if px is not None:
                assert px <= budget + 1.0, (width_px, px, line)
bb._WRAP_PX = None
print("CARDWALK_PASS wrap keeps every word at sidebar widths "
      "250-490px, and every line measures inside the panel")

# --- The walked scene itself -------------------------------------------
# The preserved scene from the failed re-walk: Part 1
# genuinely finished, Part 2 mid-procedure - the handle
# grown but its joint never closed (its two rims stand
# 0.125 m apart in the file), the icing genuinely done.
# The honest tour state is exactly that: step 1 ticked,
# standing at step 2, step 3's work present in the scene.
def _blend_version_int(path):
    """The version number of the Blender that wrote a .blend
    (402 = 4.2, 500 = 5.0), read from its header - or None
    when the header does not parse. Blender 5.0+ writes a
    new header ("BLENDER17-01v0500..."): digits where the
    classic header has its pointer-size byte, and the
    version rides after the 'v' as four digits."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(32)
    except OSError:
        return None
    if not head.startswith(b"BLENDER"):
        return None
    if head[7:8].isdigit():
        tail = head.split(b"v", 1)[1][:4] \
            if b"v" in head else b""
        return int(tail) if tail.isdigit() else 500
    digits = head[9:12]
    return int(digits) if digits.isdigit() else None


WALKED = os.path.expanduser(
    "~/workspace/walk101/home/donut.blend")
if os.path.exists(WALKED):
    walked_ver = _blend_version_int(WALKED)
    running_ver = bpy.app.version[0] * 100 + bpy.app.version[1]
    if walked_ver is not None and walked_ver > running_ver:
        # A Blender only opens files from its own format
        # generation or older: the walked scene was saved by
        # Blender 5.3, so 4.2.5 refuses it outright ("not a
        # blend file"). Skip ONLY this section, out loud -
        # every check above already ran on this Blender.
        print("CARDWALK_SKIP walked-scene section: file is "
              "Blender %d.%d format, running %d.%d"
              % (walked_ver // 100, walked_ver % 100,
                 running_ver // 100, running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=WALKED)
        checks, current = bb.tour_state(ctx)
        assert checks == [True, False, True, False, False,
                          False, False, False], checks
        assert current == 1, checks
        print("CARDWALK_PASS the walked scene reads honestly: "
              "step 1 ticked, standing at step 2, its open "
              "joint unticked")

# --- The re-walk #2 checkpoints --------------------------------------
# The preserved end states of re-walk #2's steps 2 and 3.
# step2_done is gap #3's touching-unsewn mug: step 2 must
# read FALSE on it (round 3's join fix). step3_done is
# the icing whose modifier stack was applied in the
# wrong order under a disclosed rig limitation: step 3
# must read FALSE on it - the fix-round-3 diagnosis
# proved that no-tick correct (the mis-ordered apply
# flattened the whole shell onto the dough's surface;
# every tolerance that would pass it re-admits the
# plain-duplicate cheat), so the fixture is locked in
# here as the apply-order regression case. step1_done
# only has to load cleanly. Same guards as the walked
# scene above: a missing file, or a format the running
# Blender cannot read (the checkpoints are also
# zstd-compressed, which pre-5.0 Blenders refuse),
# skips out loud per file.
CKPT = os.path.expanduser("~/workspace/walk103/checkpoints")
running_ver = bpy.app.version[0] * 100 + bpy.app.version[1]
for name, check, label in (
        ("step2_done.blend", "_check_mug_reference",
         "the touching mug fails step 2"),
        ("step3_done.blend", "_check_icing_hug",
         "the mis-ordered icing fails step 3")):
    path = os.path.join(CKPT, name)
    if not os.path.exists(path):
        print("CARDWALK_SKIP %s not present on this "
              "machine" % name)
        continue
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP %s: file is Blender %d.%d "
              "format, running %d.%d"
              % (name, ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
        continue
    if ver is None and running_ver < 500:
        # No BLENDER header to parse: the checkpoints
        # are zstd-compressed 5.x files, which a pre-5.0
        # Blender refuses outright ("not a blend file").
        print("CARDWALK_SKIP %s: compressed format a "
              "pre-5.0 Blender cannot read, running %d.%d"
              % (name, running_ver // 100,
                 running_ver % 100))
        continue
    bpy.ops.wm.open_mainfile(filepath=path)
    assert getattr(bb, check)(ctx) is False, label
    print("CARDWALK_PASS walked checkpoint %s: %s"
          % (name, label))
path = os.path.join(CKPT, "step1_done.blend")
if not os.path.exists(path):
    print("CARDWALK_SKIP step1_done.blend not present "
          "on this machine")
else:
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP step1_done.blend: file is "
              "Blender %d.%d format, running %d.%d"
              % (ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
    elif ver is None and running_ver < 500:
        print("CARDWALK_SKIP step1_done.blend: "
              "compressed format a pre-5.0 Blender "
              "cannot read, running %d.%d"
              % (running_ver // 100, running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=path)
        print("CARDWALK_PASS walked checkpoint "
              "step1_done.blend loads without error")

# --- The confirmation-walk checkpoints (walk105) ---------------------
# The preserved end states of the confirmation walk of
# the fix-round-3 bytes. step2_done is the mug joined by
# the card's own bridge alternative - every joint edge
# carrying exactly two faces, every clause of the card's
# printed tick contract met - which round 3's veto
# refused: step 2 must read TRUE on it now (round 4's
# end-attachment veto). grow_touching is the same walk's
# touching state - end resting on the wall, cap on, wall
# face present, nothing sewn - and must stay FALSE.
# apply_done is the Apply-moment mug, no handle at all,
# and must stay FALSE. Same guards as the sections
# above, per file.
CKPT105 = os.path.expanduser("~/workspace/walk105/checkpoints")
for name, want, label in (
        ("step2_done.blend", True,
         "the bridged mug ticks step 2"),
        ("grow_touching.blend", False,
         "the touching mug fails step 2"),
        ("apply_done.blend", False,
         "the apply-moment mug fails step 2")):
    path = os.path.join(CKPT105, name)
    if not os.path.exists(path):
        print("CARDWALK_SKIP %s not present on this "
              "machine" % name)
        continue
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP %s: file is Blender %d.%d "
              "format, running %d.%d"
              % (name, ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
        continue
    if ver is None and running_ver < 500:
        print("CARDWALK_SKIP %s: compressed format a "
              "pre-5.0 Blender cannot read, running %d.%d"
              % (name, running_ver // 100,
                 running_ver % 100))
        continue
    bpy.ops.wm.open_mainfile(filepath=path)
    assert bb._check_mug_reference(ctx) is want, label
    print("CARDWALK_PASS confirmation checkpoint %s: %s"
          % (name, label))

# --- The W2 confirmation-walk checkpoints (walk107) ------------------
# The preserved chain of the second confirmation walk,
# run against the fix-round-4 bytes. W2 walked the
# card's own route A - the six-face hand sew - and the
# finished mug never ticked: round 4's veto measured
# the tube's diameter over a set that included the
# wall's own anchored verts, and a sewn landing ties
# the end ring straight to those verts (on this mug
# the patch's top pair IS the root face's bottom pair
# - the card's own procedure produces the shape), so
# the diameter short-circuited through the wall and
# the arc's crown read as the dead end.
# routeA_completed_unticked is that finished mug - sew
# complete, inside faces deleted, saved - and step 2
# must read TRUE on it now (round 5: the anchored
# verts seed the tube's components but never enter
# the measured set). The chain behind it keeps its
# verdicts: apply_done (no handle yet) FALSE,
# grow_touching and ring2_done (the end resting on
# the wall, nothing sewn) FALSE, and the partial sews
# (topface/botface/sidep/quadm - the joint still open)
# FALSE. sewn_done is the completed sew with the
# inside faces still present and reads TRUE: the tick
# is graded at the completed sew, exactly as the join
# ladder above grades its sewn rung True with its
# caps on, and the inside-face delete is graded there
# as must-not-revoke, never as a precondition. Same
# guards as the sections above, per file.
CKPT107 = os.path.expanduser("~/workspace/walk107/checkpoints")
for name, want, label in (
        ("routeA_completed_unticked.blend", True,
         "the route-A sewn mug ticks step 2"),
        ("apply_done.blend", False,
         "the apply-moment mug fails step 2"),
        ("grow_touching.blend", False,
         "the touching mug fails step 2"),
        ("ring2_done.blend", False,
         "the touching mug with its JOIN ring cut "
         "fails step 2"),
        ("topface_done.blend", False,
         "the one-face sew fails step 2"),
        ("botface_done.blend", False,
         "the two-face sew fails step 2"),
        ("sidep_done.blend", False,
         "the four-face sew fails step 2"),
        ("quadm_done.blend", False,
         "the five-face sew fails step 2"),
        ("sewn_done.blend", True,
         "the completed sew ticks step 2 with the "
         "inside faces still present")):
    path = os.path.join(CKPT107, name)
    if not os.path.exists(path):
        print("CARDWALK_SKIP %s not present on this "
              "machine" % name)
        continue
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP %s: file is Blender %d.%d "
              "format, running %d.%d"
              % (name, ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
        continue
    if ver is None and running_ver < 500:
        print("CARDWALK_SKIP %s: compressed format a "
              "pre-5.0 Blender cannot read, running %d.%d"
              % (name, running_ver // 100,
                 running_ver % 100))
        continue
    bpy.ops.wm.open_mainfile(filepath=path)
    assert bb._check_mug_reference(ctx) is want, label
    print("CARDWALK_PASS W2 checkpoint %s: %s"
          % (name, label))

# --- The W3 confirmation-walk checkpoints (walk108) ------------------
# The preserved end states of the third confirmation
# walk, run against the fix-round-5 bytes - the first
# walk to pass step 2 live. step2_finished is the mug
# sewn by the card's own six-face hand sew, inside
# faces deleted, finished and saved: step 2 must read
# TRUE on it. step3_done is the same walk's finished
# icing - the card's stack in the card's order, all
# three modifiers applied, sculpted and saved - and
# the tour must stand at step 4 on it (checks 1-3
# ticked, current == 3). Same guards as the sections
# above, per file.
CKPT108 = os.path.expanduser("~/workspace/walk108/checkpoints")
path = os.path.join(CKPT108, "step2_finished.blend")
if not os.path.exists(path):
    print("CARDWALK_SKIP step2_finished.blend not "
          "present on this machine")
else:
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP step2_finished.blend: "
              "file is Blender %d.%d format, running "
              "%d.%d" % (ver // 100, ver % 100,
                         running_ver // 100,
                         running_ver % 100))
    elif ver is None and running_ver < 500:
        print("CARDWALK_SKIP step2_finished.blend: "
              "compressed format a pre-5.0 Blender "
              "cannot read, running %d.%d"
              % (running_ver // 100,
                 running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=path)
        assert bb._check_mug_reference(ctx) is True, \
            "the W3 sewn mug ticks step 2"
        print("CARDWALK_PASS W3 checkpoint "
              "step2_finished.blend: the sewn mug "
              "ticks step 2")
path = os.path.join(CKPT108, "step3_done.blend")
if not os.path.exists(path):
    print("CARDWALK_SKIP step3_done.blend not present "
          "on this machine")
else:
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP step3_done.blend: file "
              "is Blender %d.%d format, running %d.%d"
              % (ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
    elif ver is None and running_ver < 500:
        print("CARDWALK_SKIP step3_done.blend: "
              "compressed format a pre-5.0 Blender "
              "cannot read, running %d.%d"
              % (running_ver // 100,
                 running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=path)
        checks, current = bb.tour_state(ctx)
        assert checks == [True, True, True, False,
                          False, False, False,
                          False], checks
        assert current == 3, checks
        print("CARDWALK_PASS W3 checkpoint "
              "step3_done.blend: the finished icing "
              "ticks step 3, tour standing at step 4")

# --- Fix round 6: the render proof (walk110, GAP 4-8) ---------------
# Step 4's tick needs "a render exists". The shipped proof
# read the Render Result image - which reports size (0, 0)
# and has_data False after a completed render on Blender
# 5.3 (and after every background render), and whose pixels
# are never saved into the file - or a .png at the scene's
# output path, which the card never sets. A learner
# following the card exactly (F12, no output path) could
# never tick step 4. The fix records the render on the
# scene itself: a render_complete handler sets
# buddy_render_done the moment a render finishes, and the
# record is saved with the file. Locked here in both
# directions on any Blender: never rendered -> the clause
# fails; rendered by the card's exact route -> it passes,
# and still passes after save + reopen. (The factory reset
# first: the walked files above can leave the session in
# Sculpt Mode, where the object operators below will not
# run - and this lock wants a plain, never-rendered scene.)
bpy.ops.wm.read_factory_settings(use_empty=True)
wipe()
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
bpy.ops.object.camera_add(location=(0, -5, 0),
                          rotation=(1.5708, 0, 0))
ctx.scene.camera = ctx.object
bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
ctx.scene.render.filepath = "/tmp/"
assert ctx.scene.buddy_render_done is False
assert bb._render_proof(ctx) is False, \
    "a scene that never rendered must fail the render proof"
print("CARDWALK_PASS render proof: a never-rendered scene "
      "fails the clause")
ctx.scene.render.engine = "CYCLES"
ctx.scene.cycles.samples = 1
ctx.scene.cycles.use_denoising = False
ctx.scene.render.resolution_x = 16
ctx.scene.render.resolution_y = 16
ctx.scene.render.resolution_percentage = 100
bpy.ops.render.render()
assert ctx.scene.buddy_render_done is True
assert bb._render_proof(ctx) is True, \
    "a completed render must pass the render proof"
print("CARDWALK_PASS render proof: a completed render with "
      "no output path (the card's route) passes the clause")
_save(TMP)
bpy.ops.wm.open_mainfile(filepath=TMP)
assert bb._render_proof(ctx) is True, \
    "the render record must survive save + reopen"
print("CARDWALK_PASS render proof: the record survives "
      "save + reopen (progress reads from the scene alone)")

# --- The W4 confirmation-walk checkpoint (walk110) -------------------
# step4_done.blend: the walked, genuinely finished step 4
# that never ticked (GAP 4-8). Its stored output path is
# "/tmp/" - the card's own F12-only state, saved before the
# walk's disclosed branch-2 rescue - so as it stands the
# step must still NOT tick: nothing in the file proves a
# render, and the fix must not invent one. Point the output
# path at a real .png written now (branch 2, unchanged) and
# the step ticks; then clear the path and render for real
# (the card's route, via the new record) and it ticks - and
# stays ticked after save + reopen. The render below runs
# on Cycles because Eevee cannot run headless on this
# machine; no step-4 clause reads the engine. Same guards
# as the sections above.
CKPT110 = os.path.expanduser("~/workspace/walk110/checkpoints")
path = os.path.join(CKPT110, "step4_done.blend")
if not os.path.exists(path):
    print("CARDWALK_SKIP step4_done.blend not present on "
          "this machine")
else:
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP step4_done.blend: file is "
              "Blender %d.%d format, running %d.%d"
              % (ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
    elif ver is None and running_ver < 500:
        print("CARDWALK_SKIP step4_done.blend: compressed "
              "format a pre-5.0 Blender cannot read, "
              "running %d.%d"
              % (running_ver // 100, running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=path)
        assert bb._render_proof(ctx) is False, \
            "no render is proven in the walked file"
        assert bb._check_first_picture(ctx) is False, \
            "the unproven render must hold step 4"
        print("CARDWALK_PASS W4 checkpoint "
              "step4_done.blend: the finished step 4 with "
              "no proven render still waits (no false tick)")
        PNG = TMP + ".png"
        with open(PNG, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n")
        ctx.scene.render.filepath = PNG
        assert bb._render_proof(ctx) is True, \
            "branch 2 (a .png at the output path) must pass"
        assert bb._check_first_picture(ctx) is True, \
            "branch 2 must tick the walked step 4"
        print("CARDWALK_PASS W4 checkpoint "
              "step4_done.blend: branch 2 (output-path .png) "
              "still ticks step 4")
        ctx.scene.render.filepath = "/tmp/"
        assert bb._render_proof(ctx) is False, \
            "with the path cleared the clause waits again"
        ctx.scene.render.engine = "CYCLES"
        ctx.scene.cycles.samples = 1
        ctx.scene.cycles.use_denoising = False
        ctx.scene.render.resolution_x = 16
        ctx.scene.render.resolution_y = 16
        ctx.scene.render.resolution_percentage = 100
        bpy.ops.render.render()
        assert bb._check_first_picture(ctx) is True, \
            "a genuine render must tick the walked step 4"
        checks, current = bb.tour_state(ctx)
        assert current == 4, checks
        print("CARDWALK_PASS W4 checkpoint "
              "step4_done.blend: a genuine render (the "
              "card's F12 route) ticks step 4")
        _save(TMP)
        bpy.ops.wm.open_mainfile(filepath=TMP)
        assert bb._check_first_picture(ctx) is True, \
            "the tick must survive save + reopen"
        print("CARDWALK_PASS W4 checkpoint "
              "step4_done.blend: the tick survives save + "
              "reopen")
        try:
            os.remove(PNG)
        except OSError:
            pass

# --- Fix round 8: the finale's render clause (walk110, GAP 8-4) -----
# Step 8's tick text promises "a fresh render on file", but
# the clause was _render_proof itself: any render from
# earlier in the tour satisfies it - in W4 the tour
# completed at the depth-of-field save on the strength of
# the step-4 rescue render already on file, before any
# step-8 render existed. The finale now reads its own
# record: the render_complete handler sets
# buddy_final_render_done when a render finishes with
# the finale's rig standing complete around it, and
# _check_final_picture reads only that record (see
# _final_render_proof). _render_proof is untouched, so
# step 4's locks above stand as written. Locked here in
# both directions on any Blender: no record -> the clause
# fails; an early-stage record (buddy_render_done, the
# strongest _render_proof witness) -> the finale still
# fails while step 4's proof passes; the final-stage
# record -> it passes. (The factory reset first, as in
# the round-6 lock: this lock wants a plain scene.)
bpy.ops.wm.read_factory_settings(use_empty=True)
wipe()
assert ctx.scene.buddy_final_render_done is False
assert bb._final_render_proof(ctx) is False, \
    "no final-stage record must fail the finale clause"
print("CARDWALK_PASS final render proof: no final-stage "
      "render on record fails the clause")
ctx.scene.buddy_render_done = True
assert bb._render_proof(ctx) is True, \
    "step 4's proof must still accept the early record"
assert bb._final_render_proof(ctx) is False, \
    "an early-stage render must not satisfy the finale"
print("CARDWALK_PASS final render proof: an early-stage "
      "render does not tick the finale (GAP 8-4)")
ctx.scene.buddy_final_render_done = True
assert bb._final_render_proof(ctx) is True, \
    "the final-stage record must pass the finale clause"
print("CARDWALK_PASS final render proof: the final-stage "
      "record passes the clause")

# --- The W4 step-8 checkpoint (walk110) ------------------------------
# step8_done.blend: the walked finale - every scene clause
# dump-verified true by W4 (the parenting chain, a sun at
# 10, the blue sky and white bounce points, two standing
# one-face blockers, the probe at resolution 4, shadow
# Steps 16, the retuned SSS scales, DOF focused on the
# icing). Its render evidence is the finale Eevee render
# saved over the scene's output path - a branch-2 file
# guarded only by the tour's start, which cannot prove
# the render belongs to the final stage (a step-4 render
# at the same path passes the same guard: GAP 8-4
# itself) - and the file was saved by the shipped build,
# before the final-stage record existed, so it carries
# none. The honest read is therefore that the finale
# WAITS: tour standing at step 8 with every other clause
# true. One genuine render with the rig standing makes
# the record and ticks it, and the tick survives save +
# reopen. The render below runs on Cycles because Eevee
# cannot run headless on this machine; no step-8 clause
# reads the engine. Same guards as the sections above.
path = os.path.join(CKPT110, "step8_done.blend")
if not os.path.exists(path):
    print("CARDWALK_SKIP step8_done.blend not present on "
          "this machine")
else:
    ver = _blend_version_int(path)
    if ver is not None and ver > running_ver:
        print("CARDWALK_SKIP step8_done.blend: file is "
              "Blender %d.%d format, running %d.%d"
              % (ver // 100, ver % 100,
                 running_ver // 100, running_ver % 100))
    elif ver is None and running_ver < 500:
        print("CARDWALK_SKIP step8_done.blend: compressed "
              "format a pre-5.0 Blender cannot read, "
              "running %d.%d"
              % (running_ver // 100, running_ver % 100))
    else:
        bpy.ops.wm.open_mainfile(filepath=path)
        checks, current = bb.tour_state(ctx)
        assert current == 7 and checks[:7] == [True] * 7 \
            and checks[7] is False, (checks, current)
        assert bb._final_render_proof(ctx) is False, \
            "the walked file carries no final-stage record"
        assert bb._check_final_picture(ctx) is False, \
            "the finale must wait for a final-stage render"
        print("CARDWALK_PASS W4 checkpoint "
              "step8_done.blend: the walked finale waits - "
              "its on-file render cannot prove the final "
              "stage (no false tick)")
        ctx.scene.render.engine = "CYCLES"
        ctx.scene.cycles.samples = 1
        ctx.scene.cycles.use_denoising = False
        ctx.scene.render.resolution_x = 16
        ctx.scene.render.resolution_y = 16
        ctx.scene.render.resolution_percentage = 100
        bpy.ops.render.render()
        assert ctx.scene.buddy_final_render_done is True, \
            "a render with the rig standing must set the record"
        assert bb._check_final_picture(ctx) is True, \
            "a fresh final-stage render must tick the finale"
        checks, current = bb.tour_state(ctx)
        assert current == 8, checks
        print("CARDWALK_PASS W4 checkpoint "
              "step8_done.blend: a fresh render at the "
              "final step ticks the finale")
        _save(TMP)
        bpy.ops.wm.open_mainfile(filepath=TMP)
        assert bb._check_final_picture(ctx) is True, \
            "the finale tick must survive save + reopen"
        print("CARDWALK_PASS W4 checkpoint "
              "step8_done.blend: the tick survives save + "
              "reopen")

try:
    os.remove(TMP)
except OSError:
    pass
print("CARD_WALK_ALL_PASS")
