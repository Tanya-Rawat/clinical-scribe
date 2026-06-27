# -------------------------------------------------------
# STEP 1: transcribe.py
# Takes an audio file and converts it to text using Whisper
# Supports English, Hindi, and mixed language (code-switching)
# -------------------------------------------------------

import whisper
import os
import sys
from colorama import Fore, Style, init

init(autoreset=True)  # Makes colored terminal output work on all platforms


def transcribe_audio(audio_file_path: str) -> dict:
    """
    Transcribes an audio file using OpenAI Whisper.

    Args:
        audio_file_path: Path to the audio file (.mp3, .wav, .m4a, .ogg etc.)

    Returns:
        A dictionary with:
            - 'text'     : Full transcript as a string
            - 'language' : Detected language code (e.g. 'hi', 'en')
            - 'segments' : List of timestamped segments (useful for debugging)
    """

    # ── Validate file exists ──────────────────────────────────────────────────
    if not os.path.exists(audio_file_path):
        print(Fore.RED + f"[ERROR] File not found: {audio_file_path}")
        sys.exit(1)

    print(Fore.CYAN + f"\n🎙️  Loading audio file: {audio_file_path}")

    # ── Load Whisper model ────────────────────────────────────────────────────
    # Model size options (trade-off between speed and accuracy):
    #   "tiny"   → fastest, least accurate  (good for testing)
    #   "base"   → fast, decent accuracy    (good for development)
    #   "small"  → balanced                 (recommended for Hindi)
    #   "medium" → more accurate, slower    (good for production)
    #   "large"  → most accurate, slowest   (best for deployment)
    #
    # START with "base" while developing. Switch to "small" or "medium"
    # when testing Hindi/mixed language accuracy.

    print(Fore.YELLOW + "⏳ Loading Whisper model (this may take a moment the first time)...")
    model = whisper.load_model("base")
    print(Fore.GREEN + "✅ Whisper model loaded.")

    # ── Transcribe ────────────────────────────────────────────────────────────
    # Setting language=None lets Whisper auto-detect the language.
    # For faster processing when you KNOW the language, set:
    #   language="hi"  for Hindi
    #   language="en"  for English
    # Leave as None for mixed-language (code-switching) consultations.

    print(Fore.YELLOW + "⏳ Transcribing audio...")
    result = model.transcribe(
        audio_file_path,
        language=None,          # Auto-detect language
        task="transcribe",      # Use "translate" to force output in English
        verbose=False
    )

    detected_language = result.get("language", "unknown")
    full_text = result["text"].strip()

    print(Fore.GREEN + f"✅ Transcription complete.")
    print(Fore.CYAN + f"🌐 Detected language: {detected_language.upper()}")
    print(Fore.WHITE + "\n--- RAW TRANSCRIPT ---")
    print(full_text)
    print(Fore.WHITE + "----------------------\n")

    # ── Save transcript to file ───────────────────────────────────────────────
    os.makedirs("transcripts", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
    output_path = f"transcripts/{base_name}_transcript.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Detected Language: {detected_language}\n")
        f.write(f"Audio File: {audio_file_path}\n")
        f.write("=" * 50 + "\n")
        f.write(full_text)

    print(Fore.GREEN + f"💾 Transcript saved to: {output_path}")

    return {
        "text": full_text,
        "language": detected_language,
        "segments": result.get("segments", []),
        "saved_to": output_path
    }


# ── Run directly for quick testing ───────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(Fore.RED + "Usage: python transcribe.py <path_to_audio_file>")
        print(Fore.YELLOW + "Example: python transcribe.py audio/consultation1.mp3")
        sys.exit(1)

    result = transcribe_audio(sys.argv[1])
    print(Fore.CYAN + f"\n📊 Stats:")
    print(f"  Words transcribed : {len(result['text'].split())}")
    print(f"  Language detected : {result['language']}")
    print(f"  Segments found    : {len(result['segments'])}")
