"""Blender Buddy job-flow proof (the community patterns).

The flows are the community's ways of working turned into
packages: hard-surface modelling, making a model look real,
and 3D-print prep - in the order the community's guides teach
them (redesign/COMMUNITY_PATTERNS.md). Like the Donut, a flow
teaches and the scene proves each step; unlike the Donut, a
flow's gates can already be true when you arrive (a locked
size is a locked size), so the walk asserts each step's check
after its reference build, and that the whole flow reads done
at the end - not that steps complete one at a time.

Run: blender -b --factory-startup --python tests/test_flows.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bpy  # noqa: E402
import blender_buddy as bb  # noqa: E402

bb.register()

flows = [p for p in bb.PACKAGES if p.get("kind") == "flow"]
assert {p["id"] for p in flows} == {"hard_surface", "look_real",
                                    "print_ready", "sculpt_clay",
                                    "sculpt_symmetry", "sculpt_dyntopo",
                                    "sculpt_masks",
                                    "sculpt_multires", "anim_move",
                                    "anim_ease", "anim_camera",
                                    "anim_character",
                                    "anim_loop", "anim_path",
                                    "anim_follow",
                                    "anim_scale", "anim_bounce",
                                    "anim_swing", "anim_color",
                                    "anim_fade",
                                    "anim_pulse",
                                    "anim_flip",
                                    "anim_stretch",
                                    "anim_orbit",
                                    "anim_roll",
                                    "anim_fall",
                                    "anim_rise",
                                    "anim_shrink",
                                    "anim_spin",
                                    "anim_shake",
                                    "anim_slide",
                                    "anim_pace",
                                    "anim_tilt",
                                    "anim_squash",
                                    "anim_hop",
                                    "anim_zigzag",
                                    "anim_climb",
                                    "anim_descend",
                                    "anim_hover",
                                    "anim_land",
                                    "anim_glide",
                                    "anim_sway",
                                    "anim_bow",
                                    "anim_nod",
                                    "anim_wag",
                                    "anim_turn",
                                    "anim_bob",
                                    "anim_float",
                                    "anim_dip",
                                    "anim_sidestep",
                                    "anim_backstep",
                                    "anim_forwardstep",
                                    "anim_stepup",
                                    "anim_stepdown",
                                    "anim_crouch",
                                    "anim_standup",
                                    "anim_widen",
                                    "anim_narrow",
                                    "anim_lengthen",
                                    "anim_shorten",
                                    "anim_thicken",
                                    "anim_thin",
                                    "anim_taller",
                                    "anim_sideturn",
                                    "anim_leap",
                                    "anim_dive",
                                    "anim_lookback",
                                    "anim_diagonal",
                                    "anim_backdiagonal",
                                    "anim_otherdiagonal",
                                    "anim_backotherdiagonal",
                                    "anim_othersideturn",
                                    "anim_othersidestep",
                                    "anim_otherspin",
                                    "anim_otherturn",
                                    "anim_otherlookback",
                                    "anim_otherorbit",
                                    "anim_otherroll",
                                    "anim_otherflip",
                                    "anim_othertilt",
                                    "anim_otherbow",
                                    "anim_othernod",
                                    "anim_otherwag",
                                    "anim_othersway",
                                    "anim_otherswing",
                                    "anim_otherleap"}, [p["id"] for p in bb.PACKAGES]
for pkg in flows:
    for step in pkg["steps"]:
        assert "tools" in step, (pkg["id"], step["title"])
        for tid in step["tools"]:
            assert tid in bb.ACTIONS_BY_ID, (pkg["id"], tid)
print("FLOWS_PASS eighty-six flows registered; every step's "
      "tools are real Buddy buttons")


def walk(pkg_id, cycles=False):
    bpy.ops.wm.read_factory_settings(use_empty=False)
    ctx = bpy.context
    bpy.ops.buddy.tour_start(package=pkg_id)
    if cycles:
        ctx.scene.render.engine = "CYCLES"
        ctx.scene.cycles.samples = 16
        ctx.scene.render.resolution_x = 320
        ctx.scene.render.resolution_y = 240
    pkg = bb.PACKAGES_BY_ID[pkg_id]
    for i, step in enumerate(pkg["steps"]):
        bpy.ops.buddy.tour_do(step=i)
        checks, _current = bb.tour_state(ctx)
        assert checks[i], (f"{pkg_id} step {i} ({step['title']}) "
                           f"not proven: {checks}")
        print(f"FLOWS_PASS {pkg_id} step {i + 1}: {step['title']}")
    checks, current = bb.tour_state(ctx)
    assert all(checks) and current == len(pkg["steps"]), checks
    print(f"FLOWS_PASS {pkg_id}: all {len(pkg['steps'])} steps proven")


walk("hard_surface")
walk("look_real", cycles=True)
walk("print_ready")
walk("sculpt_clay")
walk("sculpt_symmetry")
walk("sculpt_dyntopo")
walk("sculpt_masks")
walk("sculpt_multires")
walk("anim_move")
walk("anim_ease")
walk("anim_camera")
walk("anim_character")
walk("anim_loop")
walk("anim_path")
walk("anim_follow")
walk("anim_scale")
walk("anim_bounce")
walk("anim_swing")
walk("anim_color")
walk("anim_fade")
walk("anim_pulse")
walk("anim_flip")
walk("anim_stretch")
walk("anim_orbit")
walk("anim_roll")
walk("anim_fall")
walk("anim_rise")
walk("anim_shrink")
walk("anim_spin")
walk("anim_shake")
walk("anim_slide")
walk("anim_pace")
walk("anim_tilt")
walk("anim_squash")
walk("anim_hop")
walk("anim_zigzag")
walk("anim_climb")
walk("anim_descend")
walk("anim_hover")
walk("anim_land")
walk("anim_glide")
walk("anim_sway")
walk("anim_bow")
walk("anim_nod")
walk("anim_wag")
walk("anim_turn")
walk("anim_bob")
walk("anim_float")
walk("anim_dip")
walk("anim_sidestep")
walk("anim_backstep")
walk("anim_forwardstep")
walk("anim_stepup")
walk("anim_stepdown")
walk("anim_crouch")
walk("anim_standup")
walk("anim_widen")
walk("anim_narrow")
walk("anim_lengthen")
walk("anim_shorten")
walk("anim_thicken")
walk("anim_thin")
walk("anim_taller")
walk("anim_sideturn")
walk("anim_leap")
walk("anim_dive")
walk("anim_lookback")
walk("anim_diagonal")
walk("anim_backdiagonal")
walk("anim_otherdiagonal")
walk("anim_backotherdiagonal")
walk("anim_othersideturn")
walk("anim_othersidestep")
walk("anim_otherspin")
walk("anim_otherturn")
walk("anim_otherlookback")
walk("anim_otherorbit")
walk("anim_otherroll")
walk("anim_otherflip")
walk("anim_othertilt")
walk("anim_otherbow")
walk("anim_othernod")
walk("anim_otherwag")
walk("anim_othersway")
walk("anim_otherswing")
walk("anim_otherleap")

# --- sculpt_symmetry negatives: the mirror must be proven ------
# A plain ball ticks only step 1 (it is symmetric, but nothing
# has been sculpted), and big work done on one side only - the
# mirror never in effect - must not tick the mirrored step.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_symmetry")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS sculpt_symmetry negative: a plain ball ticks "
      "only step 1")
main = bb._flow_main(ctx)
bb._sculpt_push(main, [((1, 0.2, 0.3), 0.38, 0.55),
                       ((-0.4, 0.1, 1), -0.30, 0.50)])
checks, _current = bb.tour_state(ctx)
assert not checks[1], checks
print("FLOWS_PASS sculpt_symmetry negative: one-sided work "
      "does not prove the mirror")

# --- sculpt_dyntopo negatives: the contrast must be proven ----
# A plain coarse ball ticks only step 1; DynTopo switched on
# with no work does not tick the worked step; and an EVEN fine
# surface (a subdivided ball - the remesh signature) worked
# one-sidedly does not tick it either: even is not DynTopo.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_dyntopo")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS sculpt_dyntopo negative: a plain coarse ball "
      "ticks only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS sculpt_dyntopo negative: DynTopo on with no "
      "work does not prove the worked step")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_dyntopo")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode="SCULPT")
bb._sculpt_push(main, [((0.6, -0.7, 0.4), 0.20, 0.35)])
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS sculpt_dyntopo negative: an even fine surface "
      "does not prove DynTopo work")

# --- sculpt_masks negatives: the divisions must be proven --
# A plain ball ticks only step 1; a face set alone does not
# tick the mask step; a mask over EVERYTHING does not tick
# it either (masking everything protects nothing); and work
# done ignoring the mask - the patch dragged along with the
# rest - does not tick the protected-work step.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_masks")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS sculpt_masks negative: a plain ball ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS sculpt_masks negative: a face set alone "
      "does not prove the mask")
bpy.ops.buddy.tour_do(step=2)
main = bb._flow_main(ctx)
attr = main.data.attributes[".sculpt_mask"]
for d in attr.data:
    d.value = 1.0
main.data.update()
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS sculpt_masks negative: a mask over "
      "everything does not prove the mask step")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_masks")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
bpy.ops.buddy.tour_do(step=2)
main = bb._flow_main(ctx)
bb._sculpt_push(main, [(bb._MASK_DIR, 0.30, 0.35),
                       ((1, 0.2, 0.3), 0.38, 0.55),
                       ((-0.4, 0.1, 1), -0.30, 0.50)])
checks, _current = bb.tour_state(ctx)
assert not checks[3], checks
print("FLOWS_PASS sculpt_masks negative: work that drags "
      "the masked patch does not prove protection")

# --- sculpt_multires negatives: the levels must be proven --
# A plain ball ticks only step 1; Multires levels with no
# work do not tick the worked steps; big forms alone do not
# tick the detail step (the detail bar sits where smooth
# forms cannot reach); and detail worked WITHOUT Multires
# does not tick it either - the levels are part of the proof.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_multires")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS sculpt_multires negative: a plain ball "
      "ticks only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2] and not checks[3], checks
print("FLOWS_PASS sculpt_multires negative: levels with no "
      "work do not prove the worked steps")
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[3], checks
print("FLOWS_PASS sculpt_multires negative: big forms alone "
      "do not prove fine detail")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="sculpt_multires")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=2)
bpy.ops.buddy.tour_do(step=3)
checks, _current = bb.tour_state(ctx)
assert not checks[3], checks
print("FLOWS_PASS sculpt_multires negative: detail without "
      "Multires does not prove the detail step")


# --- anim_move negatives: the memories must be proven -------
# A plain thing ticks only step 1 (it exists, nothing is
# remembered); one starting memory alone does not tick the
# moved step; and a second memory at nearly the same place
# does not prove travel either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_move")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_move negative: a plain thing ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2] and not checks[3], checks
print("FLOWS_PASS anim_move negative: one memory alone "
      "does not prove movement")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0.2, 0.0, 0.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_move negative: a second memory at "
      "nearly the same place does not prove travel")

# --- anim_ease negatives: the pace must be chosen ------------
# A plain thing ticks nothing (there is no journey to ease);
# a travelling move on Blender's default curve does not tick
# the eased step (the default is already gentle - the easing
# must be CHOSEN on the memories, not inherited); and an
# eased two-memory journey does not tick the bend step.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_ease")
checks, _current = bb.tour_state(ctx)
assert not any(checks), checks
print("FLOWS_PASS anim_ease negative: a plain scene ticks "
      "no steps")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not checks[1] and not checks[2], checks
print("FLOWS_PASS anim_ease negative: a default-curve move "
      "does not prove the eased step")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_ease negative: an eased straight "
      "journey does not prove the bend step")

# --- anim_camera negatives: the aim must be proven ---------
# A plain factory scene ticks only step 1 (it already has a
# camera and a cube - the shot's raw material, nothing
# remembered); one starting memory alone does not tick the
# moved step; and a camera moved WITHOUT its facing
# remembered at the new place does not tick the aimed step -
# from the moved place, the old facing misses the subject
# by a wide angle (probed before building: 1.36 rad against
# the 0.30 bar).
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_camera")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_camera negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2] and not checks[3], checks
print("FLOWS_PASS anim_camera negative: one memory alone "
      "does not prove the camera move")
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[3], checks
print("FLOWS_PASS anim_camera negative: a moved camera with "
      "its old facing does not prove the aim")

# --- anim_character negatives: the parts must be proven ----
# A plain factory scene ticks NO steps (it has no skeleton
# at all - probed before building); a character with only
# its first pose remembered does not tick the moved step;
# and one part moving alone does not tick the second-part
# step.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_character")
checks, _current = bb.tour_state(ctx)
assert not any(checks), checks
print("FLOWS_PASS anim_character negative: a plain scene "
      "ticks no steps")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[0] and checks[1] and not checks[2] \
    and not checks[3], checks
print("FLOWS_PASS anim_character negative: one pose alone "
      "does not prove a moved part")
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[3], checks
print("FLOWS_PASS anim_character negative: one part moving "
      "does not prove the second part")

# --- anim_loop negatives: the loop must be proven ---------
# A plain scene ticks no steps (nothing is remembered);
# a travelling move alone does not tick the repeat step;
# a repeating straight move does not tick the joined step
# (its ends are different places, so it would jump); and a
# joined move with no repeat rule does not tick the repeat
# step either - both halves of a loop are required.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_loop")
checks, _current = bb.tour_state(ctx)
assert not any(checks), checks
print("FLOWS_PASS anim_loop negative: a plain scene ticks "
      "no steps")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not checks[1] and not checks[2], checks
print("FLOWS_PASS anim_loop negative: a travelling move "
      "alone does not prove the repeat")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_loop negative: a repeating straight "
      "move does not prove the joined ends")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_loop")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[1], checks
print("FLOWS_PASS anim_loop negative: joined ends without "
      "the repeat rule do not prove the repeat")

# --- anim_path negatives: the journey must be proven -----
# A plain factory scene ticks only step 1 (the cube is a
# traveller, nothing drawn or tied); a drawn path alone
# does not tick the on-path step; and a traveller tied to
# the path with no travel remembered does not tick the
# travel step - the rule must carry the journey.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_path")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_path negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2] and not checks[3], checks
print("FLOWS_PASS anim_path negative: a drawn path alone "
      "does not prove the tie")
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[3], checks
print("FLOWS_PASS anim_path negative: tied to the path "
      "with no travel does not prove the journey")

# --- anim_follow negatives: the pair must be proven ------
# A plain scene ticks only step 1 (the cube is a leader,
# nothing else); a leader's move alone does not tick the
# second-thing step; a second thing sitting untied does
# not tick the tie step; and a tied pair whose leader
# never travels does not prove the finish - the follower
# must really be carried.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_follow")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_follow negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2] and not checks[3], checks
print("FLOWS_PASS anim_follow negative: a travelling leader "
      "alone does not prove the second thing")
bpy.ops.buddy.tour_do(step=2)
checks, _current = bb.tour_state(ctx)
assert checks[2] and not checks[3] and not checks[4], checks
print("FLOWS_PASS anim_follow negative: a second thing "
      "untied does not prove the tie")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_follow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=2)
bpy.ops.buddy.tour_do(step=3)
checks, _current = bb.tour_state(ctx)
assert checks[3] and not checks[4], checks
print("FLOWS_PASS anim_follow negative: tied to a leader "
      "that never travels does not prove the finish")

# --- anim_scale negatives: the grow must be proven --------
# A plain scene ticks only step 1; a starting size alone
# does not tick the grow step; and a small nudge of size
# (1.2 times) does not prove a real grow either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_scale")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_scale negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_scale negative: a starting size "
      "alone does not prove the grow")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1.2, 1.2, 1.2)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_scale negative: a small nudge of "
      "size does not prove the grow")

# --- anim_bounce negatives: the bounce must be proven ----
# A plain scene ticks only step 1; a starting place alone
# does not tick the bounce step; a straight rise that never
# comes back down does not prove a bounce; and a small hop
# (half a unit) does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bounce")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_bounce negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_bounce negative: a starting place "
      "alone does not prove the bounce")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0, 0, 2.5)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bounce negative: a straight rise "
      "that never comes back does not prove the bounce")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bounce")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.location = (0, 0, 0.5)
main.keyframe_insert(data_path="location", frame=24)
ctx.scene.frame_set(48)
main.location = (0, 0, 0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bounce negative: a small hop does "
      "not prove the bounce")

# --- anim_swing negatives: the swing must be proven ------
# A plain scene ticks only step 1; a starting lean alone
# does not tick the swing step; a one-way turn that ends
# leaned the other way does not prove a swing; a tip that
# never crosses the middle (0 -> 1.2 -> 0) does not prove
# one either; and a small sway does not prove one.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_swing")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_swing negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_swing negative: a starting lean "
      "alone does not prove the swing")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0, 0.7, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_swing negative: a one-way turn "
      "does not prove the swing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_swing")
bpy.ops.buddy.tour_do(step=0)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.rotation_euler = (0, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=1)
ctx.scene.frame_set(24)
main.rotation_euler = (0, 1.2, 0)
main.keyframe_insert(data_path="rotation_euler", frame=24)
ctx.scene.frame_set(48)
main.rotation_euler = (0, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_swing negative: a tip that never "
      "crosses the middle does not prove the swing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_swing")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.rotation_euler = (0, 0.2, 0)
main.keyframe_insert(data_path="rotation_euler", frame=24)
ctx.scene.frame_set(48)
main.rotation_euler = (0, -0.2, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_swing negative: a small sway does "
      "not prove the swing")

# --- anim_color negatives: the change must be proven -----
# A plain scene ticks only step 1; a starting colour alone
# does not tick the change step; and a nudge of the same
# colour does not prove a change either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_color")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_color negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_color negative: a starting colour "
      "alone does not prove the change")
main = bb._flow_main(ctx)
sock = bb._color_socket(main)
ctx.scene.frame_set(48)
sock.default_value = (0.75, 0.2, 0.1, 1.0)
sock.keyframe_insert(data_path="default_value", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_color negative: a nudge of the same "
      "colour does not prove the change")

# --- anim_fade negatives: the fade must be proven --------
# A plain scene ticks only step 1; a solid start alone
# does not tick the fade step; and a slight dimming does
# not prove a fade either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_fade")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_fade negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_fade negative: a solid start "
      "alone does not prove the fade")
main = bb._flow_main(ctx)
sock = bb._fade_socket(main)
ctx.scene.frame_set(48)
sock.default_value = 0.8
sock.keyframe_insert(data_path="default_value", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_fade negative: a slight dimming "
      "does not prove the fade")

# --- anim_pulse negatives: the pulse must be proven -----
# A plain scene ticks only step 1; a starting size alone
# does not tick the pulse step; a grow that never settles
# does not prove a pulse; and a small swell does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pulse")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_pulse negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_pulse negative: a starting size "
      "alone does not prove the pulse")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (2.5, 2.5, 2.5)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pulse negative: a grow that never "
      "settles does not prove the pulse")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pulse")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.scale = (1.3, 1.3, 1.3)
main.keyframe_insert(data_path="scale", frame=24)
ctx.scene.frame_set(48)
main.scale = (1, 1, 1)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pulse negative: a small swell does "
      "not prove the pulse")

# --- anim_flip negatives: the flip must be proven -------
# A plain scene ticks only step 1; an upright start alone
# does not tick the flip step; a half flip that ends
# upside down does not prove a flip; and a rock back and
# forth does not prove one either.
import math as _math
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_flip")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_flip negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_flip negative: an upright start "
      "alone does not prove the flip")
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.rotation_euler = (_math.pi, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=24)
ctx.scene.frame_set(48)
main.rotation_euler = (_math.pi, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_flip negative: a half flip that "
      "ends upside down does not prove the flip")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_flip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.rotation_euler = (0.5, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=24)
ctx.scene.frame_set(48)
main.rotation_euler = (0, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_flip negative: a rock back and "
      "forth does not prove the flip")

# --- anim_stretch negatives: the stretch must be proven --
# A plain scene ticks only step 1; a starting size alone
# does not tick the stretch step; a grow that swells every
# axis together does not prove a stretch; and a small tug
# does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stretch")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_stretch negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_stretch negative: a starting size "
      "alone does not prove the stretch")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (2.5, 2.5, 2.5)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stretch negative: a grow on every "
      "axis does not prove the stretch")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stretch")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1.3, 1, 1)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stretch negative: a small tug does "
      "not prove the stretch")

# --- anim_orbit negatives: the orbit must be proven --
# A plain scene ticks only step 1; a starting place alone
# does not tick the orbit step; a straight move does not
# prove an orbit; and a quarter arc does not prove one
# either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_orbit")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_orbit negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_orbit negative: a starting place "
      "alone does not prove the orbit")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (8, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_orbit negative: a straight move does "
      "not prove the orbit")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_orbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0, 3, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_orbit negative: a quarter arc does "
      "not prove the orbit")

# --- anim_roll negatives: the roll must be proven --
# A plain scene ticks only step 1; a remembered start alone
# does not tick the roll step; a slide (travel without
# turning) does not prove a roll; a spin on the spot
# (turning without travel) does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_roll")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_roll negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_roll negative: a remembered start "
      "alone does not prove the roll")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (2, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_roll negative: a slide does not "
      "prove the roll")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_roll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0, -4, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_roll negative: a spin on the spot "
      "does not prove the roll")

# --- anim_fall negatives: the fall must be proven --
# A plain scene ticks only step 1; a remembered high start
# alone does not tick the fall step; a sideways slide at
# height (no drop) does not prove a fall; a small dip
# (0.5 of drop) does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_fall")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_fall negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_fall negative: a high start alone "
      "does not prove the fall")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (4, 0, 4)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_fall negative: a sideways slide "
      "does not prove the fall")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_fall")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0, 0, 3.5)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_fall negative: a small dip does "
      "not prove the fall")

# --- anim_rise negatives: the rise must be proven --
# A plain scene ticks only step 1; a remembered ground
# start alone does not tick the rise step; a fall (ending
# low, rise negative) does not prove a rise; a small lift
# (0.5 of rise) does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_rise")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_rise negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_rise negative: a ground start alone "
      "does not prove the rise")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (0, 0, 4)
main.keyframe_insert(data_path="location", frame=1)
ctx.scene.frame_set(48)
main.location = (0, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_rise negative: a fall does not "
      "prove the rise")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_rise")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0, 0, 1.5)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_rise negative: a small lift does "
      "not prove the rise")

# --- anim_shrink negatives: the shrink must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the shrink step; a grow does
# not prove a shrink; a small shrink (0.8) does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shrink")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_shrink negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_shrink negative: a starting size alone "
      "does not prove the shrink")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (2.5, 2.5, 2.5)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shrink negative: a grow does not "
      "prove the shrink")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shrink")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (0.8, 0.8, 0.8)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shrink negative: a small shrink does "
      "not prove the shrink")

# --- anim_spin negatives: the spin must be proven --
# A plain scene ticks only step 1; a remembered starting
# facing alone does not tick the spin step; a half spin
# does not prove a spin; a flip over the side does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_spin")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_spin negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_spin negative: a starting facing alone "
      "does not prove the spin")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0.0, 0.0, 3.1416)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_spin negative: a half spin does not "
      "prove the spin")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_spin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(24)
main.rotation_euler = (3.1416, 0.0, 0.0)
main.keyframe_insert(data_path="rotation_euler", frame=24)
ctx.scene.frame_set(48)
main.rotation_euler = (6.2832, 0.0, 0.0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_spin negative: a flip does not "
      "prove the spin")

# --- anim_shake negatives: the shake must be proven --
# A plain scene ticks only step 1; a remembered home place
# alone does not tick the shake step; a one-way move does
# not prove a shake; a bounce up and down does not prove
# one; a small wiggle does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shake")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_shake negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_shake negative: a home place alone "
      "does not prove the shake")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (3, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shake negative: a one-way move does "
      "not prove the shake")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shake")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((12, 3), (24, 1), (36, 3), (48, 1)):
    ctx.scene.frame_set(f)
    main.location = (0, 0, z)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shake negative: a bounce does not "
      "prove the shake")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shake")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((10, -0.2), (19, 0.2), (29, -0.2), (38, 0.2),
             (48, 0)):
    ctx.scene.frame_set(f)
    main.location = (x, 0, 1)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shake negative: a small wiggle does "
      "not prove the shake")

# --- anim_slide negatives: the slide must be proven --
# A plain scene ticks only step 1; a remembered starting
# place alone does not tick the slide step; a rise does
# not prove a slide; a small shuffle does not prove one;
# a bounce does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_slide")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_slide negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_slide negative: a starting place "
      "alone does not prove the slide")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0, 0, 4)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_slide negative: a rise does not "
      "prove the slide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_slide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (0.5, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_slide negative: a small shuffle does "
      "not prove the slide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_slide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((12, 3), (24, 1), (36, 3), (48, 1)):
    ctx.scene.frame_set(f)
    main.location = (0, 0, z)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_slide negative: a bounce does not "
      "prove the slide")

# --- anim_pace negatives: the pace must be proven --
# A plain scene ticks only step 1; a remembered home
# place alone does not tick the pace step; a one-way
# slide does not prove a pace; a small back-and-forth
# does not prove one; a bounce does not prove one
# either; a shake does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pace")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_pace negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_pace negative: a home place "
      "alone does not prove the pace")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.location = (3, 0, 1)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pace negative: a one-way slide does "
      "not prove the pace")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pace")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((24, 0.5), (48, 0)):
    ctx.scene.frame_set(f)
    main.location = (x, 0, 1)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pace negative: a small back-and-forth "
      "does not prove the pace")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pace")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((12, 3), (24, 1), (36, 3), (48, 1)):
    ctx.scene.frame_set(f)
    main.location = (0, 0, z)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pace negative: a bounce does not "
      "prove the pace")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_pace")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((10, -0.7), (19, 0.7), (29, -0.7), (38, 0.7), (48, 0)):
    ctx.scene.frame_set(f)
    main.location = (x, 0, 1)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_pace negative: a shake does not "
      "prove the pace")

# --- anim_tilt negatives: the tilt must be proven --
# A plain scene ticks only step 1; a remembered upright
# facing alone does not tick the tilt step; a spin does
# not prove a tilt; a flip does not prove one; a small
# lean does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_tilt")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_tilt negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_tilt negative: an upright facing "
      "alone does not prove the tilt")
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_tilt negative: a spin does not "
      "prove the tilt")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_tilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_tilt negative: a flip does not "
      "prove the tilt")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_tilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0.25, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_tilt negative: a small lean does not "
      "prove the tilt")

# --- anim_squash negatives: the squash must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the squash step; a shrink does
# not prove a squash; a pulse does not prove one; a small
# squash does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_squash")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_squash negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_squash negative: a starting size "
      "alone does not prove the squash")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (0.4, 0.4, 0.4)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_squash negative: a shrink does not "
      "prove the squash")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_squash")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_squash negative: a pulse does not "
      "prove the squash")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_squash")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.1, 1.1, 0.8)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_squash negative: a small squash does "
      "not prove the squash")

# --- anim_hop negatives: the hop must be proven --
# A plain scene ticks only step 1; a remembered starting
# place alone does not tick the hop step; a bounce in its
# own place does not prove a hop; a slide does not prove
# one; a small hop does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hop")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_hop negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_hop negative: a starting place "
      "alone does not prove the hop")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0], start[1], start[2] + 2.5)),
             (48, start)):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hop negative: a bounce in its own "
      "place does not prove the hop")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hop")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2])),
             (48, (start[0] + 3.0, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hop negative: a slide does not "
      "prove the hop")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hop")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 0.5, start[1], start[2] + 0.5)),
             (48, (start[0] + 1.0, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hop negative: a small hop does "
      "not prove the hop")

# --- anim_zigzag negatives: the zigzag must be proven --
# A plain scene ticks only step 1; a remembered starting
# place alone does not tick the zigzag step; a straight
# slide does not prove a zigzag; a small zigzag does not
# prove one; a hop that leaves the ground does not prove
# one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_zigzag")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_zigzag negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_zigzag negative: a starting place "
      "alone does not prove the zigzag")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 2.4, start[1], start[2])),
             (48, (start[0] + 4.8, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_zigzag negative: a straight slide "
      "does not prove the zigzag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_zigzag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 0.6, start[1] + 0.4, start[2])),
             (48, (start[0] + 1.2, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_zigzag negative: a small zigzag does "
      "not prove the zigzag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_zigzag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2] + 2.0)),
             (48, (start[0] + 3.0, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_zigzag negative: a hop does "
      "not prove the zigzag")

# --- anim_climb negatives: the climb must be proven --
# A plain scene ticks only step 1; a remembered starting
# place alone does not tick the climb step; a rise on its
# own place does not prove a climb; a slide does not prove
# one; a hop does not prove one; a small climb does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_climb")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_climb negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_climb negative: a starting place "
      "alone does not prove the climb")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0], start[1], start[2] + 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_climb negative: a rise on its own "
      "place does not prove the climb")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_climb")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0] + 3.0, start[1], start[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_climb negative: a slide does not "
      "prove the climb")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_climb")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2] + 2.0)),
             (48, (start[0] + 3.0, start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_climb negative: a hop does "
      "not prove the climb")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_climb")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 0.5, start[1], start[2] + 0.5)),
             (48, (start[0] + 1.0, start[1], start[2] + 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_climb negative: a small climb does "
      "not prove the climb")

# --- anim_descend negatives: the descend must be proven --
# A plain scene ticks only step 1; a remembered high
# starting place alone does not tick the descend step; a
# fall on its own place does not prove a descend; a slide
# does not prove one; a climb does not prove one; a small
# descend does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_descend")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_descend negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_descend negative: a high starting place "
      "alone does not prove the descend")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0], start[1], start[2] - 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_descend negative: a fall on its own "
      "place does not prove the descend")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_descend")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0] + 3.0, start[1], start[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_descend negative: a slide does not "
      "prove the descend")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_descend")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2] + 1.5)),
             (48, (start[0] + 3.0, start[1], start[2] + 3.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_descend negative: a climb does "
      "not prove the descend")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_descend")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 0.5, start[1], start[2] - 0.5)),
             (48, (start[0] + 1.0, start[1], start[2] - 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_descend negative: a small descend does "
      "not prove the descend")


# --- anim_hover negatives: the hover must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the hover step; a
# plain rise does not prove a hover; a bounce does not
# prove one; a slide does not prove one; a small lift
# does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hover")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_hover negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_hover negative: a ground starting place "
      "alone does not prove the hover")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0], start[1], start[2] + 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hover negative: a plain rise "
      "does not prove the hover")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hover")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0], start[1], start[2] + 3.0)),
             (48, (start[0], start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hover negative: a bounce does not "
      "prove the hover")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hover")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0] + 3.0, start[1], start[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hover negative: a slide does not "
      "prove the hover")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_hover")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0], start[1], start[2] + 1.0)),
             (48, (start[0], start[1], start[2] + 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_hover negative: a small lift does "
      "not prove the hover")

# --- anim_land negatives: the landing must be proven --
# A plain scene ticks only step 1; a remembered high
# starting place alone does not tick the land step; a
# plain fall does not prove a landing; a bounce does not
# prove one; a slide at height does not prove one; a
# small drop does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_land")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_land negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_land negative: a high starting place "
      "alone does not prove the landing")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0], start[1], start[2] - 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_land negative: a plain fall "
      "does not prove the landing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_land")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0], start[1], start[2] - 3.0)),
             (48, (start[0], start[1], start[2]))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_land negative: a bounce does not "
      "prove the landing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_land")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0] + 3.0, start[1], start[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_land negative: a slide at height does "
      "not prove the landing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_land")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0], start[1], start[2] - 1.0)),
             (48, (start[0], start[1], start[2] - 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_land negative: a small drop does "
      "not prove the landing")

# --- anim_glide negatives: the glide must be proven --
# A plain scene ticks only step 1; a remembered high
# starting place alone does not tick the glide step; a
# fall on the spot does not prove a glide; a diagonal
# descend does not prove one; a slide at height does
# not prove one; a hop does not prove one; a small
# glide does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_glide")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_glide negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_glide negative: a high starting place "
      "alone does not prove the glide")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0], start[1], start[2] - 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_glide negative: a fall on the spot "
      "does not prove the glide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_glide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2] - 1.5)),
             (48, (start[0] + 3.0, start[1], start[2] - 3.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_glide negative: a diagonal descend does "
      "not prove the glide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_glide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (start[0] + 3.0, start[1], start[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_glide negative: a slide at height does "
      "not prove the glide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_glide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 1.5, start[1], start[2] - 1.0)),
             (48, (start[0] + 3.0, start[1], 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_glide negative: a hop does not "
      "prove the glide")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_glide")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
start = tuple(main.location)
for f, v in ((24, (start[0] + 0.5, start[1], start[2] - 0.15)),
             (48, (start[0] + 1.0, start[1], start[2] - 0.3))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_glide negative: a small glide does "
      "not prove the glide")

# --- anim_sway negatives: the sway must be proven --
# A plain scene ticks only step 1; a remembered upright
# facing alone does not tick the sway step; a tilt does
# not prove a sway; a spin does not prove one; a small
# sway does not prove one; a one-way rock does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sway")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_sway negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_sway negative: an upright facing "
      "alone does not prove the sway")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0.8, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sway negative: a tilt does not "
      "prove the sway")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sway negative: a spin does not "
      "prove the sway")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((17, 0.2), (33, -0.2), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sway negative: a small sway does "
      "not prove the sway")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((24, 0.8), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sway negative: a one-way rock does "
      "not prove the sway")

# --- anim_bow negatives: the bow must be proven --
# A plain scene ticks only step 1; a remembered upright
# facing alone does not tick the bow step; a tilt does
# not prove a bow; a sway does not prove one; a spin
# does not prove one; a small bow does not prove one
# either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bow")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_bow negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_bow negative: an upright facing "
      "alone does not prove the bow")
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0.9, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bow negative: a tilt does not "
      "prove the bow")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((17, 0.8), (33, -0.8), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bow negative: a sway does not "
      "prove the bow")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bow negative: a spin does not "
      "prove the bow")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((24, 0.2), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bow negative: a small bow does "
      "not prove the bow")

# --- anim_nod negatives: the nod must be proven --
# A plain scene ticks only step 1; a remembered upright
# facing alone does not tick the nod step; a bow does
# not prove a nod; a tilt does not prove one; a sway
# does not prove one; a spin does not prove one; a
# small nod does not prove one; a single nod does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_nod negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_nod negative: an upright facing "
      "alone does not prove the nod")
main = bb._flow_main(ctx)
for f, x in ((24, 0.9), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a bow does not "
      "prove the nod")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0.5, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a tilt does not "
      "prove the nod")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((17, 0.8), (33, -0.8), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a sway does not "
      "prove the nod")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a spin does not "
      "prove the nod")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((13, 0.15), (24, 0.0), (37, 0.15), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a small nod does "
      "not prove the nod")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_nod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((24, 0.5), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_nod negative: a single nod does "
      "not prove the nod")

# --- anim_wag negatives: the wag must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the wag step;
# a spin does not prove a wag; a nod does not prove
# one; a sway does not prove one; a small wag does
# not prove one; a single swing does not prove one
# either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_wag")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_wag negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_wag negative: a starting facing "
      "alone does not prove the wag")
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_wag negative: a spin does not "
      "prove the wag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_wag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((13, 0.5), (24, 0.0), (37, 0.5), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_wag negative: a nod does not "
      "prove the wag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_wag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, x in ((17, 0.8), (33, -0.8), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (x, 0, 0)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_wag negative: a sway does not "
      "prove the wag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_wag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((13, 0.15), (25, -0.15), (37, 0.15), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_wag negative: a small wag does "
      "not prove the wag")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_wag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((24, 0.4), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_wag negative: a single swing does "
      "not prove the wag")

# --- anim_turn negatives: the turn must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the turn step;
# a spin does not prove a turn around; a wag does
# not prove one; a small turn does not prove one; a
# tilt does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_turn")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_turn negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_turn negative: a starting facing "
      "alone does not prove the turn")
main = bb._flow_main(ctx)
import math as _math
for f, z in ((24, _math.pi), (48, 2 * _math.pi)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_turn negative: a spin does not "
      "prove the turn")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_turn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, z in ((13, 0.4), (25, -0.4), (37, 0.4), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.rotation_euler = (0, 0, z)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_turn negative: a wag does not "
      "prove the turn")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_turn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0, 0, 0.4)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_turn negative: a small turn does "
      "not prove the turn")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_turn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (1.0, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_turn negative: a tilt does not "
      "prove the turn")

# --- anim_bob negatives: the bob must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the bob step;
# a single bounce does not prove a bob; a rise does
# not prove one; a small bob does not prove one; a
# slide does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bob")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_bob negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_bob negative: a starting place "
      "alone does not prove the bob")
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 2.5), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bob negative: a single bounce does "
      "not prove the bob")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bob")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0], base[1], base[2] + 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bob negative: a rise does not "
      "prove the bob")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bob")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((13, 0.3), (25, 0.0), (37, 0.3), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bob negative: a small bob does "
      "not prove the bob")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_bob")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_bob negative: a slide does not "
      "prove the bob")

# --- anim_float negatives: the float must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the float step; a
# hover does not prove a float; a bob does not prove
# one; a bounce does not prove one; a small lift does
# not prove one; a slide does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_float")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_float negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_float negative: a ground starting "
      "place alone does not prove the float")
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 3.0), (48, 3.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_float negative: a hover does "
      "not prove the float")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_float")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((13, 1.0), (25, 0.0), (37, 1.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_float negative: a bob does not "
      "prove the float")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_float")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 2.5), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_float negative: a bounce does "
      "not prove the float")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_float")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 0.4), (48, 0.4)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_float negative: a small lift does "
      "not prove the float")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_float")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_float negative: a slide does not "
      "prove the float")

# --- anim_dip negatives: the dip must be proven --
# A plain scene ticks only step 1; a remembered high
# starting place alone does not tick the dip step; a
# hover does not prove a dip; a land does not prove
# one; a bob does not prove one; a small dip does not
# prove one; a slide does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dip")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_dip negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_dip negative: a high starting "
      "place alone does not prove the dip")
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 0.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dip negative: a hover does "
      "not prove the dip")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, -1.5), (48, -1.5)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dip negative: a land does not "
      "prove the dip")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dip")
bpy.ops.buddy.tour_do(step=0)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (main.location[0], main.location[1], 0.0)
main.keyframe_insert(data_path="location", frame=1)
base = tuple(main.location)
for f, dz in ((13, 1.0), (25, 0.0), (37, 1.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dip negative: a bob does not "
      "prove the dip")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, -0.4), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dip negative: a small dip does "
      "not prove the dip")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dip negative: a slide does not "
      "prove the dip")

# --- anim_sidestep negatives: the sidestep must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the sidestep step; a
# slide does not prove a sidestep; a pace does not prove
# one; a small sidestep does not prove one; a diagonal
# move does not prove one; a hop does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sidestep")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_sidestep negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a ground starting "
      "place alone does not prove the sidestep")
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a slide does "
      "not prove the sidestep")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dy in ((24, 2.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1] + dy, base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a pace does not "
      "prove the sidestep")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dy in ((24, 0.5), (48, 0.5)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1] + dy, base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a small sidestep does "
      "not prove the sidestep")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 2.0, base[1] + 2.0, base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a diagonal move does not "
      "prove the sidestep")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dy, dz in ((24, 1.0, 1.5), (48, 2.0, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1] + dy, base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sidestep negative: a hop does not "
      "prove the sidestep")

# --- anim_backstep negatives: the step back must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the step-back step; a
# forward slide does not prove a step back; a sidestep does
# not prove one; a pace does not prove one; a small step
# back does not prove one; a diagonal step back does not
# prove one; a hop does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_backstep negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a ground starting "
      "place alone does not prove the step back")
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a forward slide does "
      "not prove the step back")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dy in ((24, 2.0), (48, 2.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1] + dy, base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a sidestep does not "
      "prove the step back")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, -2.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a pace does not "
      "prove the step back")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, -0.5), (48, -0.5)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a small step back does "
      "not prove the step back")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] - 2.0, base[1] + 2.0, base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a diagonal step back does not "
      "prove the step back")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, -1.0, 1.5), (48, -2.0, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backstep negative: a hop does not "
      "prove the step back")

# --- anim_forwardstep negatives: the step forward must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the step-forward step; a
# step back does not prove a step forward; a sidestep does
# not prove one; a pace does not prove one; a small step
# forward does not prove one; a diagonal step forward does
# not prove one; a hop does not prove one; a long slide
# forward does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_forwardstep negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a ground starting "
      "place alone does not prove the step forward")
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] - 2.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a step back does "
      "not prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dy in ((24, 2.0), (48, 2.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1] + dy, base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a sidestep does not "
      "prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, 2.0), (48, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a pace does not "
      "prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, 0.5), (48, 0.5)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a small step forward does "
      "not prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 2.0, base[1] + 2.0, base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a diagonal step forward does not "
      "prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 1.0, 1.5), (48, 2.0, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a hop does not "
      "prove the step forward")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_forwardstep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 3.0, base[1], base[2])
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_forwardstep negative: a long slide forward does not "
      "prove the step forward")

# --- anim_stepup negatives: the step up must be proven --
# A plain scene ticks only step 1; a remembered ground
# starting place alone does not tick the step-up step; a
# float does not prove a step up; a step forward does
# not prove one; a climb straight up does not prove one;
# a hop does not prove one; a small step up does not
# prove one; a diagonal sidestep-up does not prove one;
# a step down does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_stepup negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a ground starting "
      "place alone does not prove the step up")
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, 1.5), (48, 1.5)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a float does "
      "not prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, 2.0), (48, 2.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a step forward does not "
      "prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0], base[1], base[2] + 3.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a climb straight up does not "
      "prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 1.0, 1.0), (48, 1.0, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a hop does not "
      "prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 0.3, 0.3), (48, 0.3, 0.3)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a small step up does "
      "not prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 1.0, base[1] + 1.0, base[2] + 1.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a diagonal sidestep-up does not "
      "prove the step up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(1)
main.location = (base[0], base[1], base[2] + 1.0)
main.keyframe_insert(data_path="location", frame=1)
for f, dx in ((24, 1.0), (48, 1.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepup negative: a step down does not "
      "prove the step up")

# --- anim_stepdown negatives: the step down must be proven --
# A plain scene ticks only step 1; a remembered high
# starting place alone does not tick the step-down step; a
# step up does not prove a step down; a step forward does
# not prove one; a straight drop does not prove one;
# a hop does not prove one; a small step down does not
# prove one; a diagonal sidestep-down does not prove one;
# a climb does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_stepdown negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a high starting "
      "place alone does not prove the step down")
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 1.0, 1.0), (48, 1.0, 1.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a step up does "
      "not prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx in ((24, 2.0), (48, 2.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2])
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a step forward does not "
      "prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dz in ((24, -1.0), (48, -1.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0], base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a straight drop does not "
      "prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 1.0, -1.0), (48, 1.0, 0.0)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a hop does not "
      "prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
for f, dx, dz in ((24, 0.3, -0.3), (48, 0.3, -0.3)):
    ctx.scene.frame_set(f)
    main.location = (base[0] + dx, base[1], base[2] + dz)
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a small step down does "
      "not prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0] + 1.0, base[1] + 1.0, base[2] - 1.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a diagonal sidestep-down does not "
      "prove the step down")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_stepdown")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
base = tuple(main.location)
ctx.scene.frame_set(48)
main.location = (base[0], base[1], base[2] + 2.0)
main.keyframe_insert(data_path="location", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_stepdown negative: a climb does not "
      "prove the step down")

# --- anim_crouch negatives: the crouch must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the crouch step; a squash does
# not prove a crouch; a shrink does not prove one; a
# stretch does not prove one; a small crouch does not
# prove one; a crouch that recovers does not prove one
# either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_crouch")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_crouch negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a starting size "
      "alone does not prove the crouch")
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 1.5, 0.4)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a squash does "
      "not prove the crouch")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_crouch")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a shrink does not "
      "prove the crouch")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_crouch")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1, 1, 2.0)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a stretch does not "
      "prove the crouch")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_crouch")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 0.85)), (48, (1, 1, 0.85))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a small crouch does "
      "not prove the crouch")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_crouch")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 0.5)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_crouch negative: a crouch that recovers does not "
      "prove the crouch")

# --- anim_standup negatives: the stand-up must be proven --
# A plain scene ticks only step 1; a remembered crouched
# starting size alone does not tick the stand step; a
# crouch does not prove a stand-up; a squash does not
# prove one; a shrink does not prove one; a stretch does
# not prove one; a small stand does not prove one; a
# stand that crouches back does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_standup negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_standup negative: a crouched starting size "
      "alone does not prove the stand-up")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.scale = (1, 1, 1)
main.keyframe_insert(data_path="scale", frame=1)
for f, v in ((24, (1, 1, 0.5)), (48, (1, 1, 0.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a crouch does "
      "not prove the stand-up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.scale = (1, 1, 1)
main.keyframe_insert(data_path="scale", frame=1)
for f, v in ((24, (1.5, 1.5, 0.4)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a squash does not "
      "prove the stand-up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a shrink does not "
      "prove the stand-up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1, 1, 2.0)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a stretch does not "
      "prove the stand-up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.scale = (1, 1, 0.85)
main.keyframe_insert(data_path="scale", frame=1)
for f, v in ((24, (1, 1, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a small stand does "
      "not prove the stand-up")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_standup")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 1)), (48, (1, 1, 0.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_standup negative: a stand that crouches back does not "
      "prove the stand-up")

# --- anim_widen negatives: the widening must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the widen step; a grow does
# not prove a widening; a shrink does not prove one; a
# squash does not prove one; a small widen does not prove
# one; a widen that returns does not prove one; a stretch
# that raises the height does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_widen negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_widen negative: a starting size "
      "alone does not prove the widening")
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a grow does "
      "not prove the widening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a shrink does not "
      "prove the widening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.scale = (1, 1, 1)
main.keyframe_insert(data_path="scale", frame=1)
for f, v in ((24, (1.5, 1.5, 0.4)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a squash does not "
      "prove the widening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.3, 1.3, 1)), (48, (1.3, 1.3, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a small widen does not "
      "prove the widening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 2, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a widen that returns does not "
      "prove the widening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_widen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1, 1, 2.5)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_widen negative: a stretch does not "
      "prove the widening")

# --- anim_narrow negatives: the narrowing must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the narrow step; a shrink does
# not prove a narrowing; a grow does not prove one; a
# squash does not prove one; a small narrow does not prove
# one; a narrow that returns does not prove one; a stretch
# that raises the height does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_narrow negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a starting size "
      "alone does not prove the narrowing")
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a grow does "
      "not prove the narrowing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a shrink does not "
      "prove the narrowing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.scale = (1, 1, 1)
main.keyframe_insert(data_path="scale", frame=1)
for f, v in ((24, (1.5, 1.5, 0.4)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a squash does not "
      "prove the narrowing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.85, 0.85, 1)), (48, (0.85, 0.85, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a small narrow does not "
      "prove the narrowing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, 0.5, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a narrow that returns does not "
      "prove the narrowing")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_narrow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.scale = (1, 1, 2.5)
main.keyframe_insert(data_path="scale", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_narrow negative: a stretch does not "
      "prove the narrowing")

# --- anim_lengthen negatives: the lengthening must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the lengthen step; a widen does
# not prove a lengthening; a grow does not prove one; a
# shrink does not prove one; a stretch in height does not
# prove one; a small lengthen does not prove one; a
# lengthen that returns does not prove one; a width-only
# widen does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_lengthen negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a starting size "
      "alone does not prove the lengthening")
main = bb._flow_main(ctx)
for f, v in ((24, (2, 2, 1)), (48, (2, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a widen does "
      "not prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a grow does not "
      "prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a shrink does not "
      "prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 2)), (48, (1, 1, 2))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a stretch in height does not "
      "prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.3, 1, 1)), (48, (1.3, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a small lengthen does not "
      "prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 1, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a lengthen that returns does not "
      "prove the lengthening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lengthen")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 2, 1)), (48, (1, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lengthen negative: a width-only widen does not "
      "prove the lengthening")

# --- anim_shorten negatives: the shortening must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the shorten step; a widen does
# not prove a shortening; a grow does not prove one; a
# shrink does not prove one; a stretch in height does not
# prove one; a lengthen does not prove one; a small shorten
# does not prove one; a shorten that returns does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_shorten negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a starting size "
      "alone does not prove the shortening")
main = bb._flow_main(ctx)
for f, v in ((24, (1, 2, 1)), (48, (1, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a widen does "
      "not prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a grow does not "
      "prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a shrink does not "
      "prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 2)), (48, (1, 1, 2))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a stretch in height does not "
      "prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 1, 1)), (48, (2, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a lengthen does not "
      "prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.85, 1, 1)), (48, (0.85, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a small shorten does not "
      "prove the shortening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_shorten")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, 1, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_shorten negative: a shorten that returns does not "
      "prove the shortening")

# --- anim_thicken negatives: the thickening must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the thicken step; a widen does
# not prove a thickening; a grow does not prove one; a
# lengthen does not prove one; a stretch in height does not
# prove one; a shrink does not prove one; a small thicken
# does not prove one; a thicken that returns does not
# prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_thicken negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a starting size "
      "alone does not prove the thickening")
main = bb._flow_main(ctx)
for f, v in ((24, (2, 2, 1)), (48, (2, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a widen does "
      "not prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a grow does not "
      "prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 1, 1)), (48, (2, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a lengthen does not "
      "prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 2)), (48, (1, 1, 2))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a stretch in height does not "
      "prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a shrink does not "
      "prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1.3, 1)), (48, (1, 1.3, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a small thicken does not "
      "prove the thickening")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thicken")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 2, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thicken negative: a thicken that returns does not "
      "prove the thickening")

# --- anim_thin negatives: the thinning must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the thin step; a widen does
# not prove a thinning; a thicken does not prove one; a
# grow does not prove one; a shrink does not prove one; a
# lengthen does not prove one; a stretch in height does not
# prove one; a small thin does not prove one; a thin that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_thin negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_thin negative: a starting size "
      "alone does not prove the thinning")
main = bb._flow_main(ctx)
for f, v in ((24, (2, 2, 1)), (48, (2, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a widen does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 2, 1)), (48, (1, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a thicken does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a grow does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a shrink does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 1, 1)), (48, (2, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a lengthen does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 2)), (48, (1, 1, 2))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a stretch in height does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 0.85, 1)), (48, (1, 0.85, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a small thin does not "
      "prove the thinning")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_thin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 0.5, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_thin negative: a thin that returns does not "
      "prove the thinning")

# --- anim_taller negatives: the growing taller must be proven --
# A plain scene ticks only step 1; a remembered starting
# size alone does not tick the taller step; a widen does
# not prove a growing taller; a thicken does not prove one; a
# lengthen does not prove one; a grow does not prove one; a shrink does not prove one; a
# crouch does not prove one; a small taller does not
# prove one; a taller that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_taller negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_taller negative: a starting size "
      "alone does not prove the growing taller")
main = bb._flow_main(ctx)
for f, v in ((24, (2, 2, 1)), (48, (2, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a widen does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 2, 1)), (48, (1, 2, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a thicken does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2, 1, 1)), (48, (2, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a lengthen does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (2.5, 2.5, 2.5)), (48, (2.5, 2.5, 2.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a grow does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.4, 0.4, 0.4)), (48, (0.4, 0.4, 0.4))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a shrink does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 0.5)), (48, (1, 1, 0.5))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a crouch does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 1.3)), (48, (1, 1, 1.3))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a small taller does not "
      "prove the growing taller")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_taller")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1, 1, 2)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.scale = v
    main.keyframe_insert(data_path="scale", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_taller negative: a taller that returns does not "
      "prove the growing taller")

# --- anim_sideturn negatives: the turn to the side must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the turn step;
# a turn around does not prove a turn to the side; a spin does
# not prove one; a wag does not prove one; a small turn does not prove one; a
# tilt does not prove one; a turn that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_sideturn negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a starting facing "
      "alone does not prove the turn to the side")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a turn around does not "
      "prove the turn to the side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a spin does not "
      "prove the turn to the side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, 0.4)), (25, (0, 0, -0.4)), (37, (0, 0, 0.4)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a wag does not "
      "prove the turn to the side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, 0.4)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a small turn does not "
      "prove the turn to the side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a tilt does not "
      "prove the turn to the side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_sideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, _math.pi / 2)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_sideturn negative: a turn that returns does not "
      "prove the turn to the side")

# --- anim_leap negatives: the leap must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the leap step;
# a slide does not prove a leap; a bounce in place does
# not prove one; a small leap does not prove one; a
# leap that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_leap")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_leap negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_leap negative: a starting place "
      "alone does not prove the leap")
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 1.0)), (48, (3.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_leap negative: a slide does not "
      "prove the leap")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_leap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.0, 0, 3.5)), (48, (0.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_leap negative: a bounce in place does not "
      "prove the leap")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_leap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, 0, 1.4)), (48, (1.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_leap negative: a small leap does not "
      "prove the leap")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_leap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 3.0)), (48, (0.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_leap negative: a leap that returns does not "
      "prove the leap")

# --- anim_dive negatives: the dive must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the dive step;
# a leap does not prove a dive; a glide does not
# prove one; a descend in place does not prove one;
# a slide does not prove one; a small dive does not
# prove one; a dive that rises back does not prove
# one either. (The leap, glide and slide scenes set
# their own frame-1 place first, because each of
# those journeys starts somewhere other than up
# high where a dive starts.)
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_dive negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_dive negative: a starting place "
      "alone does not prove the dive")
main = bb._flow_main(ctx)
for f, v in ((1, (0.0, 0, 1.0)), (24, (1.5, 0, 3.0)), (48, (3.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a leap does not "
      "prove the dive")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((1, (0.0, 0, 4.0)), (24, (1.5, 0, 3.5)), (48, (3.0, 0, 3.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a glide does not "
      "prove the dive")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.0, 0, 2.0)), (48, (0.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a descend in place does not "
      "prove the dive")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((1, (0.0, 0, 1.0)), (24, (1.5, 0, 1.0)), (48, (3.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a slide does not "
      "prove the dive")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, 0, 2.8)), (48, (1.0, 0, 2.6))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a small dive does not "
      "prove the dive")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_dive")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 2.0)), (48, (3.0, 0, 3.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_dive negative: a dive that rises back does not "
      "prove the dive")

# --- anim_lookback negatives: the look behind must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the look step;
# a turn around does not prove a look behind; a spin does
# not prove one; a wag does not prove one; a small look does not prove one; a
# tilt does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lookback")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_lookback negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a starting facing "
      "alone does not prove the look behind")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a turn around does not "
      "prove the look behind")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a spin does not "
      "prove the look behind")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, 0.4)), (25, (0, 0, -0.4)), (37, (0, 0, 0.4)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a wag does not "
      "prove the look behind")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, 1.0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a small look does not "
      "prove the look behind")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_lookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_lookback negative: a tilt does not "
      "prove the look behind")

# --- anim_diagonal negatives: the diagonal must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the move step;
# a slide does not prove a diagonal; a forward-only
# move does not prove one; a leap does not prove one; a small diagonal does not prove one; a
# diagonal that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_diagonal")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_diagonal negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a starting place "
      "alone does not prove the diagonal")
main = bb._flow_main(ctx)
for f, v in ((24, (0, 1.5, 1)), (48, (0, 3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a slide does not "
      "prove the diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_diagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 1)), (48, (3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a forward-only move does not "
      "prove the diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_diagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 1.5, 3)), (48, (3, 3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a leap does not "
      "prove the diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_diagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, 0.5, 1)), (48, (1, 1, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a small diagonal does not "
      "prove the diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_diagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 1.5, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_diagonal negative: a diagonal that returns does not "
      "prove the diagonal")

# --- anim_backdiagonal negatives: the back diagonal must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the move step;
# a slide does not prove a back diagonal; a backward-only
# move does not prove one; a leap does not prove one; a small back-diagonal does not prove one; a
# back-diagonal that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backdiagonal")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_backdiagonal negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a starting place "
      "alone does not prove the back diagonal")
main = bb._flow_main(ctx)
for f, v in ((24, (0, 1.5, 1)), (48, (0, 3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a slide does not "
      "prove the back diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 0, 1)), (48, (-3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a backward-only move does not "
      "prove the back diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 1.5, 3)), (48, (-3, 3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a leap does not "
      "prove the back diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.5, 0.5, 1)), (48, (-1, 1, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a small back-diagonal does not "
      "prove the back diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 1.5, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backdiagonal negative: a back-diagonal that returns does not "
      "prove the back diagonal")

# --- anim_otherdiagonal negatives: the other diagonal must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the move step;
# a slide the other way does not prove an other diagonal; a forward-only
# move does not prove one; a leap does not prove one; a small other-diagonal does not prove one; an
# other-diagonal that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherdiagonal")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherdiagonal negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: a starting place "
      "alone does not prove the other diagonal")
main = bb._flow_main(ctx)
for f, v in ((24, (0, -1.5, 1)), (48, (0, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: a slide the other way does not "
      "prove the other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 1)), (48, (3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: a forward-only move does not "
      "prove the other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, -1.5, 3)), (48, (3, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: a leap does not "
      "prove the other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.5, -0.5, 1)), (48, (1, -1, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: a small other-diagonal does not "
      "prove the other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, -1.5, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherdiagonal negative: an other-diagonal that returns does not "
      "prove the other diagonal")

# --- anim_backotherdiagonal negatives: the back-other diagonal must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the move step;
# a slide the other way does not prove a back-other diagonal; a backward-only
# move does not prove one; a leap does not prove one; a small back-other-diagonal does not prove one; a
# back-other-diagonal that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backotherdiagonal")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_backotherdiagonal negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a starting place "
      "alone does not prove the back-other diagonal")
main = bb._flow_main(ctx)
for f, v in ((24, (0, -1.5, 1)), (48, (0, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a slide the other way does not "
      "prove the back-other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backotherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 0, 1)), (48, (-3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a backward-only move does not "
      "prove the back-other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backotherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, -1.5, 3)), (48, (-3, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a leap does not "
      "prove the back-other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backotherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.5, -0.5, 1)), (48, (-1, -1, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a small back-other-diagonal does not "
      "prove the back-other diagonal")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_backotherdiagonal")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, -1.5, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_backotherdiagonal negative: a back-other-diagonal that returns does not "
      "prove the back-other diagonal")

# --- anim_othersideturn negatives: the turn to the other side must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the turn step;
# a turn to the first side does not prove a turn to the other side; a turn around does
# not prove one; a spin does
# not prove one; a wag does not prove one; a small turn does not prove one; a
# tilt does not prove one; a turn that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_othersideturn negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a starting facing "
      "alone does not prove the turn to the other side")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi / 2)), (48, (0, 0, _math.pi / 2))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a turn to the first side does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -_math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a turn around does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a spin does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, -0.4)), (25, (0, 0, 0.4)), (37, (0, 0, -0.4)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a wag does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, -0.4)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a small turn does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a tilt does not "
      "prove the turn to the other side")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersideturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi / 2)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersideturn negative: a turn that returns does not "
      "prove the turn to the other side")

# --- anim_othersidestep negatives: the sidestep the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the move step;
# a sidestep the first way does not prove a sidestep the other way; a forward
# slide does not prove one; a small sidestep the other way does not prove one; a diagonal does not prove one; a
# hop does not prove one; a sidestep the other way that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_othersidestep negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a starting place "
      "alone does not prove the sidestep the other way")
main = bb._flow_main(ctx)
for f, v in ((24, (0, 1.5, 1)), (48, (0, 3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a sidestep the first way does not "
      "prove the sidestep the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 1)), (48, (3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a forward slide does not "
      "prove the sidestep the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, -0.5, 1)), (48, (0, -1, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a small sidestep the other way does not "
      "prove the sidestep the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, -1.5, 1)), (48, (3, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a diagonal does not "
      "prove the sidestep the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, -1.5, 3)), (48, (0, -3, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a hop does not "
      "prove the sidestep the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersidestep")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, -1.5, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersidestep negative: a sidestep the other way that returns does not "
      "prove the sidestep the other way")

# --- anim_otherspin negatives: the spin the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the spin step;
# a spin the first way does not prove a spin the other way; a turn around the other way does not prove one; a small turn does not prove one; a
# tilt does not prove one; a spin that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherspin")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherspin negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a starting facing "
      "alone does not prove the spin the other way")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a spin the first way does not "
      "prove the spin the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherspin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -_math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a turn around the other way does not "
      "prove the spin the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherspin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, -0.4)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a small turn does not "
      "prove the spin the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherspin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a tilt does not "
      "prove the spin the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherspin")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -2 * _math.pi)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherspin negative: a spin that returns does not "
      "prove the spin the other way")

# --- anim_otherturn negatives: the turn around the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the turn step;
# a turn around the first way does not prove a turn around the other way; a spin the other way does not prove one; a spin the first way does not prove one; a wag does not prove one; a small turn does not prove one; a
# tilt does not prove one; a turn that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherturn negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a starting facing "
      "alone does not prove the turn around the other way")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a turn around the first way does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a spin the other way does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a spin the first way does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, -0.4)), (25, (0, 0, 0.4)),
            (37, (0, 0, -0.4)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a wag does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, -0.4)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a small turn does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a tilt does not "
      "prove the turn around the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherturn")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherturn negative: a turn that returns does not "
      "prove the turn around the other way")
# --- anim_otherlookback negatives: the look behind the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the look step;
# a look behind the first way does not prove a look behind the other way; a turn around the other way does not prove one; a spin the other way does not prove one; a wag does not prove one; a small look the other way does not prove one; a
# tilt does not prove one; a look behind the other way that
# stays does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherlookback negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a starting facing "
      "alone does not prove the look behind the other way")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a look behind the first way does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -_math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a turn around the other way does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a spin the other way does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, -0.4)), (25, (0, 0, 0.4)),
            (37, (0, 0, -0.4)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a wag does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 0, -1.0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a small look the other way does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a tilt does not "
      "prove the look behind the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherlookback")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -_math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherlookback negative: a look behind the other way that stays does not "
      "prove the look behind the other way")
# --- anim_otherorbit negatives: the orbit the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the orbit step;
# a first-way orbit does not prove an orbit the other way; a quarter arc the other way does not prove one; a straight move does not prove one; an out-and-back does not prove one; a
# small circle the other way does not prove one; an ellipse-ish path the other way does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherorbit negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: a starting place "
      "alone does not prove the orbit the other way")
main = bb._flow_main(ctx)
for f, v in ((13, (0, 3, 1)), (25, (-3, 0, 1)),
            (37, (0, -3, 1)), (48, (3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: a first-way orbit does not "
      "prove the orbit the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, -3, 1)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: a quarter arc the other way does not "
      "prove the orbit the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (0, 0, 1)
main.keyframe_insert(data_path="location", frame=1)
for f, v in ((48, (6, 0, 1)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: a straight move does not "
      "prove the orbit the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (0, 0, 1)
main.keyframe_insert(data_path="location", frame=1)
for f, v in ((24, (3, 0, 1)), (48, (0, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: an out-and-back does not "
      "prove the orbit the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (1, 0, 1)
main.keyframe_insert(data_path="location", frame=1)
for f, v in ((13, (0, -1, 1)), (25, (-1, 0, 1)),
            (37, (0, 1, 1)), (48, (1, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: a small circle the other way does not "
      "prove the orbit the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherorbit")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, -1, 1)), (25, (-3, 0, 1)),
            (37, (0, 1, 1)), (48, (3, 0, 1))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherorbit negative: an ellipse-ish path the other way does not "
      "prove the orbit the other way")
# --- anim_otherroll negatives: the roll the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting place and facing alone does not tick the roll step;
# a first-way roll does not prove a roll the other way; a slide the other way does not prove one; a spin the other way does not prove one; a
# small roll the other way does not prove one; an out-of-pace roll the other way does not prove one; a roll the other way that comes back does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherroll negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a starting place and facing "
      "alone does not prove the roll the other way")
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (-2, 0, 1)
main.keyframe_insert(data_path="location", frame=1)
for f, v, r in ((48, (2, 0, 1), (0, -4, 0)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.rotation_euler = r
    main.keyframe_insert(data_path="location", frame=f)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a first-way roll does not "
      "prove the roll the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-2, 0, 1)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a slide the other way does not "
      "prove the roll the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, r in ((48, (0, 4, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = r
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a spin the other way does not "
      "prove the roll the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.location = (0.5, 0, 1)
main.keyframe_insert(data_path="location", frame=1)
for f, v, r in ((48, (-0.5, 0, 1), (0, 1, 0)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.rotation_euler = r
    main.keyframe_insert(data_path="location", frame=f)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a small roll the other way does not "
      "prove the roll the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v, r in ((48, (-2, 0, 1), (0, 0.5, 0)),):
    ctx.scene.frame_set(f)
    main.location = v
    main.rotation_euler = r
    main.keyframe_insert(data_path="location", frame=f)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: an out-of-pace roll the other way does not "
      "prove the roll the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherroll")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v, r in ((24, (-2, 0, 1), (0, 4, 0)),
                (48, (2, 0, 1), (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.rotation_euler = r
    main.keyframe_insert(data_path="location", frame=f)
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherroll negative: a roll the other way that comes back does not "
      "prove the roll the other way")
# --- anim_otherflip negatives: the flip the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the flip step;
# a first-way flip does not prove a flip the other way; a half flip the other way does not prove one; a small turn the other way does not prove one; a
# flip on another axis does not prove one; a tilt does not prove one; a flip the other way that
# returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherflip negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a starting facing "
      "alone does not prove the flip the other way")
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (_math.pi, 0, 0)), (48, (2 * _math.pi, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a first-way flip does not "
      "prove the flip the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-_math.pi, 0, 0)), (48, (-_math.pi, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a half flip the other way does not "
      "prove the flip the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-0.4, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a small turn the other way does not "
      "prove the flip the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, -_math.pi, 0)), (48, (0, -2 * _math.pi, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a flip on another axis does not "
      "prove the flip the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, 1.0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a tilt does not "
      "prove the flip the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherflip")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-2 * _math.pi, 0, 0)), (48, (0, 0, 0.0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherflip negative: a flip the other way that returns does not "
      "prove the flip the other way")
# --- anim_othertilt negatives: the tilt the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the tilt step;
# a first-way tilt does not prove a tilt the other way; a small lean the other way does not prove one; an over-lean the other way does not prove one; a
# rock the other way that settles does not prove one; a spin does not prove one; a lean on the Y axis does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_othertilt negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a starting facing "
      "alone does not prove the tilt the other way")
main = bb._flow_main(ctx)
for f, v in ((48, (1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a first-way tilt does not "
      "prove the tilt the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-0.25, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a small lean the other way does not "
      "prove the tilt the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-2.6, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: an over-lean the other way does not "
      "prove the tilt the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.5, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a rock the other way that settles does not "
      "prove the tilt the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a spin does not "
      "prove the tilt the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othertilt")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (0, -1.0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othertilt negative: a lean on the Y axis does not "
      "prove the tilt the other way")
# --- anim_otherbow negatives: the bow the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the bow step;
# a first-way bow does not prove a bow the other way; a tilt the other way does not prove one; a sway does not prove one; a spin does not prove one; a small bow the other way does not prove one; a nod the other way does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherbow negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a starting facing "
      "alone does not prove the bow the other way")
main = bb._flow_main(ctx)
for f, v in ((24, (0.9, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a first-way bow does not "
      "prove the bow the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a tilt the other way does not "
      "prove the bow the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((17, (0.8, 0, 0)), (33, (-0.8, 0, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a sway does not "
      "prove the bow the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a spin does not "
      "prove the bow the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.2, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a small bow the other way does not "
      "prove the bow the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherbow")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (-0.5, 0, 0)), (24, (0, 0, 0)),
             (37, (-0.5, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherbow negative: a nod the other way does not "
      "prove the bow the other way")
# --- anim_othernod negatives: the nod the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the nod step;
# a first-way nod does not prove a nod the other way; a bow the other way does not prove one; a tilt the other way does not prove one; a sway does not prove one; a spin does not prove one; a small nod the other way does not prove one; a single nod the other way does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_othernod negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a starting facing "
      "alone does not prove the nod the other way")
main = bb._flow_main(ctx)
for f, v in ((13, (0.5, 0, 0)), (24, (0, 0, 0)),
             (37, (0.5, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a first-way nod does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.9, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a bow the other way does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((48, (-1.0, 0, 0)),):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a tilt the other way does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((17, (0.8, 0, 0)), (33, (-0.8, 0, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a sway does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, -_math.pi)), (48, (0, 0, -2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a spin does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (-0.15, 0, 0)), (24, (0, 0, 0)),
             (37, (-0.15, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a small nod the other way does not "
      "prove the nod the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othernod")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.5, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othernod negative: a single nod the other way does not "
      "prove the nod the other way")
# --- anim_otherwag negatives: the wag the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the wag step;
# a first-way wag does not prove a wag the other way; a spin does not prove one; a nod does not prove one; a sway does not prove one; a small wag the other way does not prove one; a single swing the other way does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherwag negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a starting facing "
      "alone does not prove the wag the other way")
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, 0.4)), (25, (0, 0, -0.4)),
             (37, (0, 0, 0.4)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a first-way wag does not "
      "prove the wag the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a spin does not "
      "prove the wag the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0.5, 0, 0)), (24, (0, 0, 0)),
             (37, (0.5, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a nod does not "
      "prove the wag the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((17, (0, 0.8, 0)), (33, (0, -0.8, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a sway does not "
      "prove the wag the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((13, (0, 0, -0.15)), (25, (0, 0, 0.15)),
             (37, (0, 0, -0.15)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a small wag the other way does not "
      "prove the wag the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherwag")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0, 0, -0.4)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherwag negative: a single swing the other way does not "
      "prove the wag the other way")
# --- anim_othersway negatives: the sway the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting facing alone does not tick the sway step;
# a first-way sway does not prove a sway the other way; a tilt does not prove one; a spin does not prove one; a small sway the other way does not prove one; a one-way rock the other way does not prove one; a bow does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_othersway negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a starting facing "
      "alone does not prove the sway the other way")
main = bb._flow_main(ctx)
for f, v in ((17, (0.8, 0, 0)), (33, (-0.8, 0, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a first-way sway does not "
      "prove the sway the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (-0.8, 0, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a tilt does not "
      "prove the sway the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
import math as _math
for f, v in ((24, (0, 0, _math.pi)), (48, (0, 0, 2 * _math.pi))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a spin does not "
      "prove the sway the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((17, (-0.2, 0, 0)), (33, (0.2, 0, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a small sway the other way does not "
      "prove the sway the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.8, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a one-way rock the other way does not "
      "prove the sway the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_othersway")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.9, 0, 0)), (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_othersway negative: a bow does not "
      "prove the sway the other way")
# --- anim_otherswing negatives: the swing the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting lean the other way alone does not tick the swing step;
# a first-way swing does not prove a swing the other way; a tip that never crosses the middle does not prove one; a small swing the other way does not prove one; a one-way move does not prove one; a swing starting upright does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherswing")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherswing negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a starting lean "
      "the other way alone does not prove the swing the other way")
main = bb._flow_main(ctx)
for f, v in ((24, (0, 1.4, 0)), (48, (0, 0.7, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a tip that never crosses "
      "the middle does not prove the swing the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherswing")
bpy.ops.buddy.tour_do(step=0)
main = bb._flow_main(ctx)
for f, v in ((1, (0, -0.7, 0)), (24, (0, 0.7, 0)),
             (48, (0, -0.7, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a first-way swing does not "
      "prove the swing the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherswing")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(1)
main.rotation_euler = (0, 0.2, 0)
main.keyframe_insert(data_path="rotation_euler", frame=1)
for f, v in ((24, (0, -0.2, 0)), (48, (0, 0.2, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a small swing the other way does not "
      "prove the swing the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherswing")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
ctx.scene.frame_set(48)
main.rotation_euler = (0, -0.7, 0)
main.keyframe_insert(data_path="rotation_euler", frame=48)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a one-way move does not "
      "prove the swing the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherswing")
bpy.ops.buddy.tour_do(step=0)
main = bb._flow_main(ctx)
for f, v in ((1, (0, 0, 0)), (24, (0, -0.7, 0)),
             (48, (0, 0, 0))):
    ctx.scene.frame_set(f)
    main.rotation_euler = v
    main.keyframe_insert(data_path="rotation_euler", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherswing negative: a swing starting upright does not "
      "prove the swing the other way")
# --- anim_otherleap negatives: the leap the other way must be proven --
# A plain scene ticks only step 1; a remembered
# starting place alone does not tick the leap step;
# a first-way leap does not prove a leap the other way; a slide the other way does not prove one; a bounce in place does
# not prove one; a small leap the other way does not prove one; a
# leap the other way that returns does not prove one either.
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherleap")
bpy.ops.buddy.tour_do(step=0)
checks, _current = bb.tour_state(ctx)
assert checks[0] and not any(checks[1:]), checks
print("FLOWS_PASS anim_otherleap negative: a plain scene ticks "
      "only step 1")
bpy.ops.buddy.tour_do(step=1)
checks, _current = bb.tour_state(ctx)
assert checks[1] and not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a starting place "
      "alone does not prove the leap the other way")
main = bb._flow_main(ctx)
for f, v in ((24, (1.5, 0, 3.0)), (48, (3.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a first-way leap does not "
      "prove the leap the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherleap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 0, 1.0)), (48, (-3.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a slide the other way does not "
      "prove the leap the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherleap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (0.0, 0, 3.5)), (48, (0.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a bounce in place does not "
      "prove the leap the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherleap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-0.5, 0, 1.4)), (48, (-1.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a small leap the other way does not "
      "prove the leap the other way")
bpy.ops.wm.read_factory_settings(use_empty=False)
ctx = bpy.context
bpy.ops.buddy.tour_start(package="anim_otherleap")
bpy.ops.buddy.tour_do(step=0)
bpy.ops.buddy.tour_do(step=1)
main = bb._flow_main(ctx)
for f, v in ((24, (-1.5, 0, 3.0)), (48, (0.0, 0, 1.0))):
    ctx.scene.frame_set(f)
    main.location = v
    main.keyframe_insert(data_path="location", frame=f)
checks, _current = bb.tour_state(ctx)
assert not checks[2], checks
print("FLOWS_PASS anim_otherleap negative: a leap the other way that returns does not "
      "prove the leap the other way")
bb.unregister()
print("ALL FLOWS TESTS PASSED")
