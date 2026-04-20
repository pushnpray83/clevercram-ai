import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.title("📚 CleverCram AI")

notes = st.text_area("Paste your notes here:")

mode = st.selectbox(
    "Choose Study Mode:",
    ["Summary", "Flashcards", "Quiz", "Cram Mode"]
)

if st.button("Generate"):
    if not notes.strip():
        st.warning("Please add notes first.")
    else:
        prompt = f"""
        You are CleverCram AI, a study assistant.

        Convert the following notes into: {mode}

        Keep it clear, structured, and exam-focused.

        Notes:
        {notes}
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        st.write(response.text)