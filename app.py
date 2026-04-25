import streamlit as st
import os
import time
from dotenv import load_dotenv
from groq import Groq

# ---------------- LOAD ENV ----------------
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CleverCram AI",
    page_icon="📚",
    layout="centered"
)

# ---------------- CLIENT ----------------
client = None
if api_key:
    client = Groq(api_key=api_key)

# ---------------- DARK THEME ----------------
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

/* Caption */
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
st.caption("Turn notes into summaries, flashcards, and cram sheets instantly.")

# ---------------- SAFETY CHECK ----------------
def safety_check(text):
    blocked = ["password", "credit card", "ssn", "bank account"]
    return not any(word in text.lower() for word in blocked)

# ---------------- PROMPTS ----------------
def build_prompt(notes, mode):

    if mode == "Summary":
        return f"""
Summarise these notes into clean bullet points.
Keep it clear, concise, and accurate.

Notes:
{notes}
"""

    elif mode == "Flashcards":
        return f"""
Create exactly 5 study flashcards.

Format:
Q: question
A: answer

Keep answers short and useful.

Notes:
{notes}
"""

    elif mode == "Cram Mode":
        return f"""
Turn these notes into a last-minute exam cheat sheet.
Use short bullet points only.

Notes:
{notes}
"""

# ---------------- GENERATE ----------------
def generate(prompt):
    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful academic study assistant. Be concise, clear and accurate."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=800
        )

        return chat.choices[0].message.content.strip()

    except Exception:
        return None

# ---------------- INPUT ----------------
notes = st.text_area(
    "Paste your notes here:",
    height=220,
    placeholder="Paste class notes, textbook paragraphs, revision content..."
)

mode = st.selectbox(
    "Choose Study Mode:",
    ["Summary", "Flashcards", "Cram Mode"]
)

# ---------------- RUN ----------------
if st.button("Generate"):

    notes = notes.strip()

    # Validation
    if not notes:
        st.warning("Please paste notes first.")

    elif not api_key:
        st.error("Missing GROQ_API_KEY in .env file.")

    elif len(notes) > 5000:
        st.error("Notes too long. Please shorten your input.")

    elif not safety_check(notes):
        st.error("Input blocked due to unsafe content.")

    else:
        start = time.time()

        with st.spinner("Generating..."):
            output = generate(build_prompt(notes, mode))

        end = time.time()

        if not output:
            st.error("AI service temporarily unavailable. Please try again later.")

        else:
            st.success("Done!")
            st.caption(f"Response time: {round(end - start, 2)}s")

            # ---------------- OUTPUT ----------------
            if mode == "Summary":
                st.subheader("📝 Summary")
                st.write(output)

            elif mode == "Flashcards":
                st.subheader("🧠 Flashcards")

                cards = output.split("Q:")

                count = 1
                for card in cards:
                    if card.strip():

                        parts = card.split("A:")
                        question = parts[0].strip()
                        answer = parts[1].strip() if len(parts) > 1 else "No answer generated."

                        with st.expander(f"Flashcard {count}"):
                            st.markdown(f"**Q:** {question}")
                            st.markdown("---")
                            st.markdown(f"**A:** {answer}")

                        count += 1

            elif mode == "Cram Mode":
                st.subheader("⚡ Cram Sheet")
                st.write(output)