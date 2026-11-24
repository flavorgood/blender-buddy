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
                                    "sculpt_symmetry"}, [p["id"] for p in bb.PACKAGES]
for pkg in flows:
    for step in pkg["steps"]:
        assert "tools" in step, (pkg["id"], step["title"])
        for tid in step["tools"]:
            assert tid in bb.ACTIONS_BY_ID, (pkg["id"], tid)
print("FLOWS_PASS five flows registered; every step's "
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

bb.unregister()
print("ALL FLOWS TESTS PASSED")
