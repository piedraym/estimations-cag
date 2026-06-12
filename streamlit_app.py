import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/api/v1/estimate"
STREAM_API_URL = "http://localhost:8000/api/v1/estimate/stream"

def response_generator(transcription):
    try:
        resp = requests.post(
            API_URL,
            json={"transcription": transcription},
            headers={"Content-type": "application/json"},
            timeout = 60
        )
        resp.raise_for_status()
        data = resp.json()
        st.markdown(data["estimation"])
    except requests.exceptions.RequestException as e:
        response = f"Error al llamar a la API: {e}"
        st.error(response)

def stream_response_generator(transcription):
    with requests.post(
        STREAM_API_URL,
        json={"transcription": transcription},
        headers={"Content-Type": "application/json"},
        stream=True,
        timeout=120,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or line.startswith(":"):
                continue # linea vacia
            if line.startswith("data:"):
                yield json.loads(line[len("data:"):].strip())



st.title("Estimador CAG")

#initilize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#Accept user input
if transcription :=st.chat_input("Pega aqui la transctipcion ..."):
    st.session_state.messages.append({"role": "user", "content": transcription})
    with st.chat_message("user"):
        st.markdown(transcription)

    # call to endpoint
    with st.chat_message("assistant"):
        try:
            full_response = st.write_stream(stream_response_generator(transcription))
        except Exception as e:
            full_response = f"Error inesperado: {e}"
            st.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})