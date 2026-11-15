---
name: google-flow-video-production
description: >-
  Use when generating images or video clips in Google Flow
  (labs.google/fx/tools/flow) for a video project, including consistent
  characters, batches from a script, and credit budgets.
---
# Google Flow video production

Flow is a browser app: hand all of the work to a computerUse subagent with the steps below (one dispatch per batch, ~6 stills + up to 4 clips fits one run; if it times out, resume it once to finish). The owner must be signed in to a Google AI plan in the box browser. Never enter credentials; on a sign-in, stop and report the URL. Never buy, upgrade, or start a trial. Prefer Flow over the bot's own image/video generation, to save the owner's credits.

## Limits (Google AI Pro, check the UI)
- Credits: 1,000 a month plus 50 a day (the balance can jump up mid-run when the daily grant lands). Read the balance before and after.
- Images and 2K upscales are free of monthly credits, with daily caps: Nano Banana 2.1 / 2 Lite ~1,000 a day, Nano Banana Pro ~100 a day, 2K upscale ~200 a day.
- Video: Veo 3.1 Lite ~10 credits per 8s clip at 720p. Downloads are 720p, and the 1080p upscale frequently fails ("Upscaling failed!"), with 4K disabled on Pro. Plan for 720p clips.
- The built-in Agent has a daily query limit.

## Setup per series
1. One project per series. Make a hero character sheet first and upload it as an ingredient.
2. Optionally set project instructions with the style suffix.

## Shot list to Flow
1. Write a shot-list markdown file on the box (name, exact prompt, hero yes/no, animate yes/no, motion text). Tell the subagent to open it in a tab via file:///path and copy prompts exactly.
2. A fixed style suffix on every prompt, for example: "Clean flat 2D cartoon, thick black outlines, bright saturated colors, simple white round-head stickman with big round expressive eyes and thin black line limbs. 16:9. No text, no letters."
3. Hero shots: attach the sheet, and restate the marks and "big wide round eyes, never sleepy or squinted." Non-hero shots: do NOT attach the hero sheet (it leaks his hair and outfit). Attach a style frame plus that character's own ref, and paste a "NOT the hero, has NO <marks>" lock.
4. Use the Flow Agent first (owner's preference) to batch the stills with Nano Banana 2.1. If it errors ("Something went wrong"), generate directly. Reject and regenerate once for drifted marks, sleepy eyes, text/logos, a painterly or 3D look, or extra characters. Download the keepers at 2K upscale (2752x1536).
5. Animate only short action beats: Frames mode, still as the start frame, Veo 3.1 Lite 720p 8s, locked or slow camera, one simple action, a hard credit cap (e.g. 40). Avoid zooms into faces (Veo melts them). Any shot held on screen more than ~1.5s should be a 2K still animated in the edit, not a 720p clip.
6. Nested download menus (resolution choices) often close on browser clicks; use desktop clicks for them. Move files from ~/Downloads to /workspace/<project>/flow/<episode>/<shot>.jpg|mp4 and verify their resolutions.

## Report back
File paths and resolutions, credits before and after, which shots drifted or look weak, and whether the Agent worked. Then an executor reviews a contact sheet and renders.
