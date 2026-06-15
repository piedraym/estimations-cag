import os
import streamlit as st
import requests
import json
import time

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/api/v1/estimate"
STREAM_API_URL = f"{API_BASE_URL}/api/v1/estimate/stream"

TYPEWRITER_CHUNK_SIZE = 3     # caracteres por "tick" al simular escritura
TYPEWRITER_DELAY = 0.01       # segundos entre ticks

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
        cache_hit = resp.headers.get("X-Cache-Hit") == "true"
        st.session_state.last_cache_hit = cache_hit
        for line in resp.iter_lines(decode_unicode=True):
            if not line or line.startswith(":"):
                continue # linea vacia
            if line.startswith("data:"):
                event = json.loads(line[len("data:"):].strip())
                if event["type"] == "delta":
                    delta = event["content"]
                    if cache_hit:
                        for i in range(0, len(delta), TYPEWRITER_CHUNK_SIZE):
                            yield delta[i:i + TYPEWRITER_CHUNK_SIZE]
                            time.sleep(TYPEWRITER_DELAY)
                    else:
                        yield delta
                elif event["type"] == "done":
                    st.session_state.last_model = event["model"]
                    st.session_state.last_usage = event["usage"]



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

with st.sidebar:
    st.header("Cache")
    if "last_cache_hit" in st.session_state:
        if st.session_state.last_cache_hit:
            st.success("Last call: Cache Hit")
        else:
            st.info("Last call: Cache Miss")
    else:
        st.caption("Any consult yet")

    st.header("Modelo")
    last_model = st.session_state.get("last_model")
    if last_model:
        st.write(last_model)
    else:
        st.caption("Any data yet")

    st.header("Tokens")
    usage = st.session_state.get("last_usage")
    if usage:
        st.metric("Enviados (input)", usage["input_tokens"])
        st.metric("Recibido (output)", usage["output_tokens"])
        st.metric("Total", usage["total_tokens"])
    else:
        st.caption("No data yet")