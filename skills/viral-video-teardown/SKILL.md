---
name: viral-video-teardown
description: >-
  Use when the user shares a viral video, post, or a set of channels to learn
  from, before proposing ideas or making anything.
---
# Viral video teardown

The goal is to learn why something wins: ideas and storytelling first, looks second.

## A single post or video
1. Read the post with the X tools (or WebFetch for other sites). Note views, likes, bookmarks, follower count, and any quoted post or shared prompt (a long post may carry a full prompt in `note_tweet`).
2. Download the MP4 to your working directory and send it to a watchVideo subagent (or watch it yourself). Ask for: a detailed description, the hook in the first 3 seconds, how often the stakes rise, camera view, sound, captions, story structure, the ending/CTA, visual style and likely tools, and length.
3. Turn it into a reusable formula of 5-7 steps.

## A set of channels (always do this, never judge from screenshots alone)
1. Pull each channel's full long-form list with `yt-dlp --flat-playlist -J`: title, views, duration, date. Save a CSV.
2. Compute the median views per video, upload pace, which title patterns and topics hit vs. flop, how concentrated views are in the top videos, and how length relates to views.
3. Pull auto-subtitles (`yt-dlp --write-auto-subs --skip-download`) for the top 3 videos per channel. Analyze the hook in the first 30-40s, words per minute, how facts are framed (named scientist plus method), joke rate, recurring beats (guess-then-reverse, "you're probably thinking"), and the ending.
4. Find gaps: proven angles nobody in the set has covered yet.
5. Report the insights as data with numbers, then a ranked idea list that ties each idea to the data. Don't copy titles or scripts.

## Lessons
- Present-day hook, then the flip, then the title question said out loud in the first ~40s beats generic trivia.
- Fewer, better videos usually beat high-volume uploading.
- Contradiction titles ("Why X if Y?") and "what did ancient humans do when <weather/hardship>" work well for stickman explainers.
