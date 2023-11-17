import streamlit as st
from utils.http_client import fetch


def main():
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


if __name__ == "__main__":
    main()
