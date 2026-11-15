---
name: stickman-explainer-pipeline
description: >-
  Use when making a stickman-style educational YouTube video or Short (script,
  character, images, clips, voice, edit, thumbnail).
---
# Stickman explainer pipeline

The quality bar is a top channel in the niche. Never send a robotic voice or a slideshow of still pictures as a finished result. Check every output yourself first, and say plainly what still falls short.

## 1. Idea and script
- Choose the topic from viral-video-teardown data, not from a hunch.
- Script in second person, ~200 wpm. Open on a present-day comfort, flip back in time, and say the title question out loud by ~0:40. Start a new chapter every 1-1.5 min, with a new fact every 15-20s. Each fact gets a named source and method. Keep jokes dry and in the visuals, about one a minute. End with a callback to the opening, and almost no subscribe ask.
- Research the web, keep a source list, and flag uncertain claims.
- Write one visual line under every narration line.

## 2. Character and style
- Give the channel one recurring hero with 3-4 unique marks (hair, a mark on the clothing, an accessory) that set him apart from competitors. Make a character sheet.
- Style: white round head, big round expressive eyes, thin black line limbs, simple costumes, bright clean flat cartoon backgrounds with thick outlines. No painted or realistic look.
- In every prompt, say the background characters don't share the hero's marks, or they will copy his outfit.

## 3. Images and clips: Google Flow (if the user has Google AI Pro signed in on the box browser)
- Hand Flow work to a computerUse subagent. Use one Flow project per series and upload the character sheet as an ingredient.
- Images: Nano Banana 2.1. They don't use monthly credits (Pro gives up to ~1,000 a day). Upscale to 2K.
- Clips: Frames mode with the image as the start frame, Veo 3.1 Lite, 720p, 8s, ~10 credits each. Animate only the key beats, and set a credit budget in the task.
- Flow's built-in agent can plan storyboards and batch shots from a script.
- Fall back to GenerateImage/GenerateVideo with the reference sheet if Flow isn't available.

## 4. Voice
- Use free voices only if the user wants free. Test several and keep the most natural (Microsoft Edge multilingual neural voices, or Chatterbox under the MIT licence), and run a Whisper check.
- Avoid Kokoro for narration (flat), and F5-TTS/XTTS for monetized channels (non-commercial licences).
- Paid upgrade if the user wants it: ElevenLabs.

## 5. Edit (ffmpeg)
- 1920x1080, 30fps. Hard cuts on the narration every 2-4s, gentle Ken Burns on stills, lanczos upscaling for clips.
- Use only a few text cards (key numbers, dates). No word-by-word subtitles in long-form. Mix the narration at about -16 LUFS.
- Review a contact sheet with one frame per second plus a Whisper pass, and iterate at least twice.

## 6. Thumbnail (1280x720)
- 1-2 huge yellow words plus "?" in a heavy rounded font with a thick black outline, added with Pillow over a no-text scene.
- One character with a strong reaction and one clear scene. Strong colour contrast, and keep the bottom-right corner clear. Check it at 246x138.
- Make 2 options for A/B testing.
