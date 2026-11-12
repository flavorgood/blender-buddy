"""Blender Buddy AI Expert proof (v0.5).

Run with:
  blender -b --factory-startup --python tests/test_expert.py

No real AI service is called (and no real key exists here): the
expert's network function is swapped for a stub, and the test proves
the full plumbing - question + scene summary go out, the plain-words
answer comes back into the panel, a suggested button is recognised
only when it's a real Buddy button, the floating tip is set, and
failures land as plain explanations instead of crashes.
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context
wm = ctx.window_manager

assert hasattr(bpy.ops.buddy, "ask_expert")
assert hasattr(bpy.ops.buddy, "open_prefs")
assert bb._EXPERT_HANDLE is not None, "floating overlay handler not registered"
print("EXPERT_PASS operators + floating overlay registered")

# --- no key yet: a plain setup message, and no call is made --------------
called = []
bb._expert_http = lambda url, key, payload: called.append(payload) or {}
bb._expert_settings = lambda: {"key": "", "url": "http://stub",
                               "model": "stub", "float": True}
wm.buddy_ask = "how do I round an edge?"
bpy.ops.buddy.ask_expert()
assert "isn't set up yet" in wm.buddy_answer, wm.buddy_answer
assert called == [], "no key must mean no call"
print("EXPERT_PASS no key -> setup message, nothing sent")

# --- happy path: answer stored, button suggested, tip floats -------------
seen = {}

def fake_http(url, key, payload):
    seen["url"] = url
    seen["key"] = key
    seen["payload"] = payload
    return {"choices": [{"message": {"content":
            "Pick the shape, then round its edge - that softens the corner.\n"
            "BUTTON: round_edge"}}]}

bb._expert_http = fake_http
bb._expert_settings = lambda: {"key": "test-key", "url": "http://stub",
                               "model": "stub-model", "float": True}
bpy.ops.buddy.ask_expert()
assert wm.buddy_answer.startswith("Pick the shape"), wm.buddy_answer
assert "BUTTON" not in wm.buddy_answer
assert wm.buddy_suggested == "round_edge", wm.buddy_suggested
assert bb._EXPERT_TIP.startswith("Pick the shape"), bb._EXPERT_TIP
msgs = seen["payload"]["messages"]
assert seen["key"] == "test-key" and seen["payload"]["model"] == "stub-model"
assert "Cube" in msgs[1]["content"], msgs[1]["content"]
assert "round_edge = Round off a sharp edge" in msgs[0]["content"]
print("EXPERT_PASS question+scene out, answer+button+tip back")

# --- an invented button name is not trusted -------------------------------
bb._expert_http = lambda url, key, payload: {"choices": [{"message": {
    "content": "Just press the magic button.\nBUTTON: magic_button"}}]}
bpy.ops.buddy.ask_expert()
assert wm.buddy_suggested == "", wm.buddy_suggested
assert wm.buddy_answer == "Just press the magic button."
print("EXPERT_PASS invented button names are dropped")

# --- a dead service becomes a plain explanation ---------------------------
def dead_http(url, key, payload):
    raise RuntimeError("boom")

bb._expert_http = dead_http
bpy.ops.buddy.ask_expert()
assert "didn't answer" in wm.buddy_answer, wm.buddy_answer
print("EXPERT_PASS failure lands as plain words, not a crash")

bb.unregister()
assert bb._EXPERT_HANDLE is None
print("ALL EXPERT TESTS PASSED")
