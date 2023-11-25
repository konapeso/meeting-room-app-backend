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


if "editing_user" not in st.session_state:
    st.session_state["editing_user"] = None


def main():
    """メインのアプリケーション"""
    st.title("Streamlit app")

    # ユーザーのデータを送信する部分
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

    response = fetch("http://localhost:8000/users/", "GET", {})
    if response.status_code == 200:
        users = response.json()["users"]
        for user in users:
            st.write(
                f"Name: {user['name']}, Full Name: {user['fullname']}, Nickname: {user['nickname']}"
            )
            if st.button("Edit", key=f"edit_{user['id']}"):
                # 編集処理
                pass
            if st.button("Delete", key=f"delete_{user['id']}"):
                # 削除処理
                pass
    else:
        st.error(f"Failed to load users: {response.status_code}")


# セッション状態の初期化
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ログインフォーム
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if check_credentials(username, password):
        st.sidebar.success("Logged in as {}".format(username))
        st.session_state["logged_in"] = True
    else:
        st.sidebar.error("Incorrect username or password")

# ログアウトボタン（オプション）
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False

# ユーザーがログインしている場合のみメインアプリケーションを表示
if st.session_state["logged_in"]:
    main()
