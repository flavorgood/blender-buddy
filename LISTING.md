# Blender Buddy — store listing draft (for extensions.blender.org)

Status: the extension package is BUILT and validated by Blender's
own tooling (`blender_buddy_v0.8_extension.zip`, built from
`extension_src/`), and it installs + enables through Blender's
extension system in a fresh profile. What remains is human-side:
a Blender ID account, the maintainer's license ruling (below), and
the submit button on the platform. Nothing here is live yet.

## Name
Blender Buddy - Blender in Plain Words

## Tagline (max 64 chars, as validated)
Blender in plain words: every tool visible, named by its job

## Tags (platform list)
3D View · User Interface · Mesh · Modeling · Material · Sculpt

## Description (draft)
Blender is powerful and famously hard to start. Its tools hide
behind shortcuts and names you have to already know — so most
beginners quit in the first hour.

Blender Buddy changes none of Blender's functions. It makes them
visible, in plain words:

• Every button is named by the JOB — "Round off a sharp edge",
  "Cut one shape out of another" — with one plain sentence saying
  what it does before you press it, and Blender's real name and
  shortcut in small text so you learn the real words as you go.
• Search in your own words: synonyms, half-words, US spellings and
  typos all find their tool ("bevell", "squish it flat",
  "doughnut shape"). Gibberish finds nothing.
• Nothing is lost: the 93 everyday tools sit on plain-words
  buttons, and ALL of Blender's tools (2,410 on Blender 4.2.5)
  are in the searchable index in the same panel, each runnable.
• Day 1 is the Donut: the famous first project as 8 one-press
  steps, built the way the original tutorial builds it, and a
  step only ticks off when your scene proves it's done.
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

## Permission justification (network)
Declared in the manifest. Network is used ONLY when the user asks
the Buddy Expert something or runs one of its plans, and only to
the service/program/local AI the user themselves chose in the
add-on preferences. The question and a short scene summary are
sent; nothing else, and never in the background.

## License — OWNER DECISION NEEDED
The GitHub code is MIT. The extension manifest currently declares
GPL-3.0-or-later, the platform's expected license for add-ons
(Blender itself is GPL and add-ons build on its Python API).
Before submitting, the owner must rule: relicense the add-on to
GPL-3.0-or-later (recommended for the platform), or keep MIT and
accept the platform may refuse the listing.

## Submission checklist for the owner (about 5 minutes)
1. Create a Blender ID at id.blender.org (free).
2. Rule on the license above.
3. On extensions.blender.org: Submit → upload
   `blender_buddy_v0.8_extension.zip` → paste the description
   above → answer the network-permission question with the
   justification above.
4. Review by the platform team follows; fixes, if any, come back
   as review notes.

## GitHub About (set 2026-11-12)
Description: "Blender in plain words — a free add-on that makes
every Blender tool visible, named by the job and searchable in
your own words, with a Donut first project and your own AI agent.
Beginner-proof: if a day-1 beginner can't use it, we aren't done."
Topics: blender, blender-addon, blender-extension, beginners,
3d-modeling, blender-tutorial, plain-language, ai-agent
