# Clinical Scribe — AI Documentation Assistant
> Audio → Transcript → Structured SOAP Note | English + Hindi + Hinglish


## What this does
Records or accepts a doctor-patient consultation audio file, transcribes it 
(including Hindi and mixed language), and generates a structured SOAP note 
with anomaly flags and a patient-facing Hindi summary.

## Setup (do this once)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get your free Gemini API key
- Go to: https://aistudio.google.com
- Sign in with Google → click "Get API Key" → Create key
- Copy the key

### 3. Add your key to .env
Open `.env` and replace `your_key_here` with your actual key:
```
GEMINI_API_KEY=AIza...your_actual_key_here
```

---

## How to run

### Option A — Full pipeline (audio file → SOAP note)
```bash
python app.py audio/consultation.mp3
```
Supported audio formats: .mp3, .wav, .m4a, .ogg, .flac

### Option B — Text mode (paste transcript manually, great for testing)
```bash
python app.py --text
```
Then paste your transcript, type END on a new line, press Enter.

### Option C — Test just the transcription
```bash
python transcribe.py audio/consultation.mp3
```

### Option D — Test just the note generation (with built-in mock transcript)
```bash
python generate_note.py
```

---

## Project structure
```
clinical-scribe/
├── app.py              ← Main pipeline (run this)
├── transcribe.py       ← Step 1: Audio → Transcript (Whisper)
├── generate_note.py    ← Step 2: Transcript → SOAP Note (Gemini)
├── requirements.txt    ← Python dependencies
├── .env                ← Your API key (never share this)
├── audio/              ← Put your audio files here
├── transcripts/        ← Saved transcripts appear here
└── notes/              ← Saved SOAP notes (JSON) appear here
```

---

## Output
Each run produces:
- `transcripts/<name>_transcript.txt` — raw transcript
- `notes/<name>_soap_note.json` — structured SOAP note with:
  - Subjective / Objective / Assessment / Plan sections
  - Confidence score per section
  - Anomaly flags
  - Hindi patient summary
  - Disclaimer and metadata

---

## Important disclaimer
This system is for research and demonstration purposes only.
All AI-generated notes must be reviewed, edited, and signed off 
by a licensed physician before any clinical use.
