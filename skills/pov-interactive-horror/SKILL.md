---
name: pov-interactive-horror
description: >-
  Use when making a first-person interactive horror Short or Reels episode
  that ends on a 2-choice cliffhanger (script, stills, phone UI, voices,
  edit, choice screen).
---
# POV interactive horror

The viewer is the protagonist. Every episode is an original story: a mundane setting, a rising threat, a paradox twist, and a 2-choice cliffhanger that asks people to comment for Part 2. Never reuse a script or twist from another creator.

The quality bar is a finished vertical episode, not a slideshow of stills with a robotic voice. Check the cut yourself before you send it, and say plainly what still falls short.

## The 7-step formula

Build every episode in this order. Escalate about every 10–15 seconds; no dead air.

1. **POV mundane setting.** First-person, present tense, whispered narration. You can see your own hands, sleeves, and phone. Start in a quiet, ordinary place (a classroom, a night of babysitting, a late shift).
2. **Ambiguous disturbance.** A sound hook in the first second, and the first spoken line by 0:03 (a thud, a knock, a flicker). It could still be nothing.
3. **Confirmation of danger.** A new sound, a broken rule, or a visual that proves this is not a false alarm.
4. **Digital connection via phone UI.** The phone is the second witness: texts, a camera app, a location dot, or a call. The clock in the status bar is part of the story.
5. **Threat at the door.** The danger arrives in the room — a voice in the hall, a knock, a hand — while you are still watching the phone.
6. **Paradox twist.** Around 1:15, two sources you trust contradict each other, and both cannot be true (the voice at the door vs. the text that says "don't open").
7. **2-choice cliffhanger + "comment for Part 2".** Cut to black. "WHAT DO YOU DO?" then option A and option B, 3 words max per option, then "COMMENT FOR PART 2".

## Format rules

1. It is always "you". Narrator: whispered, present tense, short sentences.
2. Runtime 2:00–2:20 (past the 1-minute monetization line), 9:16, 1080×1920, 30 fps.
3. A sound hook in the first second; first spoken line by 0:03.
4. Escalate every 10–15 seconds: a new sound, new text, new visual, or a broken rule.
5. Every episode has a phone screen.
6. The paradox twist lands around 1:15.
7. Every episode ends on the 2-choice card, then "COMMENT FOR PART 2".
8. The majority decides Part 2. Count top-level comments across platforms within 48 hours (or use a poll as a tiebreaker). Part 2 opens with the result on screen: *"71% of you chose STAY WITH HER."*
9. Give the viewer a "rule" early (don't go upstairs after midnight) and break or test it later.
10. Pin a comment: `A: OPTION ONE 🔴 / B: OPTION TWO ⚪ (majority = Part 2)`.
11. Cadence: Part 1 → Part 2 within 48 hours, while the comment fight is still going. Then a new story. Settings rotate; characters can return for a universe arc.
12. Original stories only.

A series name that invites argument in the comments (for example "Wrong Choice") works well. Check handle availability on every platform before you commit.

## Visual style

Flat 2D cel-shaded horror cartoon. Bold, clean black outlines, flat shading with at most 2 tones per surface, minimal texture. First-person POV in every shot. Faces are simple; the only "wrong" detail is blank white eyes or a smile that is slightly too wide. Never show gore — imply it (a dark smear, a shadow).

**Palette**

| Role | Hex |
|------|-----|
| Midnight navy (base shadow) | `#0B1426` |
| Charcoal (deep black) | `#15171C` |
| TV / screen teal (cold light) | `#3FD0D4` |
| Lamp amber (the only warm safe light) | `#E8A33D` |
| Blood red (brand accent, highlighted words, choice A) | `#FF2D2D` |
| Bone white (eyes, text) | `#F2EDE4` |

Every shot has exactly one cold source and at most one warm source. When the amber light dies, safety leaves with it.

**Master image prompt** (pass a locked style-reference still every time):

> Flat 2D horror cartoon illustration, first-person POV, {scene}. Bold clean outlines, flat cel shading, limited palette: deep navy and charcoal shadows, cold teal light, one amber accent, small touches of blood red. Moody, unsettling, minimal detail, no text, vertical 9:16.

**Captions:** Anton, uppercase, 110–120 px, white fill with an 11 px black stroke. 1–3 words on screen at a time. The word being spoken turns blood red and pops to 118% scale over 120 ms. Lower third (y ≈ 1600 of 1920); move down to y ≈ 1760 when the phone UI is on. Other speakers get a small tag above the line in Inter Bold, pale blue: `MIA (upstairs)`.

**Phone UI:** a realistic dark-mode messenger or app screen in Inter. The phone slides up from the bottom; the scene behind it dims to 50%.

**Choice screen:** pure black. "WHAT DO YOU DO?" in Bebas Neue. Option A has a red outline, option B a white outline, 3 words max. Under them: "COMMENT FOR PART 2" in red.

**Sound:** a constant low drone, room tone that fits the setting (rain, hum, wind), and a sound hit in the first second. Whispered narrator, sidechain ducking under dialogue, a heartbeat during the build-up, and a dissonant sting with a red flash on the twist.

## Production

Use the local pipeline in `scripts/pov/`:

```
python3 scripts/pov/build.py scripts/pov/episodes/ep1_test.json
```

- Write the episode as JSON: shots (image, zoom, focus, shake), phone UI (chat / monitor), voice lines, SFX cues, ambience, flicker and flash, choice card. Copy `episodes/ep1_test.json` as the template.
- Generate 10–14 stills from the prompt template, all in one style, first-person. Optionally animate 2–3 key beats in Google Flow (see google-flow-video-production).
- `sfx.py` synthesizes thud, creak, footstep, ping, sting, riser, heartbeat, lullaby, rain, and drone, so you do not need licensed sound libraries.
- Voices: free Edge neural voices or Chatterbox (MIT) if the user wants free tools. Test several and keep the most natural; run a Whisper check. Avoid Kokoro as the final narrator (too flat) unless it is only a layout pass. F5-TTS and XTTS are non-commercial — do not use them on a monetized channel. Paid upgrade if the user wants it: ElevenLabs.
- Output: 1080×1920, 30 fps, libx264 + AAC. Mix narration around -16 LUFS. Review a contact sheet (one frame per second) plus a Whisper pass, and iterate at least twice.
