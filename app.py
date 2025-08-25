import streamlit as st
from PIL import Image
import numpy as np
import easyocr

st.set_page_config(page_title="SUG Helper", page_icon="📸", layout="centered")

TEMPLATES = {
    "Sexual": {"risk":"Non-violation with Risky Video Cover","policy":"Explicit sexual expression",
        "reasoning":"The video cover/captions include sexualized phrasing ({keywords}). Content focuses on sexualized body language; no explicit nudity. Classified under Explicit sexual expression per SOP.",
        "context":"No minors nor graphic sexual acts detected. Assessment is based on captions and poses."},
    "Violence": {"risk":"Contextual Violation","policy":"Violent",
        "reasoning":"The content includes indications of violence ({keywords}). Content implies harm/injury; classified under Violent policy per SOP.",
        "context":"No graphic gore observed; decision based on violent cues in text/thumbnail."},
    "Non-Violation": {"risk":"Non-Violation","policy":"Non-Risky",
        "reasoning":"No policy-relevant risk indicators detected. Captions/cover show benign content ({keywords}).",
        "context":"No sexual, violent, hateful, or other restricted signals."},
    "Hate": {"risk":"Contextual Violation","policy":"Hateful / Derogatory",
        "reasoning":"Captions/covers contain derogatory or hateful phrasing ({keywords}). Classified under Hateful/Derogatory policy.",
        "context":"Assessment based on visible hateful language; no sexual context."},
    "Drugs": {"risk":"Contextual Violation","policy":"Drugs & Controlled substances",
        "reasoning":"Content includes references to drugs or controlled substances ({keywords}). Classified under Drugs policy.",
        "context":"No minors observed; assessment based on drug-related text cues."},
    "Self-harm": {"risk":"Contextual Violation","policy":"Suicide & Self-harm",
        "reasoning":"Content suggests self-harm or suicidal behavior ({keywords}). Classified under Self-harm policy.",
        "context":"Assessment based on text/imagery cues suggesting self-harm."}
}

KEYWORDS = {
    "Sexual":["sex","ass","sat on his face","booty","nudes","onlyfans","kiss","nsfw"],
    "Violence":["fight","hit","punch","kill","blood","knife","shoot","attack"],
    "Hate":["slur","racist","hate","nazi","faggot","bitch","retard","stupid"],
    "Drugs":["weed","cocaine","heroin","ecstasy","mdma","meth","drug","smoke"],
    "Self-harm":["suicide","cut","kill myself","end it","jump","hang","self harm"]
}

st.title("📸 SUG Helper – Auto Classification")
st.write("Upload screenshot → OCR → suggested Risk Type, Policy, Reasoning, Context")

uploaded = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg","jpeg","png"])
col_flags = st.columns(2)
with col_flags[0]: minors = st.toggle("Potential minors", value=False)
with col_flags[1]: gore = st.toggle("Graphic gore", value=False)

def copy_box(label, text):
    st.text_area(label, text, height=120, key=f"ta_{label}", help="Long-press to copy on phone")
    st.button(f"📋 Copy {label}", key=f"btn_{label}")

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Uploaded screenshot", use_container_width=True)

    # --- OCR: EASYOCR (BRAK pytesseract) ---
    st.caption("Extracting text with EasyOCR… (first run may take longer)")
    reader = easyocr.Reader(["en"], gpu=False)
    result = reader.readtext(np.array(img))
    text = " ".join([t[1] for t in result]).lower()

    st.subheader("Extracted Text (OCR)")
    st.write(text if text.strip() else "_(no text found)_")

    # --- Kategoryzacja ---
    matched = "Non-Violation"; found = []
    for cat, words in KEYWORDS.items():
        for w in words:
            if w in text:
                matched = cat; found.append(w)

    risk = "Contextual Violation" if (minors or gore) else TEMPLATES[matched]["risk"]
    found_str = ", ".join(sorted(set(found))) if found else "no sensitive cues"
    tpl = TEMPLATES[matched]

    st.subheader("Classification Result")
    st.markdown(f"**Detected Category:** {matched}")
    st.markdown(f"**Risk Type:** {risk}")
    st.markdown(f"**Policy:** {tpl['policy']}")

    reasoning = tpl["reasoning"].format(keywords=found_str)
    context = ""
    if minors: context += "Potential minors observed. Escalate per SOP. "
    if gore: context += "Graphic gore present. Escalate per SOP. "
    if not context: context = tpl["context"]

    copy_box("Reasoning", reasoning)
    copy_box("Context", context)
else:
    st.info("Upload a screenshot to start.")
