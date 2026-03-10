import streamlit as st
import requests

st.title("Underrated Movies Finder")

query = st.text_input("Enter a movie-related query (optional):")

if st.button("Get Underrated Movies"):
    response = requests.post(
        "http://localhost:8000/underrated-movies",
        json={"query": query}
    )
    if response.status_code == 200:
        movies = response.json().get("underrated_movies", [])
        st.write("### Underrated Movies:")
        for movie in movies:
            st.write(f"- {movie}")
    else:
        st.error("Failed to fetch movies. Is the FastAPI server running?")
