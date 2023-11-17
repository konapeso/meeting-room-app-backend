import streamlit as st
from utils.http_client import fetch

# secrets.toml からユーザー名とパスワードを読み込む
usernames = st.secrets["usernames"]["users"]
passwords = st.secrets["passwords"]["users"]

# ユーザー名とパスワードを辞書として格納
credentials = dict(zip(usernames, passwords))


def check_credentials(username, password):
    """与えられたユーザー名とパスワードの組み合わせが正しいか確認する"""
    return credentials.get(username) == password


def main():
    """メインのアプリケーション"""
    st.title("Streamlit app")

    name = st.text_input("Name")
    fullname = st.text_input("Full Name")
    nickname = st.text_input("Nickname")

    if st.button("Submit Data"):
        if name and fullname and nickname:
            user_data = {"name": name, "fullname": fullname, "nickname": nickname}
            response = fetch("http://localhost:8000/users/", "POST", user_data)
            if response.status_code == 200:
                st.success("User created successfully!")
            else:
                st.error(f"Failed to create user: {response.status_code}")
        else:
            st.error("All fields are required")


# ログインフォーム
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if check_credentials(username, password):
        st.sidebar.success("Logged in as {}".format(username))
        main()
    else:
        st.sidebar.error("Incorrect username or password")
