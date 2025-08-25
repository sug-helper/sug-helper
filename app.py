import streamlit as st
from PIL import Image
import numpy as np

# OCR jest opcjonalny – ładujemy tylko gdy użytkownik włączy
def run_easyocr(image):
    import easyocr
    reader = easyocr.Reader(["en"], gpu=False)
    result = reader.readtext(np.array(image))
    return " ".join([t[1] for t in result])

st.set_page_config(page_title="SUG Helper", page_icon="📸", layout="centered")

TEMPLATES = {
    "Sexual": {
        "risk": "Non-violation with Risky Video Cover",
        "policy": "Explicit sexual expression",
        "reasoning": "The video cover/captions include sexualized phrasing ({keywords}). Content focuses on sexualized body language; no explicit nudity. Classified under Explicit sexual expression per SOP.",
        "context": "No minors nor graphic sexual acts detected. Assessment is based on captions and poses."
    },
    "Violence": {
        "risk": "Contextual Violation",
        "policy": "Violent",
        "reasoning": "The content includes indications of violence ({keywords}). Content implies harm/injury; classified under Violent policy per SOP.",
        "context": "No graphic gore observed; decision based on violent cues in text/thumbnail."
    },
    "Non-Violation": {
        "risk": "Non-Violation",
        "policy": "Non-Risky",
        "reasoning": "No policy-relevant risk indicators detected. Captions/cover show benign content ({keywords}).",
        "context": "No sexual, violent, hateful, or other restricted signals."
    },
    "Hate": {
        "risk": "Contextual Violation",
        "policy": "Hateful / Derogatory",
        "reasoning": "Captions/covers contain derogatory or hateful phrasing ({keywords}). Classified under Hateful/Derogatory policy.",
        "context": "Assessment based on visible hateful language; no sexual context."
    },
    "Drugs": {
        "risk": "Contextual Violation",
        "policy": "Drugs & Controlled substances",
        "reasoning": "Content includes references to drugs or controlled substances ({keywords}). Classified under Drugs policy.",
        "context": "No minors observed; assessment based on drug-related text cues."
    },
    "Self-harm": {
        "risk": "Contextual Violation",
        "policy": "Suicide & Self-harm",
        "reasoning": "Content suggests self-harm or suicidal behavior ({keywords}). Classified under Self-harm policy.",
        "context": "Assessment based on text/imagery cues suggesting self-harm."
    }
}

KEYWORDS = {
    "Sexual": ["sex", "ass", "sat on his face", "booty", "nudes", "onlyfans", "kiss", "nsfw"],
    "Violence": ["fight", "hit", "punch", "kill", "blood", "knife", "shoot", "attack"],
    "Hate": ["slur", "racist", "hate", "nazi", "faggot", "bitch", "retard", "stupid"],
    "Drugs": ["weed", "cocaine", "heroin", "ecstasy", "mdma", "meth", "drug", "smoke"],
    "Self-harm": ["suicide", "cut", "kill myself", "end it", "jump", "hang", "self harm"]
}

st.title("📸 SUG Helper – Auto Classification")
st.write("Paste captions (albo użyj OCR), a dostaniesz Risk Type, Policy, Reasoning, Context.")

# --- Wejścia ---
uploaded = st.file_uploader("Opcjonalnie: wrzuć screenshot (JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Uploaded screenshot", use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    minors = st.toggle("Potential minors", value=False)
with col2:
    gore = st.toggle("Graphic gore", value=False)

st.markdown("### Wklej tekst (szybciej i pewniej)")
manual_text = st.text_area(
    "Captions / tekst z ekranu (skopiuj z Google Lens / Microsoft Lens)",
    height=120,
    placeholder="np. 'KAI SAT ON HIS FACE', 'Just two dudes shaking ass' ..."
)

use_ocr = st.checkbox("Próbuj OCR z obrazka (opcjonalne)")

def classify(text):
    text_l = text.lower()
    matched = "Non-Violation"
    found = []
    for cat, words in KEYWORDS.items():
        for w in words:
            if w in text_l:
                matched = cat
                found.append(w)
    risk = "Contextual Violation" if (minors or gore) else TEMPLATES[matched]["risk"]
    found_str = ", ".join(sorted(set(found))) if found else "no sensitive cues"
    tpl = TEMPLATES[matched]
    reasoning = tpl["reasoning"].format(keywords=found_str)
    context = ""
    if minors:
        context += "Potential minors observed. Escalate per SOP. "
    if gore:
        context += "Graphic gore present. Escalate per SOP. "
    if not context:
        context = tpl["context"]
    return matched, risk, tpl["policy"], reasoning, context

# --- Logika: manual first, OCR fallback ---
text_source = ""
if manual_text.strip():
    text_source = manual_text.strip()
elif use_ocr and uploaded:
    with st.spinner("OCR in progress…"):
        try:
            text_source = run_easyocr(img)
        except Exception as e:
            st.error(f"OCR error: {e}")
            text_source = ""

if text_source:
    st.subheader("Extracted / Provided Text")
    st.write(text_source)

    matched, risk, policy, reasoning, context = classify(text_source)

    st.subheader("Classification Result")
    st.markdown(f"**Detected Category:** {matched}")
    st.markdown(f"**Risk Type:** {risk}")
    st.markdown(f"**Policy:** {policy}")
    st.text_area("Reasoning", reasoning, height=120, help="Long-press to copy")
    st.text_area("Context", context, height=120, help="Long-press to copy")
else:
    st.info("Wklej tekst w pole powyżej (najszybciej), albo zaznacz 'Próbuj OCR' i wrzuć obrazek.")
    
