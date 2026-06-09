import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/estimate"

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
        with st.spinner("Estimando..."):
            response = response_generator(transcription)

    st.session_state.messages.append({"role": "assistant", "content": response})