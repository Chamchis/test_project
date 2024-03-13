# main.py
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage
import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4-turbo-preview'

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

want_to = "너는 아래 입력된 특정 시즌의 스페인 라리가 경기 전적을 알려주는 챗봇이야.content{}"
dfs = []
for season in range(12,21):
    df = pd.read_csv(f'laliga/20{season}-{season+1}/es.1.csv')
    dfs.append(df)
df = pd.concat(dfs)

content = df[['Team 1', 'FT', 'Team 2']].values.tolist()

st.header("⚽ Football Base AI")
st.info("12-13 시즌부터 20-21 시즌까지의 스페인 라리가 경기 전적에 대한 내용을 제공합니다")
# st.error("프롬프트 엔지니어링에 대한 내용이 적용되어 있습니다.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [ChatMessage(role="assistant", content="원하시는 두 팀을 입력해주세요 ")]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if prompt := st.chat_input():
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    if not API_KEY:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    with st.chat_message("assistant"):
        stream_handler = StreamHandler(st.empty())
        llm = ChatOpenAI(openai_api_key=API_KEY, streaming=True, callbacks=[stream_handler], model_name=MODEL)
        response = llm([ ChatMessage(role="system", content=want_to.format(content))]+st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))