from google.protobuf import message
import streamlit as st
from openai import OpenAI
from google import genai
from groq import Groq
from dotenv import load_dotenv
from urllib3 import response
from core.config import config

def runllm(provider, model_name, messages, max_tokens=500):
    if provider == "Openai":
        client = OpenAI(api_key=config.openai_api_key)
    
    elif provider == "Groq":
        client = Groq(api_key=config.groq_api_key)
    else:
        client = genai.Client(api_key=config.gemini_api_key)
    
    if provider == "Google":
        response = client.models.generate_content(
            model=model_name,
            contents=[message["content"] for message in messages],
        ).text
    elif provider == "Groq":
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens
        ).choices[0].message.content
    else:
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_completion_tokens=max_tokens,
            reasoning_effort="minimal",
        ).choices[0].message.content

with st.sidebar:
    st.title("LLM API Tester")
    provider = st.selectbox("Provider", ["Openai", "Google", "Groq"])
    if provider == "Openai":
        model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"])
    elif provider == "Google":
        model_name = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.0-flash"])
    elif provider == "Groq":
        model_name = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.3-70b-instruct"])

    st.session_state.provider = provider
    st.session_state.model_name = model_name

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        output = runllm(st.session_state.provider, st.session_state.model_name, st.session_state.messages)
        response_data = output
        answer = response_data
        st.write(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})