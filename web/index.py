import requests
import streamlit as st

# ページタイトルを表示します
st.title("Streamlit app")

# テキストを表示します
st.text("Hello World!")

# マークダウンを表示します
st.markdown("## Hello World!")

# WebAPI `http://localhost:8000` にリクエストを送り、レスポンスを表示します。
res = requests.get("http://localhost:8000/")
if res.status_code == 200:
    st.text("FastAPI `/` にリクエストを送りました。")
    st.text(res.json())
else:
    st.text("Error occured.")
    print(res.status_code)
