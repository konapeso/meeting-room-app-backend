import streamlit as st
import datetime
import requests
import json
import pandas as pd


page = st.sidebar.selectbox(
    "Choose your page", ["users", "rooms", "bookings", "booked_rooms"]
)

if page == "users":
    st.title("ユーザー登録画面")
    with st.form(key="user"):
        user_name = st.text_input(label="ユーザー名", max_chars=100)
        user_email = st.text_input(label="メールアドレス")
        is_executive = st.checkbox("役員ですか？")
        password = st.text_input(label="パスワード", type="password")
        if len(password) < 8:
            st.error("パスワードは最低8文字必要です。")
        data = {
            "user_name": user_name,
            "user_email": user_email,
            "is_executive": is_executive,
            "password": password,
        }
        submit_button = st.form_submit_button(label="リクエスト送信")

    if submit_button:
        url = "http://127.0.0.1:8000/users"
        res = requests.post(url, data=json.dumps(data))
        if res.status_code == 200:
            st.success("ユーザー登録完了")
        st.json(res.json())


elif page == "rooms":
    st.title("会議室登録画面")
    with st.form(key="room"):
        room_name = st.text_input("部屋名", max_chars=100)
        capacity = st.number_input("定員", step=1)
        image_url = st.text_input("画像URLを入力してください")
        room_type_options = ["社員用", "役員用", "ゲストルーム"]
        room_type = st.selectbox("会議室タイプ", room_type_options)
        submit_button = st.form_submit_button(label="会議室登録")

    if submit_button:
        if image_url:
            data = {
                "room_name": room_name,
                "capacity": capacity,
                "room_image": image_url,
                "room_type": room_type,
            }
        else:
            st.error("画像がアップロードされていません。")
        url = "http://127.0.0.1:8000/rooms"
        res = requests.post(url, data=json.dumps(data))
        if res.status_code == 200:
            st.success("会議室登録完了")
        st.json(res.json())


elif page == "bookings":
    st.title("会議室予約画面")
    # ユーザー一覧の取得
    url_users = "http://127.0.0.1:8000/users"
    res = requests.get(url_users)

    users = res.json()
    users_name = {}
    users_id = {user["user_id"]: user["user_name"] for user in users}
    for user in users:
        users_name[user["user_name"]] = user["user_id"]

    # 会議室一覧の取得
    url_rooms = "http://localhost:8000/rooms"
    res = requests.get(url_rooms)
    rooms = res.json()
    rooms_name = {}
    rooms_id = {
        room["room_id"]: {
            "room_name": room["room_name"],
            "capacity": room["capacity"],
            "room_type": room["room_type"],
        }
        for room in rooms
    }
    for room in rooms:
        rooms_name[room["room_name"]] = {
            "room_id": room["room_id"],
            "capacity": room["capacity"],
            "room_type": room["room_type"],
        }

    st.write("### 会議室一覧")
    df_rooms = pd.DataFrame(rooms)
    df_rooms.columns = [
        "会議室名",
        "定員",
        "会議室画像",
        "会議室タイプ",
        "会議室ID",
    ]
    st.table(df_rooms)

    url_bookings = "http://localhost:8000/bookings"
    res = requests.get(url_bookings)
    bookings = res.json()

    if bookings:  # データが存在する場合
        df_bookings = pd.DataFrame(bookings)

        # IDを各値に変更
        to_user_name = lambda x: users_id[x]
        to_room_name = lambda x: rooms_id[x]["room_name"]
        to_datetime = lambda x: datetime.datetime.fromisoformat(x).strftime(
            "%Y/%m/%d %H:%M"
        )

        # user_id と room_id のマッピング処理
        if "user_id" in df_bookings.columns:
            df_bookings["user_id"] = df_bookings["user_id"].map(to_user_name)
        if "room_id" in df_bookings.columns:
            df_bookings["room_id"] = df_bookings["room_id"].map(to_room_name)

        # 日時のフォーマット処理
        df_bookings["start_datetime"] = df_bookings["start_datetime"].map(to_datetime)
        df_bookings["end_datetime"] = df_bookings["end_datetime"].map(to_datetime)

        # 列名の変更
        df_bookings = df_bookings.rename(
            columns={
                "user_id": "予約者名",
                "room_id": "会議室名",
                "booked_num": "予約人数",
                "start_datetime": "開始時刻",
                "end_datetime": "終了時刻",
                "booking_id": "予約番号",
            }
        )

        st.write("### 予約一覧")
        st.table(df_bookings)

    else:  # データが存在しない場合
        st.write("現在予約はありません。")

    # Streamlit セッションステートの初期化
    if "selected_room_name" not in st.session_state:
        st.session_state.selected_room_name = list(rooms_name.keys())[0]
    if "is_guest_room" not in st.session_state:
        st.session_state.is_guest_room = False

    # 会議室名の選択
    selected_room_name = st.selectbox(
        "会議室名",
        list(rooms_name.keys()),
        index=list(rooms_name.keys()).index(st.session_state.selected_room_name),
    )
    selected_room = rooms_name[selected_room_name]
    st.session_state.selected_room_name = selected_room_name

    # 会議室タイプの更新
    st.session_state.is_guest_room = selected_room["room_type"] == "ゲストルーム"

    with st.form(key="booking"):
        user_name: str = st.selectbox("予約者名", list(users_name.keys()))
        booked_num: int = st.number_input("予約人数", step=1, min_value=1)
        date = st.date_input("日付を入力", min_value=datetime.date.today())
        start_time = st.time_input("開始時刻:", value=datetime.time(hour=9, minute=0))
        end_time = st.time_input("終了時刻:", value=datetime.time(hour=20, minute=0))
        participant_names = st.multiselect("参加者を選択", list(users_name.keys()))
        # ゲストのメールアドレス入力フィールド（ゲストルームの場合のみ表示）
        guest_email = (
            st.text_input("ゲストのメールアドレスを入力") if st.session_state.is_guest_room else ""
        )
        submit_button = st.form_submit_button(label="予約登録")

    if submit_button:
        user_id: int = users_name[user_name]
        room_id = selected_room["room_id"]
        capacity = selected_room["capacity"]
        participant_ids = [users_name[name] for name in participant_names]
        participants = []
        for name in participant_names:
            participants.append(
                {"user_id": users_name[name], "is_guest": False, "guest_email": None}
            )

        # ゲストのメールアドレスがある場合、ゲストユーザーを追加
        if st.session_state.is_guest_room and guest_email:
            participants.append(
                {"user_id": None, "is_guest": True, "guest_email": guest_email}
            )

        data = {
            "user_id": user_id,
            "room_id": room_id,
            "booked_num": booked_num,
            "start_datetime": datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=start_time.hour,
                minute=start_time.minute,
            ).isoformat(),
            "end_datetime": datetime.datetime(
                year=date.year,
                month=date.month,
                day=date.day,
                hour=end_time.hour,
                minute=end_time.minute,
            ).isoformat(),
            "participants": participants,
        }

        # 定員より多い予約人数の場合
        if booked_num > capacity:
            st.error(f"{selected_room_name}の定員は{capacity}人です。予約人数を減らしてください。")
        # 開始時刻 >= 終了時刻
        elif start_time >= end_time:
            st.error("開始時刻が終了時刻を超えています。")
        elif start_time < datetime.time(
            hour=9, minute=0, second=0
        ) or end_time > datetime.time(hour=20, minute=0, second=0):
            st.error("利用時間は9:00~20:00です。")
        else:
            url = "http://127.0.0.1:8000/bookings"
            res = requests.post(url, json=data)
            if res.status_code == 200:
                st.success("予約完了しました")
            elif res.status_code == 404 and res.json()["detail"] == "Already booked":
                st.error("指定の時間にはすでに予約が入っています。")
            st.json(res.json())

elif page == "booked_rooms":
    st.title("会議室予約一覧")

    # ユーザー情報と会議室情報を取得
    users_res = requests.get("http://127.0.0.1:8000/users")
    rooms_res = requests.get("http://127.0.0.1:8000/rooms")

    # ユーザー情報と会議室情報をIDをキーとする辞書に変換
    if users_res.status_code == 200 and rooms_res.status_code == 200:
        users = {user["user_id"]: user["user_name"] for user in users_res.json()}
        rooms = {room["room_id"]: room["room_name"] for room in rooms_res.json()}

        # 予約情報の取得
        bookings_res = requests.get("http://127.0.0.1:8000/bookings")
        if bookings_res.status_code == 200:
            bookings = bookings_res.json()
            for booking in bookings:
                user_name = users.get(booking["user_id"], "不明")
                room_name = rooms.get(booking["room_id"], "不明")
                start_datetime = datetime.datetime.fromisoformat(
                    booking["start_datetime"]
                ).strftime("%Y/%m/%d %H:%M")
                end_datetime = datetime.datetime.fromisoformat(
                    booking["end_datetime"]
                ).strftime("%Y/%m/%d %H:%M")

                # 参加者情報の取得
                participants_res = requests.get(
                    f'http://127.0.0.1:8000/bookings/{booking["booking_id"]}/participants'
                )
                participants_names = []
                if participants_res.status_code == 200:
                    participants = participants_res.json()
                    for participant in participants:
                        if participant["user_id"]:
                            participant_name = users.get(participant["user_id"], "不明")
                        else:
                            participant_name = "ゲスト"
                        participants_names.append(participant_name)

                # 予約情報の表示
                st.subheader(f"予約ID: {booking['booking_id']}")
                st.write(f"予約者名: {user_name}")
                st.write(f"会議室名: {room_name}")
                st.write(f"予約人数: {booking['booked_num']}")
                st.write(f"開始時刻: {start_datetime}")
                st.write(f"終了時刻: {end_datetime}")
                st.write(f"参加者: {', '.join(participants_names)}")

                # キャンセルボタンの追加
                start_datetime = datetime.datetime.fromisoformat(
                    booking["start_datetime"]
                )
                if (
                    datetime.datetime.now() + datetime.timedelta(minutes=30)
                    < start_datetime
                ):
                    if st.button(
                        f"キャンセル {booking['booking_id']}",
                        key=f"cancel-{booking['booking_id']}",
                        type="primary",
                    ):
                        cancel_url = (
                            f"http://127.0.0.1:8000/bookings/{booking['booking_id']}"
                        )
                        res_cancel = requests.delete(cancel_url)
                        if res_cancel.status_code == 200:
                            st.success(f"予約 {booking['booking_id']} がキャンセルされました")
                        else:
                            st.error(f"予約 {booking['booking_id']} のキャンセルに失敗しました")
                st.markdown("---")
        else:
            st.write("予約されている会議室はありません。")
    else:
        st.error(f"エラーが発生しました。ステータスコード: {res.status_code}")
