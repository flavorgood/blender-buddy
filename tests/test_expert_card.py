"""Blender Buddy floating Expert card proof (fix round 11).

Run with:
  blender -b --factory-startup --python tests/test_expert_card.py

The card's geometry, hit testing, wrap/scroll math and content
sync are pure or property-driven, so they are proven headless
here. The card ask path is exercised for real: a capability
question typed into the card's buffer must be answered locally
("what can you do") with no connection, exactly as in the panel.
The GUI behaviour (dragging, typing, the chip) is proven on the
rig - see redesign/FIX11_LOG.md.
"""
import json
import os
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
ctx = bpy.context
wm = ctx.window_manager

# --- registered: handler, operators, preference defaults ---------
assert bb._EXPERT_HANDLE is not None, "card draw handler not registered"
assert hasattr(bpy.ops.buddy, "expert_card_open")
assert hasattr(bpy.ops.buddy, "expert_card_modal")
ann = bb.BUDDY_Preferences.__annotations__
assert ann["expert_float"].keywords["default"] is True
assert ann["expert_card_x"].keywords["default"] == -1
assert ann["expert_card_y"].keywords["default"] == -1
assert ann["expert_card_w"].keywords["default"] == 440
assert ann["expert_card_h"].keywords["default"] == 360
assert ann["expert_card_min"].keywords["default"] is False
print("CARD_PASS handler + operators registered, prefs default on")

# --- geometry: clamping to the region -----------------------------
# Unset position lands at the proven spot: x=72, top margin 96.
assert bb._card_clamp_geo(1600, 1000, (-1, -1, 440, 360)) == \
    (72, 1000 - 360 - 96, 440, 360)
# Oversize shrinks to the region; undersize grows to the minimums.
assert bb._card_clamp_geo(800, 600, (0, 0, 5000, 4000)) == \
    (0, 0, 800, 600)
assert bb._card_clamp_geo(1600, 1000, (0, 0, 10, 10)) == \
    (0, 0, bb._CARD_MIN_W, bb._CARD_MIN_H)
# A stored position outside the region is pulled back inside.
x, y, w, h = bb._card_clamp_geo(1600, 1000, (1500, 950, 440, 360))
assert x + w <= 1600 and y + h <= 1000 and x >= 0 and y >= 0
print("CARD_PASS geometry clamps to region, min sizes held")

# --- layout + hit tests -------------------------------------------
geo = (100, 100, 440, 360)
lay = bb._card_layout(geo)
assert lay["footer_kind"] is None
centre = lambda r: ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)  # noqa: E731
assert bb._card_hit(lay, *centre(lay["title"])) == "title"
assert bb._card_hit(lay, *centre(lay["btn_close"])) == "btn_close"
assert bb._card_hit(lay, *centre(lay["btn_min"])) == "btn_min"
assert bb._card_hit(lay, *centre(lay["field"])) == "field"
assert bb._card_hit(lay, *centre(lay["btn_ask"])) == "btn_ask"
assert bb._card_hit(lay, *centre(lay["body"])) == "body"
assert bb._card_hit(lay, *centre(lay["grip"])) == "grip"
# The status strip is card, but not a button.
assert bb._card_hit(lay, *centre(lay["status"])) == "card"
assert bb._card_hit(lay, 5, 5) is None
assert bb._card_hit(lay, 2000, 2000) is None
print("CARD_PASS hit tests: title/buttons/field/body/grip")

lay = bb._card_layout(geo, footer="plan")
assert bb._card_hit(lay, *centre(lay["btn_run"])) == "btn_run"
assert bb._card_hit(lay, *centre(lay["btn_clear"])) == "btn_clear"
lay = bb._card_layout(geo, footer="do")
assert bb._card_hit(lay, *centre(lay["btn_do"])) == "btn_do"
# In the plan footer there is no do-button: its would-be spot
# (same rect the do layout uses) belongs to the plan's buttons.
lay = bb._card_layout(geo, footer="plan")
assert "btn_do" not in lay
do_rect = (geo[0] + bb._CARD_PAD, geo[1] + 5,
           geo[0] + bb._CARD_PAD + 262, geo[1] + bb._CARD_FOOTER_H - 5)
assert bb._card_hit(lay, *centre(do_rect)) in ("btn_run", "btn_clear")
print("CARD_PASS hit tests: plan footer vs advice footer")

lay = bb._card_layout(geo, minimized=True)
assert bb._card_hit(lay, *centre(lay["chip"])) == "chip"
assert bb._card_hit(lay, 500, 500) is None
assert lay["chip"][:2] == (10, 10), "chip is pinned to the corner"
print("CARD_PASS minimised chip pinned to the corner")

# --- wrap + scroll math (measured width stubbed) -------------------
real_px = bb._card_text_px
bb._card_text_px = lambda text, size=11: len(text) * 6.0  # noqa: E731
try:
    lines = bb._card_wrap("aaaa bbbb cccc", 30)
    assert lines == ["aaaa", "bbbb", "cccc"], lines
    lines = bb._card_wrap("abcdefghij", 30)
    assert lines == ["abcde", "fghij"], lines
    lines = bb._card_wrap("one two\nthree", 60)
    assert lines == ["one two", "three"], lines
    # Words survive whole and in order.
    src = "the quick brown fox jumps"
    joined = "".join(bb._card_wrap(src, 42)).replace(" ", "")
    assert joined == src.replace(" ", ""), joined
    # Field view keeps the caret visible at the end of a long line.
    visible, caret_px = bb._card_field_view("0123456789ABCDEF", 16, 30)
    assert visible == "BCDEF" and caret_px == 30, (visible, caret_px)
    visible, caret_px = bb._card_field_view("0123456789", 4, 60)
    assert visible == "0123456789" and caret_px == 24
finally:
    bb._card_text_px = real_px
assert bb._card_clamp_scroll(5, 10, 4) == 5
assert bb._card_clamp_scroll(99, 10, 4) == 6
assert bb._card_clamp_scroll(-2, 10, 4) == 0
assert bb._card_clamp_scroll(3, 2, 4) == 0
print("CARD_PASS wrap, field view and scroll math")

# --- status line truth ----------------------------------------------
bb._EXPERT_JOB.update(busy=True, started=time.monotonic(), limit=140)
try:
    status = bb._card_status_text({"service": "CODEX", "key": "", "url": "", "model": ""})
    assert "Waiting for the expert" in status and "of 140s" in status and "Esc" in status
finally:
    bb._EXPERT_JOB["busy"] = False
assert "Ready" in bb._card_status_text(
    {"service": "KEY", "key": "k", "url": "", "model": "m"})
assert "Not set up yet" in bb._card_status_text(
    {"service": "KEY", "key": "", "url": "https://x", "model": "m"})
print("CARD_PASS status line: busy / ready / not set up")

# --- content sync mirrors the panel --------------------------------
wm.buddy_plan = ""
wm.buddy_answer = "Round the edge first, then smooth it."
lines, footer = bb._card_sync_content(ctx, 400)
assert footer is None
assert any("Round the edge" in line for line in lines), lines
wm.buddy_plan = json.dumps([{"kind": "button", "id": "add_cube"},
                            {"kind": "set", "id": "brush.size",
                             "value": 120}])
wm.buddy_plan_summary = "Add a cube, set the brush"
wm.buddy_plan_report = "Plan ready: 2 steps."
lines, footer = bb._card_sync_content(ctx, 400)
assert footer == "plan"
assert any("1." in line for line in lines), lines
assert any("2." in line for line in lines), lines
wm.buddy_plan = ""
wm.buddy_plan_summary = ""
wm.buddy_plan_report = ""
wm.buddy_answer = ""
print("CARD_PASS content sync: answer body, plan body + footer")

# --- the card ask path: capability answer with NO connection -------
bb._CARD["text"] = "what can you do for me"
bb._card_do_ask(ctx)
assert wm.buddy_ask == "what can you do for me"
assert "no connection at all" in wm.buddy_answer, wm.buddy_answer
assert bb._EXPERT_JOB["busy"] is False
print("CARD_PASS card ask -> local capability answer, no connection")

# --- the opener flips the card on ----------------------------------
bb._CARD["open"] = False
res = bpy.ops.buddy.expert_card_open()
assert res == {"FINISHED"} and bb._CARD["open"] is True
print("CARD_PASS opener reopens the card")

# --- autostart is a clean no-op headless ----------------------------
assert bb._card_autostart() is None
print("CARD_PASS autostart no-ops in background mode")

bb.unregister()
assert bb._EXPERT_HANDLE is None
print("ALL CARD TESTS PASSED")
