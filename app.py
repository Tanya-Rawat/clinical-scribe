import streamlit as st
import tempfile
import os
import json
from transcribe import transcribe_audio
from generate_note import generate_soap_note

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Clinical Scribe",
    page_icon="🏥",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a1628; }
    .stApp { background-color: #0a1628; color: #ffffff; }
    .soap-box {
        background-color: #112240;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #028090;
    }
    .flag-box {
        background-color: #2d1515;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #e63946;
    }
    .hindi-box {
        background-color: #112240;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #02c39a;
    }
    .confidence-HIGH   { color: #02c39a; font-weight: bold; }
    .confidence-MEDIUM { color: #f4a261; font-weight: bold; }
    .confidence-LOW    { color: #e63946; font-weight: bold; }
    .disclaimer {
        background-color: #2d2200;
        border: 1px solid #f4a261;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        font-size: 13px;
        color: #f4a261;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🏥 Clinical Scribe")
st.markdown("**AI-powered documentation assistant** · English · Hindi · Hinglish")
st.markdown('<div class="disclaimer">⚠️ FOR RESEARCH & DEMO USE ONLY. All AI-generated notes must be reviewed and approved by a licensed physician before any clinical use.</div>', unsafe_allow_html=True)
st.divider()

# ── Input mode tabs ───────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎙️ Upload Audio", "📝 Paste Transcript"])

with tab1:
    st.markdown("### Upload consultation audio")
    st.caption("Supported formats: .webm, .mp3, .wav, .m4a, .ogg, .flac")
    audio_file = st.file_uploader("Choose audio file", type=["webm","mp3","wav","m4a","ogg","flac"], label_visibility="collapsed")

    if audio_file:
        st.audio(audio_file)
        if st.button("▶ Generate SOAP Note", type="primary", key="audio_btn", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp:
                tmp.write(audio_file.read())
                tmp_path = tmp.name

            with st.spinner("Step 1/2 — Transcribing audio (this takes ~30 seconds)..."):
                try:
                    result = transcribe_audio(tmp_path)
                    transcript = result["text"]
                    lang = result["language"].upper()
                    st.session_state["transcript"] = transcript
                    st.session_state["lang"] = lang
                except Exception as e:
                    st.error(f"Transcription failed: {e}")
                    st.stop()
                finally:
                    os.unlink(tmp_path)

            with st.spinner("Step 2/2 — Generating SOAP note..."):
                try:
                    note = generate_soap_note(transcript)
                    st.session_state["note"] = note
                except Exception as e:
                    st.error(f"Note generation failed: {e}")
                    st.stop()

            st.success("✅ Done!")
            st.rerun()

with tab2:
    st.markdown("### Paste consultation transcript")
    st.caption("Type or paste the conversation below. Hindi, English, or mixed all work.")
    transcript_input = st.text_area("Transcript", height=200, placeholder="Doctor: What brings you in today?\nPatient: Doctor sahab, teen din se bukhar hai...", label_visibility="collapsed")

    if st.button("▶ Generate SOAP Note", type="primary", key="text_btn", use_container_width=True):
        if len(transcript_input.strip()) < 20:
            st.warning("Please enter a longer transcript.")
        else:
            with st.spinner("Generating SOAP note..."):
                try:
                    note = generate_soap_note(transcript_input)
                    st.session_state["note"] = note
                    st.session_state["transcript"] = transcript_input
                    st.session_state["lang"] = "MIXED"
                except Exception as e:
                    st.error(f"Note generation failed: {e}")
                    st.stop()
            st.success("✅ Done!")
            st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
if "note" in st.session_state:
    note = st.session_state["note"]
    transcript = st.session_state.get("transcript", "")
    lang = st.session_state.get("lang", "")
    soap = note.get("soap_note", {})
    flags = note.get("anomaly_flags", [])
    hindi_summary = note.get("summary_in_hindi", "")

    st.divider()

    # Anomaly flags — show at top if any exist
    if flags:
        st.markdown("### 🚨 Anomaly Flags")
        for flag in flags:
            severity = flag.get("severity", "LOW")
            icon = "🔴" if severity == "HIGH" else "🟡"
            st.markdown(f'<div class="flag-box">{icon} <strong>[{severity}]</strong> {flag.get("flag","")}<br><small>{flag.get("reason","")}</small></div>', unsafe_allow_html=True)
    else:
        st.success("✅ No anomalies flagged")

    st.markdown("### 📋 SOAP Note")

    col1, col2 = st.columns(2)

    with col1:
        # Subjective
        subj = soap.get("subjective", {})
        conf = subj.get("confidence", "LOW")
        st.markdown(f'<div class="soap-box"><strong>📋 SUBJECTIVE</strong> &nbsp; <span class="confidence-{conf}">● {conf} confidence</span><br><br>'
            f'<strong>Chief Complaint:</strong> {subj.get("chief_complaint","[Not mentioned]")}<br><br>'
            f'<strong>History:</strong> {subj.get("history_of_present_illness","[Not mentioned]")}<br><br>'
            f'<strong>Past History:</strong> {subj.get("past_medical_history","[Not mentioned]")}<br><br>'
            f'<strong>Medications:</strong> {subj.get("medications","[Not mentioned]")}<br><br>'
            f'<strong>Allergies:</strong> {subj.get("allergies","[Not mentioned]")}</div>', unsafe_allow_html=True)

        # Assessment
        assess = soap.get("assessment", {})
        conf = assess.get("confidence", "LOW")
        st.markdown(f'<div class="soap-box"><strong>🩺 ASSESSMENT</strong> &nbsp; <span class="confidence-{conf}">● {conf} confidence</span><br><br>'
            f'<strong>Diagnosis:</strong> {assess.get("diagnosis","[Not mentioned]")}<br><br>'
            f'<strong>Reasoning:</strong> {assess.get("reasoning","[Not mentioned]")}</div>', unsafe_allow_html=True)

    with col2:
        # Objective
        obj = soap.get("objective", {})
        conf = obj.get("confidence", "LOW")
        st.markdown(f'<div class="soap-box"><strong>🔬 OBJECTIVE</strong> &nbsp; <span class="confidence-{conf}">● {conf} confidence</span><br><br>'
            f'<strong>Vitals:</strong> {obj.get("vitals","[Not mentioned]")}<br><br>'
            f'<strong>Examination:</strong> {obj.get("physical_examination","[Not mentioned]")}<br><br>'
            f'<strong>Investigations:</strong> {obj.get("investigations","[Not mentioned]")}</div>', unsafe_allow_html=True)

        # Plan
        plan = soap.get("plan", {})
        conf = plan.get("confidence", "LOW")
        st.markdown(f'<div class="soap-box"><strong>💊 PLAN</strong> &nbsp; <span class="confidence-{conf}">● {conf} confidence</span><br><br>'
            f'<strong>💊 PRESCRIPTION DRAFT</strong> <em style="color:#e63946;font-size:11px;">— SIMULATION ONLY, NOT FOR CLINICAL USE</em><br>'
            f'{plan.get("medications_prescribed","[Not mentioned]")}<br><br>'
            f'<strong>Tests Ordered:</strong> {plan.get("investigations_ordered","[Not mentioned]")}<br><br>'
            f'<strong>Follow-up:</strong> {plan.get("follow_up","[Not mentioned]")}<br><br>'
            f'<strong>Patient Education:</strong> {plan.get("patient_education","[Not mentioned]")}</div>', unsafe_allow_html=True)

    # Hindi summary
    if hindi_summary:
        st.markdown(f'<div class="hindi-box">🇮🇳 <strong>Patient Summary (Hindi)</strong><br><br>{hindi_summary}</div>', unsafe_allow_html=True)

    # Raw transcript expander
    with st.expander("📄 View raw transcript"):
        st.markdown(f"**Language detected:** {lang}")
        st.text(transcript)

    # Download button
    st.divider()
    st.markdown("### 💾 Save Note")
    note_json = json.dumps(note, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇ Download SOAP Note (JSON)",
        data=note_json,
        file_name="soap_note.json",
        mime="application/json",
        use_container_width=True
    )

    st.markdown('<div class="disclaimer">⚠️ This is an AI-generated draft. The treating physician must review, edit, and sign off before this note is used for any clinical purpose.</div>', unsafe_allow_html=True)