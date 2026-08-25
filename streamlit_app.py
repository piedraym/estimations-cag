import os
import streamlit as st
import requests

from pydantic import ValidationError
from app.schemas.estimation import EstimationRequest

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/api/v1/estimate"

st.title("Estimador CAG")

with st.form("estimation_form"):
    transcription = st.text_area(
        "Transcripcion de la reunion",
        placeholder= "Pega aqui la transcripcion...",
        height=300
    )
    submitted = st.form_submit_button("Estimar")

if submitted:
    try:
        request = EstimationRequest(transcription=transcription)
    except ValidationError as e:
        st.error(f"Datos invalidos: {e}")
    else:
        with st.spinner("Generando estimacion..."):
            try:
                resp = requests.post(
                    API_URL,
                    json=request.model_dump(),
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Error al llamar a la API: {e}")
            else:
                st.session_state.last_estimation = data["estimation"]
                st.session_state.last_model = data["model"]
                st.session_state.last_usage = data["usage"]

if "last_estimation" in st.session_state:
    st.markdown(st.session_state.last_estimation)

with st.sidebar:
    st.header("Modelo")
    last_model = st.session_state.get("last_model")
    if last_model:
        st.write(last_model)
    else:
        st.caption("No hay datos aun")

    st.header("Tokens")
    usage = st.session_state.get("last_usage")
    if usage:
        st.metric("Enviados (input)", usage["input_tokens"])
        st.metric("Recibido (output)", usage["output_tokens"])
        st.metric("Total", usage["total_tokens"])
    else:
        st.caption("No hay datos aun")