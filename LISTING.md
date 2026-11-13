# Blender Buddy — store listing draft (for extensions.blender.org)

Status: the extension package is BUILT and validated by Blender's
own tooling (`blender_buddy_v1.2.1_extension.zip`, built from
`extension_src/`), and it installs + enables through Blender's
extension system in a fresh profile. What remains is human-side:
a Blender ID account, the maintainer's license ruling (below), and
the submit button on the platform. Nothing here is live yet.

## Name
Blender Buddy - Blender in Plain Words

## Tagline (max 64 chars, as validated)
AAA-level 3D creation, usable by anyone

## Tags (platform list)
3D View · User Interface · Mesh · Modeling · Material · Sculpt

## Description (official — owner-approved pitch, 2026-11-12)
Blender is the free professional studio behind films, video
games, product designs, architecture and 3D printing — the same
class of tool the big studios pay thousands per seat for, except
Blender costs nothing. It has exactly one flaw, and it's fatal:
it is famously unusable by normal people. Its thousands of tools
are hidden behind keyboard shortcuts and insider jargon, so most
people who open it — people with real ideas — quit within the
first hour. The power was never the problem. The door is locked.

Blender Buddy doesn't translate Blender. It redesigns how
Blender is used — putting AAA-level modeling usability in the
hands of normal people with great ideas:

• Tools organised by the job you're trying to do, everything
  visible on screen instead of hidden behind shortcuts.
• Search in your own everyday words — typos and all — and be
  handed the right tool.
• Learn by doing real projects, starting with the famous Donut,
  while Buddy watches your work and moves you forward as each
  step lands.
• Your own AI expert inside Blender: it knows your scene,
  answers in plain language, and can operate the tools with you.
• Nothing removed, nothing dumbed down — and Buddy re-checks
  itself against each new version of Blender, so it never goes
  stale as the software evolves.

The details:

• Every button is named by the JOB — "Round off a sharp edge",
  "Cut one shape out of another" — with one plain sentence saying
  what it does before you press it, and Blender's real name and
  shortcut in small text so you learn the real words as you go.
• Search in your own words: synonyms, half-words, US spellings and
  typos all find their tool ("bevell", "squish it flat",
  "doughnut shape"). Gibberish finds nothing.
• Nothing is lost: the 96 everyday tools sit on plain-words
  buttons, and ALL of Blender's tools (2,410 on Blender 4.2.5)
  are in the searchable index in the same panel, each runnable.
• Day 1 is the Donut: the famous first project as 8 taught
  steps — you do each one with your own hands, guided in plain
  words, and a step only ticks off when your scene proves
  it's done.
• Your own AI agent (optional, bring your own access): ask in
  plain words and it answers for YOUR scene — or, with agent mode
  on, writes a short plan you check and run: pressing tools,
  setting exact values (like the exact sculpt brush you asked
  for), styling node trees, finding add-ons. Power it by an AI
  key (OpenAI-style or Claude), by your ChatGPT login through
  OpenAI's own Codex program, or by a free local AI — no account
  with Blender Buddy, nothing phones home.

Blender's own interface, menus and shortcuts are untouched. Turn
Buddy off and Blender is exactly as it was.

Free forever — built to impact humanity, not to bill it.

## Permission justification (network)
Declared in the manifest. Network is used ONLY when the user asks
the Buddy Expert something or runs one of its plans, and only to
the service/program/local AI the user themselves chose in the
add-on preferences. The question and a short scene summary are
sent; nothing else, and never in the background.

## License — RULED AND DONE (owner, 2026-11-12)
The owner chose the stay-free license: the whole add-on is now
GPL-3.0-or-later, in the repo's LICENSE file, the README, and the
extension manifest alike — one license everywhere, matching what
the platform expects (Blender itself is GPL and add-ons build on
its Python API).

## Submission checklist for the owner (about 5 minutes)
1. Create a Blender ID at id.blender.org (free).
2. ~~Rule on the license~~ — done, GPL-3.0-or-later (above).
3. On extensions.blender.org: Submit → upload
   `blender_buddy_v1.2.1_extension.zip` → paste the description
   above → answer the network-permission question with the
   justification above.
4. Review by the platform team follows; fixes, if any, come back
   as review notes.

## GitHub About (set 2026-11-12, wording updated 2026-11-12)
Description: "Blender Buddy redesigns how Blender is used:
AAA-level 3D creation in the hands of normal people with great
ideas. Tools organised by the job, search in your own words,
learn-by-doing projects, your own AI expert — nothing removed.
Free forever (GPL)."
Topics: blender, blender-addon, blender-extension, beginners,
3d-modeling, blender-tutorial, plain-language, ai-agent
