"""Blender Buddy visual-fit proof (v0.9).

Run with:
  blender -b --factory-startup --python tests/test_visual.py

Why this exists: real screenshots of the panel in a real Blender
window (taken under a virtual display) showed Blender cutting off
label lines with '...' wherever the add-on's fixed wrap widths were
wider than the actual sidebar. These checks pin the fix: wrapping
aims at the width that truly fits, and never wider.
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()
fails = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" - {detail}" if detail and not cond else ""))
    if not cond:
        fails.append(name)


class FakeRegion:
    def __init__(self, width):
        self.width = width


class FakeContext:
    def __init__(self, region):
        self.region = region


# No region (background Blender): the historical default.
check("fit width, no region", bb._fit_width(FakeContext(None)) == 44)
# The default sidebar from the screenshots: ~290px -> ~39 chars.
check("fit width, default sidebar", bb._fit_width(FakeContext(FakeRegion(290))) == 39,
      str(bb._fit_width(FakeContext(FakeRegion(290)))))
# A very wide panel is still capped so lines stay readable.
check("fit width, wide panel capped", bb._fit_width(FakeContext(FakeRegion(1200))) == 64)
# A very narrow panel never goes below the floor.
check("fit width, narrow floor", bb._fit_width(FakeContext(FakeRegion(160))) == 26)


class FakeLayout:
    def __init__(self):
        self.lines = []

    def label(self, text=""):
        self.lines.append(text)


bb._WRAP_CAP = 30
lay = FakeLayout()
bb._wrap(lay, "Blender calls this: UV Sphere   Key: Shift+A, then "
              "some more words to force a second line", width=52)
check("wrap honours the cap over a wider request",
      lay.lines and all(len(l) <= 30 for l in lay.lines),
      repr(lay.lines))
bb._WRAP_CAP = 64
lay2 = FakeLayout()
bb._wrap(lay2, "short text", width=44)
check("wrap under the cap is untouched", lay2.lines == ["short text"])

# Every Buddy button must explain itself in its hover tooltip too.
# A screenshot caught the 'Set up the expert' button showing
# Blender's '(undocumented operator)' instead - four operators had
# no description at all.
ops = [getattr(bb, n) for n in dir(bb) if n.startswith("BUDDY_OT")]
check("operators found", len(ops) >= 8, str(len(ops)))
for cls in ops:
    check(f"tooltip for {cls.bl_idname}",
          bool(getattr(cls, "bl_description", "").strip()))

# The floating card's shape. A real screenshot (v1.0 draft) caught
# the rounded rectangle folded into a wedge: the outline was fine,
# the fan primitive was not. The card is now explicit triangles
# built from the outline; pin the geometry: every point inside the
# rectangle, and the triangles' total area matching a rounded
# rectangle's true area (w*h minus the four corner squares' waste).
import math

pts = bb._rounded_rect_points(0, 0, 380, 58, 10)
check("card outline stays inside the rectangle",
      all(0 <= px <= 380 and 0 <= py <= 58 for px, py in pts))
tris = bb._fan_tris(190, 29, pts)
check("card fan is explicit triangles", len(tris) == 3 * len(pts))
area = 0.0
for i in range(0, len(tris), 3):
    (ax, ay), (bx, by), (cx, cy) = tris[i:i + 3]
    area += abs((bx - ax) * (cy - ay) - (cx - ax) * (by - ay)) / 2
want = 380 * 58 - (4 - math.pi) * 10 ** 2
check("card triangles cover the rounded rectangle",
      abs(area - want) < want * 0.02, f"{area:.0f} vs {want:.0f}")

bb.unregister()
print("FAILURES:", fails if fails else "none")
print("ALL VISUAL TESTS PASSED" if not fails else "VISUAL TESTS FAILED")
sys.exit(1 if fails else 0)
