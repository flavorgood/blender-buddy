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
                                    "anim_pulse"}, [p["id"] for p in bb.PACKAGES]
for pkg in flows:
    for step in pkg["steps"]:
        assert "tools" in step, (pkg["id"], step["title"])
        for tid in step["tools"]:
            assert tid in bb.ACTIONS_BY_ID, (pkg["id"], tid)
print("FLOWS_PASS twenty-one flows registered; every step's "
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

bb.unregister()
print("ALL FLOWS TESTS PASSED")
