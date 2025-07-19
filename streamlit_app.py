# realtime_chatbot_streamlit.py
import multiprocessing
multiprocessing.freeze_support()

import streamlit as st
import time
import cohere
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, GTTSEngine
from datetime import datetime


# ----------- Interface preparing---------- #
st.set_page_config(page_title="مساعد صوتي فوري")
st.title("🎙️ المساعد الصوتي - Realtime")

col1, col2, col3 = st.columns(3)

with col1:
    start_button = st.empty()

with col2:
    placeholder = st.empty()

with col3:  
    chat_placeholder = st.empty()

# ----------- session state ---------- #
if "recorder" not in st.session_state:
    st.session_state.recorder = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "response" not in st.session_state:
    st.session_state.response = ""

# ----------- Models ---------- #
co = cohere.Client('l95LmZoflNOyfEFQqBtWyMNPjrLKKprp9JtmHh0k')

tts_engine = GTTSEngine(voice="ar")
audio_stream = TextToAudioStream(tts_engine)


# ----------- functions ---------- #
def log_user_question(question: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("user_questions_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {question}\n")


def render_chat():
    chat_content = "### 🗨️ سجل المحادثة\n\n"
    for msg in st.session_state.chat_history:
        role = "🧑‍🦱 أنت" if msg["role"] == "USER" else "🤖 المساعد"
        chat_content += f"**{role}:** {msg['message']}\n\n"
    chat_placeholder.markdown(chat_content) 


def start_recording():
    while True:
        placeholder.text("جاري الاعداد، الرجاء الانتظار...")
        st.session_state.recorder = AudioToTextRecorder(language='ar')
        st.session_state.recorder.start()
        placeholder.text("بدأ التسجيل لمدة 7 ثوان")
        time.sleep(7)
        placeholder.text("انتهى التسجيل، جاري تنفيذ الطلب...")
        st.session_state.recorder.stop()
        query = st.session_state.recorder.text()
        st.session_state.transcript = query
        log_user_question(query)

        if not query:
            st.warning("لم يتم فهم أي كلام")
            return

        st.session_state.chat_history.append({"role": "USER", "message": query})

        result = co.chat(
            message=query, 
            chat_history=st.session_state.chat_history,
            model="command-r7b-12-2024",
            preamble="You are a helpful AI assistant. Always answer with less than 15 words."
        )
        response = result.text
        st.session_state.response = response

        st.session_state.chat_history.append({"role": "CHATBOT", "message": response})

        render_chat()

        audio_stream.feed(response)
        placeholder.text("تم الرد بنجاح!")
        audio_stream.play()


# ----------- interface ---------- #
with col1:
    if start_button.button("🚀 ابدأ المحادثة"):
        start_recording()

with col2:
    placeholder.text("اضغط على الرز لبدء المحادثة")

with col3:  
    render_chat()
