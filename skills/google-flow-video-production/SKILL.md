---
name: google-flow-video-production
description: >-
  Use when generating images or video clips in Google Flow
  (labs.google/fx/tools/flow) for a video project, including consistent
  characters, batches from a script, and credit budgets.
---
# Google Flow video production

Flow is a browser app, so hand all of the work to a computerUse subagent with the steps below. The user must be signed in to a Google AI plan in the box browser. Never enter credentials. If a sign-in appears, stop and report the URL. Never buy or upgrade.

## Limits (Google AI Pro, check what the UI shows)
- Credits: 1,000 a month plus 50 a day. Read the remaining credits in the UI before and after each run.
- Images and 2K upscales don't use monthly credits but have daily caps: Nano Banana 2.1 / 2 Lite up to ~1,000 a day, Nano Banana Pro ~100 a day, 2K upscale ~200 a day. Short-term rate limits also apply.
- Video: Veo 3.1 Lite is ~10 credits per 4/6/8s at 720p. Omni Flash is ~1 credit/s at 360p or 3/s at 720p, up to 10-15s.
- The built-in Agent has a daily query limit that depends on the plan.

## Setup per series
1. Create one project per series (for example "<Series> <character>").
2. Make a character sheet first (front, side, expressions, the hero's unique marks), then upload it as an ingredient/reference.
3. Optionally set project instructions with the style suffix so every generation inherits it.

## Shot list to Flow
1. Turn the script's visual lines into a shot list: name, prompt, whether the hero appears, and whether it gets animated.
2. Add a fixed style suffix to every prompt, for example: "Clean flat 2D cartoon, thick black outlines, bright saturated colors, simple white round-head stickman with big round expressive eyes and thin black line limbs. 16:9. No text, no letters."
3. Hero shots: attach the reference and spell out the marks again, including eye shape (otherwise the eyes come out sleepy or squinted). Say that other characters don't share the hero's marks.
4. Generate with Nano Banana 2.1. Pick the best of the batch and regenerate once if the hero drifts or the image is muddy. Download at 2K upscale.
5. Animate only the key beats: Frames mode, image as the start frame (optional end frame), Veo 3.1 Lite 720p 8s. Describe small motion and a static or slow camera. Set a hard credit budget in the task (for example a maximum of 40 credits).
6. The Agent can turn a script into a storyboard and batch the shots. Use it for whole episodes, and still check each result.
7. Save to `<project>/flow/<episode>/` with the shot names, moving files out of your Downloads folder.

## Report back
File paths, credits used and remaining, and any shot where the hero drifted (eyes, outfit marks) or the quality was poor. Then review a contact sheet before the edit.
