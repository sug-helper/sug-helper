import streamlit as st
from PIL import Image
import pytesseract

# --- Szablony Reasoning/Context ---
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
        "reasoning": "The video includes indications of violence ({keywords}). Content implies harm/injury; classified under Violent policy per SOP.",
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
        "context": "Assessment based on visible hateful language; no minors or sexual context."
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

# --- Słowa-klucze ---
KEYWORDS = {
    "Sexual": ["sex", "ass", "sat on his face", "booty", "nudes", "onlyfans", "kiss", "nsfw"],
    "Violence": ["fight", "hit", "punch", "kill", "blood", "knife", "shoot", "attack"],
    "Hate": ["slur", "racist", "hate", "nazi", "faggot", "bitch", "stupid", "retard"],
    "Drugs": ["weed", "cocaine", "heroin", "ecstasy", "mdma", "meth", "drug", "smoke"],
    "Self-harm": ["suicide", "cut", "kill myself", "end it", "jump", "hang", "self harm"]
}

# --- App UI ---
st.title("📸 SUG Helper – Auto Classification")
st.write("Upload screenshot → get Risk Type, Policy, Reasoning, Context")

uploaded = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded Screenshot", use_column_width=True)

    # OCR
    text = pytesseract.image_to_string(img).lower()
    st.subheader("Extracted Text (OCR)")
    st.write(text)

    # Match category
    matched_category = "Non-Violation"
    found_keywords = []
    for cat, words in KEYWORDS.items():
        for w in words:
            if w in text:
                matched_category = cat
                found_keywords.append(w)

    found_str = ", ".join(set(found_keywords)) if found_keywords else "no sensitive cues"
    template = TEMPLATES[matched_category]

    # Output
    st.subheader("Classification Result")
    st.write(f"**Risk Type:** {template['risk']}")
    st.write(f"**Policy:** {template['policy']}")
    st.write(f"**Reasoning:** {template['reasoning'].format(keywords=found_str)}")
    st.write(f"**Context:** {template['context']}")
  
