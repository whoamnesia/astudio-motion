# Sound for code-made films

**Sound only on request.** Deliver a silent master by default (with `-an`, no empty audio track); add music, SFX or
VO only when the brief asks for sound or supplies a track, and otherwise offer it as a next step in one line. When
you do make sound: you cannot hear - say so in the delivery note; measure what you can (loudness, peaks, timing) and
leave listening to the person.

## Sources (licensed only)
- the person's track/VO; royalty-free libraries they hold a licence for; free-licence libraries checked per item
  (Pixabay Music, Free Music Archive with CC-BY, YouTube Audio Library terms); synthesized SFX made in code.
- Never "found" music. Mark placeholders clearly.

## Beat grid
```bash
# tempo + beat times (if Python with numpy/librosa is available)
python3 -c "import librosa,sys; y,sr=librosa.load(sys.argv[1]); t,b=librosa.beat.beat_track(y=y,sr=sr,units='time'); print(round(float(t),1)); print([round(x,3) for x in b[:32]])" track.mp3
```
Without librosa: ask for the BPM or detect onsets with ffmpeg `silencedetect`/`astats` around kicks. frames per beat =
fps × 60 / BPM; compute beat k as `round(k * fps * 60 / BPM)`, never accumulate rounded beats. Start on a downbeat,
cut the song window so the drop lands on the product's big moment; something happens on every beat during the build.

## Synthesized UI sounds (ffmpeg lavfi)
```bash
ffmpeg -f lavfi -i "sine=frequency=1800:duration=0.04" -af "afade=t=out:st=0.01:d=0.03,volume=0.35" click.wav     # tick
ffmpeg -f lavfi -i "anoisesrc=d=0.35:c=pink:a=0.5" -af "highpass=f=600,lowpass=f=6000,afade=t=in:d=0.15,afade=t=out:st=0.2:d=0.15,volume=0.4" whoosh.wav
ffmpeg -f lavfi -i "sine=frequency=110:duration=0.6" -af "afade=t=out:st=0.05:d=0.55,volume=0.9" hit.wav          # low hit on a settle
```
Place each sound at its visual event time (the click frame, the settle frame) - same frame, never "shortly after".

## Mixing onto the render
```bash
# music bed at -18 LUFS-ish under SFX, SFX at their event times, fade out the last 1.5s
ffmpeg -i film.mp4 -i music.mp3 -i click.wav -i whoosh.wav \
  -filter_complex "[1:a]volume=0.5,afade=t=out:st=28.5:d=1.5[m];[2:a]adelay=4200|4200[c];[3:a]adelay=6100|6100[w];[m][c][w]amix=inputs=3:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest film-sound.mp4
ffmpeg -i film-sound.mp4 -af ebur128 -f null - 2>&1 | grep -E "I:|LRA:|Peak"     # integrated loudness: aim -14 LUFS (social) / -16 (web)
ffmpeg -i film-sound.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy final.mp4     # normalise
```

## Captions
SRT/VTT with 1-2 lines <= 32 chars, 1-6s each, synced to VO timestamps; burn in for social
(`-vf subtitles=captions.srt:force_style='FontName=Inter,FontSize=48,PrimaryColour=&H00FFFFFF&,Outline=0,BorderStyle=3'`)
or ship sidecar for web players.
