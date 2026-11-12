"""Blender Buddy agent-mode proof (v0.6).

Run with:
  blender -b --factory-startup --python tests/test_agent.py

No real AI service is called: the expert's network function is swapped
for a stub. The test proves that a plain-words goal can become a
checked plan, that the plan actually runs buttons and Blender tools,
that exact settings and node-tree styles land and read back, that an
add-on search can be opened, that invented or malformed steps are
dropped, and that a failed step produces one revised plan which is
shown rather than silently run.
"""
import json
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context
wm = ctx.window_manager

assert hasattr(bpy.ops.buddy, "run_plan")
assert hasattr(bpy.ops.buddy, "clear_plan")
assert wm.buddy_agent is True
print("AGENT_PASS operators present, agent mode on by default")

bb._expert_settings = lambda: {"key": "test-key", "url": "http://stub",
                               "model": "stub-model", "float": True}

next_reply = ""
calls = []
opened_urls = []


def reply(text):
    return {"choices": [{"message": {"content": text}}]}


def fake_http(url, key, payload):
    calls.append(payload)
    user = payload["messages"][1]["content"]
    if "Your previous plan stopped" in user:
        return reply("SUMMARY: Add the ball another way.\n"
                     "STEP: button:add_ball")
    return reply(next_reply)


bb._expert_http = fake_http
bb._open_url = lambda url: opened_urls.append(url) or {"FINISHED"}


def clear_objects():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.buddy.clear_plan()


def ask(question, text):
    global next_reply
    next_reply = text
    wm.buddy_ask = question
    bpy.ops.buddy.ask_expert()
    return json.loads(wm.buddy_plan or "[]")


# --- parser: only real, well-formed steps survive --------------------------
summary, steps, dropped = bb._parse_plan(
    "SUMMARY: Test the gate.\n"
    "STEP: button:add_cube\n"
    "STEP: set:brush.size:120\n"
    "STEP: set:brush.size:banana\n"
    "STEP: set:brush.falloff:FEATHER\n"
    "STEP: set:volume.up:3\n"
    "STEP: style:plasma\n")
assert summary == "Test the gate."
assert steps == [{"kind": "button", "id": "add_cube"},
                 {"kind": "set", "id": "brush.size", "value": 120}], steps
assert dropped == 4, dropped
assert bb._step_label(steps[1]) == "Set sculpt brush size to 120"
print("AGENT_PASS parser keeps real steps and drops invented ones")

# --- a normal plan runs buttons and a raw Blender tool ----------------------
clear_objects()
plan = ask(
    "make a red box",
    "SUMMARY: Make a red box.\n"
    "STEP: button:add_cube\n"
    "STEP: tool:object.select_all\n"
    "STEP: button:not_a_button\n"
    "STEP: tool:fake.tool\n"
    "STEP: button:give_colour")
assert [s["id"] for s in plan] == ["add_cube", "object.select_all",
                                   "give_colour"], plan
assert "Plan ready: 3 steps" in wm.buddy_plan_report
assert "2 steps" in wm.buddy_plan_report and "left out" in wm.buddy_plan_report
bpy.ops.buddy.run_plan()
cube = bpy.context.object
assert cube and cube.type == "MESH"
assert cube.data.materials[0].name == "Buddy Red"
assert wm.buddy_plan == ""
assert wm.buddy_plan_report.startswith("Done - all 3 steps ran")
print("AGENT_PASS plan ran buttons and a raw Blender tool")

# --- settings and a node-tree style land exactly ----------------------------
clear_objects()
bpy.ops.buddy.action(action_id="add_cube")
cube = bpy.context.object
ctx.scene.render.engine = "CYCLES"
plan = ask(
    "give it rounded edges, a soft exact sculpt brush, better samples, "
    "and a wood style",
    "SUMMARY: Set the edges, brush, picture quality, and wood style.\n"
    "STEP: button:round_all_edges\n"
    "STEP: set:bevel.width:0.08\n"
    "STEP: set:bevel.segments:4\n"
    "STEP: set:render.samples:64\n"
    "STEP: set:brush.size:120\n"
    "STEP: set:brush.strength:0.5\n"
    "STEP: set:brush.falloff:SPHERE\n"
    "STEP: style:wood")
assert len(plan) == 8, plan
bpy.ops.buddy.run_plan()
bevel = next(m for m in cube.modifiers if m.type == "BEVEL")
assert abs(bevel.width - 0.08) < 1e-6, bevel.width
assert bevel.segments == 4
assert ctx.scene.cycles.samples == 64
brush = ctx.tool_settings.sculpt.brush
assert brush, "the setting must land on the current sculpt brush"
assert brush.size == 120 and abs(brush.strength - 0.5) < 1e-6
assert brush.curve_preset == "SPHERE"
mat = cube.data.materials[0]
node_types = {n.type for n in mat.node_tree.nodes}
assert {"TEX_NOISE", "VALTORGB", "BUMP"} <= node_types, node_types
assert wm.buddy_plan_report.startswith("Done - all 8 steps ran")
print("AGENT_PASS exact settings read back and wood node tree built")

# --- find is a real step: it opens the add-on search ------------------------
plan = ask(
    "find me something for brick walls",
    "SUMMARY: Look for a brick-wall add-on.\n"
    "STEP: find:brick wall generator")
assert plan == [{"kind": "find", "id": "brick wall generator"}], plan
bpy.ops.buddy.run_plan()
assert opened_urls and "extensions.blender.org/search/" in opened_urls[-1]
assert "brick%20wall%20generator" in opened_urls[-1]
assert "add-on search" in wm.buddy_plan_report
print("AGENT_PASS find step opened the add-on search")

# --- a failed step replans once, and the new plan is not auto-run -----------
clear_objects()
plan = ask(
    "make a box and bevel it",
    "SUMMARY: Make a box, then try a tool in the wrong mode.\n"
    "STEP: button:add_cube\n"
    "STEP: tool:mesh.bevel")
assert len(plan) == 2
result = bpy.ops.buddy.run_plan()
assert "CANCELLED" in result, result
assert "replanned" in wm.buddy_plan_report, wm.buddy_plan_report
plan = json.loads(wm.buddy_plan or "[]")
assert plan == [{"kind": "button", "id": "add_ball"}], plan
assert "Sphere" not in bpy.data.objects, "revised plan must wait for Run"
bpy.ops.buddy.run_plan()
assert "Sphere" in bpy.data.objects
assert wm.buddy_plan_report.startswith("Done - all 1 steps ran")
print("AGENT_PASS failure replanned once and waited for the user")

# --- advice mode still works when agent mode is off --------------------------
wm.buddy_agent = False
wm.buddy_ask = "how do I round an edge?"
next_reply = ("Round the edge after you pick the shape.\n"
              "BUTTON: round_edge")
bpy.ops.buddy.ask_expert()
assert wm.buddy_answer.startswith("Round the edge")
assert wm.buddy_suggested == "round_edge"
assert wm.buddy_plan == ""
wm.buddy_agent = True
print("AGENT_PASS advice mode still works with agent mode off")

bb.unregister()
print("ALL AGENT TESTS PASSED")
