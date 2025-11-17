import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import PyPDF2

# -------------------------
# LANGUAGE SUPPORT
# -------------------------
LANG_CODES = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es"
}

# -------------------------
# FUNCTIONS
# -------------------------

# Extract text from PDF
def extract_pdf_text(uploaded_file):
    text = ""
    reader = PyPDF2.PdfReader(uploaded_file)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text


# Summarize text locally
def summarize_text(text, sentence_count=6):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, sentence_count)

    result = "📌 **Summary:**\n\n"
    for sentence in summary:
        result += f"• {sentence}\n\n"

    return result


# Translation
def translate_text(text, lang):
    try:
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except:
        return text


# Text-to-Speech
def text_to_speech(text, lang_code="en", filename="output.mp3"):
    clean_text = text.replace("•", "")
    tts = gTTS(text=clean_text, lang=lang_code)
    tts.save(filename)
    return filename


# -------------------------
# UI
# -------------------------

st.title("✨ EchoAssist Offline Edition")
st.write("No API required. Local PDF summarization + Text-to-Speech built in.")

mode = st.selectbox(
    "Choose a feature:",
    ["📄 PDF Summarizer", "🔊 Text → Translate → Speech"]
)


# -------------------------
# MODE 1 → PDF SUMMARIZER
# -------------------------
if mode == "📄 PDF Summarizer":
    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf and st.button("📚 Summarize PDF"):
        st.info("⏳ Extracting & summarizing text...")

        full_text = extract_pdf_text(pdf)

        if len(full_text.strip()) < 50:
            st.error("⚠ Not enough readable text in PDF.")
        else:
            summary = summarize_text(full_text)

            st.subheader("📌 Summary Output:")
            st.write(summary)

            st.download_button(
                label="💾 Download Summary",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )


# -------------------------
# MODE 2 → TEXT TO SPEECH
# -------------------------
elif mode == "🔊 Text → Translate → Speech":
    target_lang = st.selectbox("Select output language:", list(LANG_CODES.keys()))
    lang_code = LANG_CODES[target_lang]

    text_input = st.text_area("Enter text:")

    if st.button("▶ Convert"):
        if not text_input.strip():
            st.warning("⚠ Please enter text.")
        else:
            translated = translate_text(text_input, lang_code)

            st.subheader("📝 Translation:")
            st.write(translated)

            audio = text_to_speech(translated, lang_code)
            st.audio(audio)
