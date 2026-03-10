import streamlit as st
import requests

st.title("AI Travel Agent")

user_input = st.text_input("Ask your travel question")

if st.button("Send"):

    payload = {"question": user_input}

    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json=payload
    )

    data = response.json()

    st.write("### Agent Response")
    st.write(data["response"])