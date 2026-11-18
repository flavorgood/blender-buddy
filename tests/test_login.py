"""Blender Buddy login-routes proof (v0.7).

Run with:
  blender -b --factory-startup --python tests/test_login.py

The question this answers: "can I just log in with ChatGPT?" There
is no login button an add-on may offer - but OpenAI's own Codex
program IS signed in with the user's ChatGPT account, and Anthropic
forbids the equivalent for Claude. So Buddy offers: key, ChatGPT
login THROUGH the Codex program, or a local AI with no key at all.

No real program and no real service is called here: the CLI runner
and the network function are stubbed. The test proves the routing -
readiness per route, Codex present -> questions and plans flow
through it and never through the network function, Codex missing ->
a plain setup message, local AI -> works with an empty key.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context
wm = ctx.window_manager

# A real child reads a long Unicode prompt exactly as Codex reads stdin.
# Passing this as a Windows positional argument cannot start the child.
python = Path(sys.executable)
if not python.stem.lower().startswith("python"):
    name = "python.exe" if os.name == "nt" else f"python{sys.version_info.major}.{sys.version_info.minor}"
    python = Path(sys.prefix) / "bin" / name
prompt = "Unicode: café \U0001f9f0\n" * 4000
read_digest = ("import sys, hashlib; data = sys.stdin.buffer.read().replace(b'\\r\\n', b'\\n'); "
               "print(hashlib.sha256(data).hexdigest())")
assert bb._run_cli([str(python), "-c", read_digest], input_text=prompt).strip() == (
    hashlib.sha256(prompt.encode("utf-8")).hexdigest())
print("LOGIN_PASS full UTF-8 plan transported through stdin to a local child")

# --- readiness per route -----------------------------------------------------
assert bb._expert_ready({"service": "KEY", "key": "", "url": "https://x"}) is False
assert bb._expert_ready({"service": "KEY", "key": "k", "url": "https://x"}) is True
assert bb._expert_ready({"service": "KEY", "key": "",
                         "url": "http://localhost:1234/v1"}) is True
assert bb._expert_ready({"service": "LOCAL", "key": "", "url": ""}) is False
real_local_alive = bb._local_alive
bb._local_alive = lambda url: False
assert bb._expert_ready({"service": "LOCAL", "key": "",
                         "url": "http://localhost:11434/v1"}) is False
bb._local_alive = lambda url: True
assert bb._expert_ready({"service": "LOCAL", "key": "",
                         "url": "http://localhost:11434/v1"}) is True
print("LOGIN_PASS readiness: key route needs a key, local route needs "
      "a local AI that actually answers (the probe is stubbed in this "
      "suite; its real proof is the live failure drill)")

real_which = bb.shutil.which
bb.shutil.which = lambda name: "/usr/bin/codex" if name == "codex" else None
assert bb._expert_ready({"service": "CODEX", "key": "", "url": ""}) is True
bb.shutil.which = lambda name: None
missing_cli = patch.object(bb.os.path, "isfile", return_value=False)
missing_cli.start()
assert bb._expert_ready({"service": "CODEX", "key": "", "url": ""}) is False
print("LOGIN_PASS readiness: ChatGPT route needs the Codex program present")

# --- Codex missing: plain setup message, nothing runs -------------------------
bb._expert_settings = lambda: {"key": "", "url": "", "model": "",
                               "float": True, "service": "CODEX"}
cli_calls = []
bb._run_cli = lambda argv, timeout=120: cli_calls.append(argv) or ""
wm.buddy_ask = "make a box"
bpy.ops.buddy.ask_expert()
assert "couldn't locate the Codex command-line program" in wm.buddy_answer, wm.buddy_answer
assert cli_calls == []
print("LOGIN_PASS Codex missing -> plain setup message, no call")

# --- Codex present: the agent plan flows through the program ------------------
missing_cli.stop()
bb.shutil.which = lambda name: "/usr/bin/codex" if name == "codex" else None


def fake_cli(argv, timeout=120, include_stderr=False, *, input_text=None):
    cli_calls.append(argv)
    assert argv[0].endswith("codex")
    if argv[1:] == ["login", "status"]:
        assert include_stderr and input_text is None
        return "Logged in"
    assert argv[1] == "exec" and argv[-1] == "-"
    assert "read-only" in argv, "the expert must not write files via Codex"
    assert "make a box" in input_text and input_text not in argv
    with open(argv[argv.index("--output-last-message") + 1], "w", encoding="utf-8") as result:
        result.write("SUMMARY: Make a ball.\nSTEP: button:add_ball")
    return "Progress on stdout; only the final file is the plan."


bb._run_cli = fake_cli


def no_http(url, key, payload):
    raise AssertionError("the ChatGPT route must not use the key/network path")


bb._expert_http = no_http
wm.buddy_agent = True
bpy.ops.buddy.ask_expert()
plan = json.loads(wm.buddy_plan or "[]")
assert plan == [{"kind": "button", "id": "add_ball"}], plan
bpy.ops.buddy.run_plan()
assert "Sphere" in bpy.data.objects
assert wm.buddy_plan_report.startswith("Done - all 1 steps ran")
print("LOGIN_PASS ChatGPT route: plan made through Codex and ran")

# --- local AI: empty key still asks and answers --------------------------------
bb._expert_settings = lambda: {"key": "",
                               "url": "http://localhost:11434/v1/chat/completions",
                               "model": "llama3.1", "float": True,
                               "service": "LOCAL"}
bb._expert_http = lambda url, key, payload: {"choices": [{"message": {
    "content": "Pick the shape first, then round the edge.\n"
               "BUTTON: round_edge"}}]}
wm.buddy_agent = False
wm.buddy_ask = "how do I round an edge?"
bpy.ops.buddy.ask_expert()
assert wm.buddy_answer.startswith("Pick the shape"), wm.buddy_answer
assert wm.buddy_suggested == "round_edge"
wm.buddy_agent = True
print("LOGIN_PASS local AI answers with no key at all")

# --- Claude key: Anthropic's shape, translated --------------------------------
assert bb._expert_ready({"service": "CLAUDE", "key": "", "url": bb._CLAUDE_URL}) is False
assert bb._expert_ready({"service": "CLAUDE", "key": "sk-ant-x",
                         "url": bb._CLAUDE_URL}) is True
bb._expert_settings = lambda: {"key": "", "url": bb._CLAUDE_URL,
                               "model": bb._CLAUDE_MODEL, "float": True,
                               "service": "CLAUDE"}
wm.buddy_agent = True
wm.buddy_ask = "make a ball"
bpy.ops.buddy.ask_expert()
assert "no Claude key is pasted yet" in wm.buddy_answer, wm.buddy_answer
print("LOGIN_PASS Claude with no key -> its own plain setup message")

claude_seen = {}


def fake_claude_http(url, key, payload):
    claude_seen.update(url=url, key=key, payload=payload)
    return {"content": [
        {"type": "thinking", "thinking": "ignored"},
        {"type": "text", "text": "SUMMARY: Make a ball, Claude style.\n"
                                  "STEP: button:add_ball"}]}


bb._expert_http_claude = fake_claude_http
bb._expert_http = no_http
bb._expert_settings = lambda: {"key": "sk-ant-x", "url": bb._CLAUDE_URL,
                               "model": bb._CLAUDE_MODEL, "float": True,
                               "service": "CLAUDE"}
before = len(bpy.data.objects)
bpy.ops.buddy.ask_expert()
assert claude_seen["url"] == bb._CLAUDE_URL
assert claude_seen["key"] == "sk-ant-x"
payload = claude_seen["payload"]
assert payload["model"] == bb._CLAUDE_MODEL
assert payload["max_tokens"] == 1024
assert "Buddy Expert" in payload["system"], "system goes in its own field"
assert payload["messages"][0]["role"] == "user"
assert "make a ball" in payload["messages"][0]["content"]
plan = json.loads(wm.buddy_plan or "[]")
assert plan == [{"kind": "button", "id": "add_ball"}], plan
bpy.ops.buddy.run_plan()
assert len(bpy.data.objects) == before + 1
assert wm.buddy_plan_report.startswith("Done - all 1 steps ran")
print("LOGIN_PASS Claude key: Anthropic shape sent, text read back, plan ran")

bb.shutil.which = real_which
bb._local_alive = real_local_alive
bb.unregister()
print("ALL LOGIN TESTS PASSED")
