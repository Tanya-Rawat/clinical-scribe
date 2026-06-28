# 🏥 Clinical Scribe — AI Documentation Assistant

> **Audio → Transcript → Structured SOAP Note**
> English · Hindi · Hinglish (code-switched speech)

Built for **NextGen Nexus 2025 — National Generative AI Buildathon | Healthcare Track**

---

## What this does

Clinical Scribe converts doctor-patient consultation audio into structured medical notes — automatically. It transcribes multilingual speech (including Hindi-English code-switching), generates SOAP notes using an LLM, flags clinical anomalies, and produces a patient-facing Hindi summary.

**The problem it solves:** Doctors in India spend 2+ hours daily on documentation. With a 1:1700 doctor-to-patient ratio, every minute matters. Clinical Scribe gives that time back.

---

## Features

| Feature | Details |
|---|---|
| 🎙️ Multilingual transcription | Hindi, English, Hinglish — auto-detected via OpenAI Whisper |
| 📋 Structured SOAP notes | Subjective, Objective, Assessment, Plan — with confidence scores |
| 🚨 Anomaly flagging | Drug interactions, abnormal vitals, allergy conflicts |
| 🇮🇳 Hindi patient summary | Plain language summary for patient-facing use |
| 🗂️ Patient history summary | Summarizes past records into a 30-second doctor briefing |
| 💊 Prescription draft | Clearly labelled simulation — not for clinical use |
| 🛡️ Responsible AI | Mandatory doctor review, confidence scores, bias disclaimers |
| 🖥️ Streamlit UI | Clean browser interface — upload audio, see SOAP note instantly |

---

## Tech stack

- **ASR:** OpenAI Whisper (runs locally, no API key needed)
- **LLM:** Groq API — `llama-3.3-70b-versatile` (free tier, no daily quota issues)
- **UI:** Streamlit
- **Language:** Python 3.10+

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/clinical-scribe.git
cd clinical-scribe
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get your free Groq API key
- Go to: https://console.groq.com
- Sign up → API Keys → Create key
- Copy the key

### 4. Create your `.env` file
Create a file called `.env` in the project folder and add:
```
GROQ_API_KEY=your_groq_key_here
```

> ⚠️ Never share your `.env` file or push it to GitHub. It is already in `.gitignore`.

### 5. Install ffmpeg (required for audio decoding)
- **Ubuntu/Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH

---

## How to run

### Option A — Streamlit browser UI (recommended)
```bash
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501` — upload audio, paste transcript, or summarize patient history.

### Option B — Command line, audio file
```bash
python app.py audio/consultation.mp3
```
Supported formats: `.webm`, `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`

### Option C — Command line, paste transcript
```bash
python app.py --text
```
Paste transcript, type `END` on a new line, press Enter.

### Option D — Test note generation only (uses built-in mock transcript)
```bash
python generate_note.py
```

### Option E — Test patient history summary
```bash
python summarize_history.py
```

---

## Project structure

```
clinical-scribe/
├── streamlit_app.py     ← Browser UI (run this for demo)
├── app.py               ← Command-line pipeline
├── transcribe.py        ← Step 1: Audio → Transcript (Whisper)
├── generate_note.py     ← Step 2: Transcript → SOAP Note (Groq)
├── summarize_history.py ← Step 3: Past records → Patient briefing (Groq)
├── requirements.txt     ← Python dependencies
├── .env                 ← Your API key (never share or commit this)
├── .gitignore           ← Ensures .env is never pushed
├── audio/               ← Put your audio files here
├── transcripts/         ← Saved transcripts appear here
└── notes/               ← Saved SOAP notes (JSON) appear here
```

---

## Output

Each run produces:

**SOAP Note** (`notes/<name>_soap_note.json`):
- Subjective / Objective / Assessment / Plan
- Confidence score per section (HIGH / MEDIUM / LOW)
- Anomaly flags with severity levels
- Hindi patient summary
- Timestamp and disclaimer metadata

**Patient History Summary** (`notes/<name>_summary.json`):
- One-line doctor briefing
- Known conditions, medications, allergies
- Critical flags (e.g. documented drug allergies)
- Recent visit summary
- Abnormal findings

---

## Responsible AI

This system is built with responsible AI principles:

- **Human control:** Every note requires physician review and sign-off before saving. The AI is an assistant, not a decision-maker.
- **Transparency:** Every generated field shows a confidence score. LOW confidence sections are visually highlighted.
- **No hallucination by design:** The prompt explicitly instructs the model to write `[Not mentioned]` rather than infer or guess missing information.
- **Privacy:** No patient data is stored on external servers. Groq API calls use the transcript only — no patient identifiers.
- **Clear labelling:** Prescription drafts are explicitly labelled "SIMULATION ONLY — NOT FOR CLINICAL USE".

---

## Sample output

Given a Hindi-English consultation where a doctor prescribes Amoxicillin to a patient with documented penicillin allergy, the system generates:

```
🚨 ANOMALY FLAGS
  [HIGH] Amoxicillin prescribed to penicillin-allergic patient
         Reason: Amoxicillin is a penicillin-type antibiotic. Cross-reactivity
                 risk. Prescribing doctor must review immediately.
```

---

## Disclaimer

> This system is for **research and demonstration purposes only**.
> All AI-generated notes must be reviewed, edited, and approved by a licensed physician before any clinical use.
> This tool does not constitute medical advice and must not be used for actual patient care without appropriate clinical oversight.
