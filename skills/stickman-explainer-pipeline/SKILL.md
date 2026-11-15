---
name: stickman-explainer-pipeline
description: >-
  Use when making a stickman-style educational YouTube video or Short (script,
  character, images, clips, voice, edit, thumbnail).
---
# Stickman explainer pipeline

The quality bar is a top channel in the niche (Ink Explainer-style). Never send a robotic voice, a soft/blurry frame, or a slideshow as a finished result. Check every output yourself first, attach the video, and say plainly what still falls short. Owners are often blunt: fix the exact thing they flag, fast.

## 0. Save the owner's credits
Generate images and clips in Google Flow (follow google-flow-video-production) whenever the owner has a Google AI plan signed in. Avoid built-in GenerateImage/GenerateVideo; use them only if Flow, Gemini, or Meta AI are all unavailable.

## 1. Idea and script
- Choose the topic from viral-video-teardown data, not from a hunch.
- Second person, ~200 wpm, dry jokes in the visuals (~1 a minute), a new fact every 15-20s with a named source and method, a chapter every 1-1.5 min, an ending that calls back to the hook, and almost no subscribe ask.
- **Hook (most important):** drop the viewer straight into the hardship. Example: "Imagine you're stuck in the middle of nowhere. It's forty degrees. Today? Tap water, AC, a cold juice, an ice bath, or just hop in the pool. But fifty thousand years ago?" The past era must be on screen by ~8-10s, and the title question spoken by ~20s. No long present-day scenes, no modern statistics or news in the hook. A fast comfort montage (~1s per cut) is the only modern part.
- Research the web, keep a source list, and flag uncertain claims.
- Write one visual line under every narration line, then a shot-list file (name, exact prompt with style suffix, hero yes/no, animate yes/no + motion text). The browser subagent opens it via file:// and copies prompts exactly.

## 2. Character and style
- One recurring hero with 3-4 unique marks (hair, a clothing mark, an accessory) plus a character sheet.
- Style: white round head, BIG WIDE ROUND eyes (state it every prompt, or they come out sleepy), thin black line limbs, bright flat cartoon backgrounds, thick outlines. Nothing painterly or realistic.
- Other characters: say they do NOT have the hero's marks, and don't attach the hero sheet as a reference for shots he isn't in (use a style frame plus a separate character ref).

## 3. Images and clips
- Via google-flow-video-production. Stills at 2K, and animate only the key beats with a hard credit cap.
- Flow video downloads are 720p and its 1080p upscale often fails. Upscaled 720p looks soft at 1080p and owners notice. Use clips only for short (~1s) action beats; for any shot held longer than ~1.5s, use the 2K still with ffmpeg motion (push-in, heat shimmer, pulses, shakes) instead.

## 4. Voice
- Free: Microsoft Edge neural (Brian Multilingual at about +28% speed tested best), or Chatterbox (MIT). Test a few, and run a Whisper check.
- Avoid Kokoro (flat), and F5-TTS/XTTS for monetized channels (non-commercial licences). Paid upgrade: ElevenLabs. Tell the owner the voice is still the weakest link if it is TTS.

## 5. Edit (ffmpeg, done by an executor)
- 1920x1080, 30fps, cut from 2K sources with lanczos plus a light unsharp. Hard cuts every 1-4s, punch-ins on every beat, and few text cards (key numbers/dates), placed off faces and the sun. No word-by-word subtitles in long-form. Narration at -16 LUFS, music ducked and quiet, under ~1.5s silent tail.
- Review a contact sheet with one frame per second, sharpness crops of each shot, and a Whisper pass. Iterate at least twice before showing the owner.
- Workflow split: the browser subagent makes Flow assets into /workspace/<project>/flow/<episode>/, then an executor renders. Test the opening (~25-30s) with the owner before the full episode.

## 6. Thumbnail (1280x720)
- 1-2 huge yellow words plus "?" in a heavy rounded font with a thick black outline, over a no-text scene (Pillow).
- One character with a strong reaction, one clear scene, strong contrast, bottom-right corner kept clear. Check at 246x138, and make 2 options for A/B testing.
