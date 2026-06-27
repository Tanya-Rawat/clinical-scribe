# -------------------------------------------------------
# STEP 2: generate_note.py
# Takes a transcript and generates a structured SOAP note
# Using Groq API (free, fast, no daily quota issues)
# -------------------------------------------------------

from groq import Groq
import os
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

# Load API key from .env file
load_dotenv()


def setup_groq():
    """Loads the Groq API key and configures the client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print(Fore.RED + "[ERROR] Groq API key not found.")
        print(Fore.YELLOW + "→ Open the .env file and paste your key.")
        print(Fore.YELLOW + "→ Get a free key at: https://console.groq.com")
        raise ValueError("Missing GROQ_API_KEY in .env file")
    return Groq(api_key=api_key)


# ── The prompt is the most important part of this entire system ───────────────
# This is called "prompt engineering" - how you instruct the AI matters
# enormously. Study this carefully and experiment with changes.

SOAP_PROMPT_TEMPLATE = """
You are an expert clinical documentation assistant helping doctors in India 
generate structured medical notes. Your role is to assist - the doctor will 
always review and approve the final note.

TRANSCRIPT OF DOCTOR-PATIENT CONSULTATION:
\"\"\"
{transcript}
\"\"\"

INSTRUCTIONS:
1. Extract information ONLY from the transcript above. Do NOT invent or assume 
   any medical details not explicitly stated.
2. If a field cannot be determined from the transcript, write [Not mentioned].
3. The consultation may be in Hindi, English, or mixed (Hinglish). 
   Understand all and write the note in professional English.
4. Flag anything that seems clinically concerning under ANOMALIES.
5. Mark your confidence for each section: HIGH / MEDIUM / LOW.

Generate a structured SOAP note in the following JSON format:

{{
  "soap_note": {{
    "subjective": {{
      "chief_complaint": "Main reason patient visited (patient's own words)",
      "history_of_present_illness": "Duration, character, severity of symptoms",
      "past_medical_history": "Previous conditions, surgeries, hospitalizations",
      "medications": "Current medications patient is taking",
      "allergies": "Known allergies",
      "confidence": "HIGH/MEDIUM/LOW"
    }},
    "objective": {{
      "vitals": "Temperature, BP, pulse, SpO2 if mentioned",
      "physical_examination": "Examination findings mentioned by doctor",
      "investigations": "Lab results, X-ray, reports mentioned",
      "confidence": "HIGH/MEDIUM/LOW"
    }},
    "assessment": {{
      "diagnosis": "Doctor's working diagnosis or differential",
      "reasoning": "Clinical reasoning if mentioned",
      "confidence": "HIGH/MEDIUM/LOW"
    }},
    "plan": {{
      "medications_prescribed": "Drug name, dose, frequency, duration",
      "investigations_ordered": "Tests ordered",
      "referrals": "Any specialist referrals",
      "follow_up": "Follow-up instructions",
      "patient_education": "Advice given to patient",
      "confidence": "HIGH/MEDIUM/LOW"
    }}
  }},
  "anomaly_flags": [
    {{
      "flag": "Description of concern",
      "severity": "HIGH/MEDIUM/LOW",
      "reason": "Why this is flagged"
    }}
  ],
  "summary_in_hindi": "2-3 sentence plain language summary for patient in Hindi",
  "metadata": {{
    "language_detected": "Primary language of consultation",
    "note_generated_at": "auto",
    "disclaimer": "AI-generated draft. Must be reviewed and approved by the treating physician."
  }}
}}

Return ONLY valid JSON. No explanation text outside the JSON.
"""


def generate_soap_note(transcript: str) -> dict:
    """
    Sends transcript to Groq and returns a structured SOAP note.

    Args:
        transcript: Raw text transcript of the consultation

    Returns:
        Dictionary containing the parsed SOAP note and anomaly flags
    """

    if not transcript or len(transcript.strip()) < 20:
        print(Fore.RED + "[ERROR] Transcript is too short or empty.")
        raise ValueError("Invalid transcript provided")

    print(Fore.CYAN + "\n🤖 Sending transcript to Groq (llama-3.3-70b) for SOAP note generation...")

    client = setup_groq()

    # Build the prompt by inserting the transcript
    prompt = SOAP_PROMPT_TEMPLATE.format(transcript=transcript)

    # ── Call the LLM ──────────────────────────────────────────────────────────
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw_output = response.choices[0].message.content.strip()
    except Exception as e:
        print(Fore.RED + f"[ERROR] Groq API call failed: {e}")
        raise

    # ── Parse JSON response ───────────────────────────────────────────────────
    # Strip markdown code fences if model wraps output in ```json ... ```
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    try:
        note_data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(Fore.RED + f"[ERROR] Could not parse LLM response as JSON: {e}")
        print(Fore.YELLOW + "Raw response was:")
        print(raw_output)
        raise

    # Add timestamp
    note_data["metadata"]["note_generated_at"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(Fore.GREEN + "✅ SOAP note generated successfully.")
    return note_data


def display_note(note_data: dict):
    """Prints the SOAP note in a readable format in the terminal."""
    soap = note_data.get("soap_note", {})
    flags = note_data.get("anomaly_flags", [])
    hindi_summary = note_data.get("summary_in_hindi", "")

    print("\n" + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "           CLINICAL SCRIBE — SOAP NOTE DRAFT")
    print(Fore.YELLOW + "    ⚠️  AI-generated. Doctor must review before use.")
    print("=" * 60)

    # Subjective
    subj = soap.get("subjective", {})
    print(Fore.CYAN + "\n📋 SUBJECTIVE")
    print(f"  Chief Complaint   : {subj.get('chief_complaint', '[Not mentioned]')}")
    print(f"  History           : {subj.get('history_of_present_illness', '[Not mentioned]')}")
    print(f"  Past History      : {subj.get('past_medical_history', '[Not mentioned]')}")
    print(f"  Medications       : {subj.get('medications', '[Not mentioned]')}")
    print(f"  Allergies         : {subj.get('allergies', '[Not mentioned]')}")
    print(Fore.YELLOW + f"  Confidence        : {subj.get('confidence', '?')}")

    # Objective
    obj = soap.get("objective", {})
    print(Fore.CYAN + "\n🔬 OBJECTIVE")
    print(f"  Vitals            : {obj.get('vitals', '[Not mentioned]')}")
    print(f"  Examination       : {obj.get('physical_examination', '[Not mentioned]')}")
    print(f"  Investigations    : {obj.get('investigations', '[Not mentioned]')}")
    print(Fore.YELLOW + f"  Confidence        : {obj.get('confidence', '?')}")

    # Assessment
    assess = soap.get("assessment", {})
    print(Fore.CYAN + "\n🩺 ASSESSMENT")
    print(f"  Diagnosis         : {assess.get('diagnosis', '[Not mentioned]')}")
    print(f"  Reasoning         : {assess.get('reasoning', '[Not mentioned]')}")
    print(Fore.YELLOW + f"  Confidence        : {assess.get('confidence', '?')}")

    # Plan
    plan = soap.get("plan", {})
    print(Fore.CYAN + "\n💊 PLAN")
    print(f"  Medications       : {plan.get('medications_prescribed', '[Not mentioned]')}")
    print(f"  Tests Ordered     : {plan.get('investigations_ordered', '[Not mentioned]')}")
    print(f"  Referrals         : {plan.get('referrals', '[Not mentioned]')}")
    print(f"  Follow-up         : {plan.get('follow_up', '[Not mentioned]')}")
    print(f"  Patient Education : {plan.get('patient_education', '[Not mentioned]')}")
    print(Fore.YELLOW + f"  Confidence        : {plan.get('confidence', '?')}")

    # Anomaly flags
    if flags:
        print(Fore.RED + "\n🚨 ANOMALY FLAGS")
        for flag in flags:
            severity = flag.get("severity", "?")
            color = Fore.RED if severity == "HIGH" else Fore.YELLOW
            print(color + f"  [{severity}] {flag.get('flag', '')}")
            print(f"         Reason: {flag.get('reason', '')}")
    else:
        print(Fore.GREEN + "\n✅ No anomalies flagged.")

    # Hindi summary
    if hindi_summary:
        print(Fore.CYAN + "\n🇮🇳 PATIENT SUMMARY (Hindi)")
        print(f"  {hindi_summary}")

    print("\n" + "=" * 60)
    print(Fore.YELLOW + "  ⚠️  This is an AI-generated draft.")
    print(Fore.YELLOW + "  Treating physician must review, edit, and sign off.")
    print("=" * 60 + "\n")


def save_note(note_data: dict, base_name: str):
    """Saves the SOAP note as a JSON file."""
    os.makedirs("notes", exist_ok=True)
    output_path = f"notes/{base_name}_soap_note.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(note_data, f, indent=2, ensure_ascii=False)
    print(Fore.GREEN + f"💾 Note saved to: {output_path}")
    return output_path


# ── Run directly for quick testing ───────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(Fore.YELLOW + "No transcript file provided. Running with mock transcript...")
        test_transcript = """
        Doctor: Good morning, what brings you in today?
        Patient: Doctor sahab, 3 din se bukhar hai. Bahut zyada thakan bhi ho rahi hai.
        Doctor: Okay. Temperature kitna tha?
        Patient: Ghar pe check kiya tha, 102 tha.
        Doctor: Koi khansi ya gale mein kharash?
        Patient: Haan, thodi si khansi hai.
        Doctor: Koi purani beemari hai? Koi dawai le rahe hain abhi?
        Patient: Nahi doctor, kuch nahi. Haan, penicillin se allergy hai mujhe.
        Doctor: Okay noted. Let me check. Throat looks red, mild inflammation.
        BP is 118/76, temperature 101.4F now. Looks like viral fever with pharyngitis.
        I'll prescribe paracetamol 500mg twice a day for 3 days and a throat lozenge.
        Drink plenty of fluids. Come back in 3 days if not improving.
        """
        note = generate_soap_note(test_transcript)
        display_note(note)
        save_note(note, "mock_test")
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            transcript = f.read()
        note = generate_soap_note(transcript)
        display_note(note)
        base = os.path.splitext(os.path.basename(sys.argv[1]))[0]
        save_note(note, base)