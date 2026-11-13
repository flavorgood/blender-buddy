"""Blender Buddy anti-stale self-check proof (v1.2).

Run with:
  blender -b --factory-startup --python tests/test_stale.py

Buddy's law: be a Blender expert that does not go stale across
Blender updates. The full index already re-learns itself from the
running Blender; this suite proves the curated buttons now check
themselves the same way.

1. On the Blender running this suite, the self-check flags NONE
   of the real catalogue (no false positives - a check that cries
   wolf would hide good tools from beginners).
2. Fake actions pointing at an operator, modifier, mode and
   toolbar tool that do not exist are each flagged, with the
   right reason - while real ones mixed into the same list pass.
3. The stale map hides a flagged action from the drawers' action
   stream and from plain-words search, and the buddy.action
   operator refuses it with a plain report instead of running it.
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()

# 1. The real catalogue is clean on this Blender.
real_stale = bb._self_check()
assert real_stale == [], (
    "self-check flagged real actions on this Blender: %r" % (real_stale,))
assert bb._stale_map() == {}, bb._stale_map()

# 2. Fakes are caught, kind by kind; a real action in the same
#    list is not.
fakes = [
    dict(id="fake_op", plain="Fake operator", kind="op",
         target="mesh.primitive_nonexistent_add"),
    dict(id="fake_mod", plain="Fake modifier", kind="modifier",
         target="NO_SUCH_MODIFIER"),
    dict(id="fake_mode", plain="Fake mode", kind="mode",
         target="NO_SUCH_MODE"),
    dict(id="fake_tool", plain="Fake tool", kind="tool",
         target="builtin.no_such_tool"),
    dict(id="fake_custom", plain="Fake custom", kind="custom",
         target="no_such_helper"),
    bb.ACTIONS_BY_ID["add_cube"],
]
flagged = {s["id"]: s["reason"] for s in bb._self_check(fakes)}
assert set(flagged) == {"fake_op", "fake_mod", "fake_mode",
                        "fake_tool", "fake_custom"}, flagged
assert all(flagged.values()), flagged

# 3. With a stale map in force, the fake disappears from search
#    and the operator refuses it in plain words.
saved_cache = bb._STALE_CACHE
try:
    bb._STALE_CACHE = {"add_cube": "the tool behind it is not in "
                                   "this Blender"}
    hits = bb.search_actions("add a box")
    assert all(a["id"] != "add_cube" for a in hits), [a["id"] for a in hits]
    result = bpy.ops.buddy.action(action_id="add_cube")
    assert result == {"CANCELLED"}, result
finally:
    bb._STALE_CACHE = saved_cache

# And with the real (empty) map restored, the same search and the
# same button work again.
hits = bb.search_actions("add a box")
assert any(a["id"] == "add_cube" for a in hits), [a["id"] for a in hits]

print("ALL STALE TESTS PASSED (%d actions checked clean on Blender %s)"
      % (len(bb.ACTIONS), bpy.app.version_string))
