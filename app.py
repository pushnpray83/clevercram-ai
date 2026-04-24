import streamlit as st
import os
import time
from dotenv import load_dotenv
from groq import Groq

# ---------------- LOAD ENV ----------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CleverCram AI",
    page_icon="📚",
    layout="centered"
)

# ---------------- DARK THEME (CUSTOM CSS) ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #0b0f19;
    color: #e5e7eb;
}

/* Main title */
h1 {
    color: #ffffff;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* Subtext */
.stCaption {
    color: #9ca3af;
}

/* Text area */
textarea {
    background-color: #111827 !important;
    color: #e5e7eb !important;
    border: 1px solid #1f2937 !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton button {
    background-color: #1f2937;
    color: white;
    border-radius: 8px;
    border: 1px solid #374151;
    transition: 0.2s;
}

.stButton button:hover {
    background-color: #374151;
    border-color: #4b5563;
}

/* Select box */
div[data-baseweb="select"] > div {
    background-color: #111827;
    color: white;
    border-radius: 8px;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #111827;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📚 CleverCram AI")
st.caption("Minimal AI study tool — summaries, flashcards, and cram sheets")

# ---------------- SAFETY CHECK ----------------
def safety_check(text):
    blocked = ["password", "credit card", "ssn", "bank account"]
    return not any(word in text.lower() for word in blocked)

# ---------------- PROMPTS ----------------
def build_prompt(notes, mode):

    if mode == "Summary":
        return f"Summarise into bullet points:\n\n{notes}"

    elif mode == "Flashcards":
        return f"""
Create 5 flashcards.

Format:
Q: ...
A: ...

Notes:
{notes}
"""

    elif mode == "Cram Mode":
        return f"""
Create a short revision cheat sheet.

Notes:
{notes}
"""

# ---------------- GENERATE ----------------
def generate(prompt):
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )
        return chat.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- INPUT ----------------
notes = st.text_area("Paste your notes here:")

mode = st.selectbox("Choose Study Mode:", ["Summary", "Flashcards", "Cram Mode"])

# ---------------- RUN ----------------
if st.button("Generate"):

    if not notes.strip():
        st.warning("Please paste notes first.")

    elif not api_key:
        st.error("Missing GROQ_API_KEY")

    elif not safety_check(notes):
        st.error("Blocked due to unsafe input.")

    else:
        start = time.time()

        output = generate(build_prompt(notes, mode))

        end = time.time()

        st.success("Done!")
        st.caption(f"Response time: {round(end - start, 2)}s")

        # ---------------- OUTPUT ----------------
        if mode == "Summary":
            st.write(output)

        elif mode == "Flashcards":
            st.subheader("🧠 Flashcards")

            cards = output.split("Q:")

            for i, card in enumerate(cards):
                if card.strip():
                    parts = card.split("A:")

                    q = parts[0].strip()
                    a = parts[1].strip() if len(parts) > 1 else ""

                    with st.expander(f"Flashcard {i+1}"):
                        st.markdown(f"**Q:** {q}")
                        st.markdown("---")
                        st.markdown(f"**A:** {a}")

        elif mode == "Cram Mode":
            st.subheader("⚡ Cram Sheet")
            st.write(output)