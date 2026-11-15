# POV episode builder

```bash
export FONT_DIR=/path/to/Anton-Inter-BebasNeue   # if they are not on the system
# Optional layout-pass TTS (Kokoro ONNX models, Apache-2.0):
#   mkdir -p scripts/pov/models
#   # place kokoro-v1.0.onnx and voices-v1.0.bin in that folder
#   # or set KOKORO_DIR

# Put first-person stills next to the names in the episode JSON:
#   scripts/pov/assets/img/s1_couch.jpg
#   scripts/pov/assets/img/s2_stairs.jpg
#   scripts/pov/assets/img/s3_monitor.jpg
#   scripts/pov/assets/img/s4_girl.jpg

python3 scripts/pov/build.py scripts/pov/episodes/ep1_test.json
```

`episodes/ep1_test.json` is a 29-second sample of the format (shots, phone UI, lines, SFX, choice card). Copy it to start a full 2-minute episode. `sfx.py` synthesizes the sound effects, so you do not need a licensed library.

Stills are not included — generate them from the prompt template in `skills/pov-interactive-horror/SKILL.md`. Re-renders are cached under `build_cache/`.
