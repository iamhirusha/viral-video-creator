# Free voice helpers

| Script | Engine | Licence notes |
|--------|--------|----------------|
| `edge_tts_gen.py` | Microsoft Edge neural voices | Free, needs network. Good default for a clean narrator. |
| `chatterbox_gen.py` | Chatterbox | MIT. More emotion than Edge. Optional `--ref` uses *your* audio only. |
| `f5_gen.py` | F5-TTS | **Non-commercial.** Do not use on a monetized channel. You must supply your own reference wav — none is included here. |
| `whisper_check.py` | faster-whisper | Score WER and pitch on a take before you lock a voice. |

`jobs.example.txt` is a Chatterbox batch that uses the model's default voice only.
