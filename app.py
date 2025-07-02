import streamlit as st
import pandas as pd

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_excel("band_songs.xlsx")
    return df.where(pd.notnull(df), None)

df = load_data()

st.title("🎸 밴드 합주 곡 선택기")

members_input = st.text_input(
    "오늘 참석하는 멤버 이름을 쉼표로 입력하세요 (예: 요한,형준,경주):",
    ""
)

if st.button("가능한 곡 보기"):
    present_members = [m.strip() for m in members_input.split(",") if m.strip()]
    if not present_members:
        st.warning("참석자를 입력하세요.")
    else:
        priorities = {1: [], 2: [], 3: []}
        for _, row in df.iterrows():
            parts = [
                ("드럼", row["드럼"]),
                ("베이스", row["베이스"]),
                ("기타1", row["기타1"]),
                ("기타2", row["기타2"]),
                ("건반", row["건반"]),
                ("보컬", row["보컬"])
            ]
            total = sum(1 for _, p in parts if p is not None)
            present = sum(1 for _, p in parts if p is None or p in present_members)
            # 담당자 이름도 같이 표시
            missing = [f"{name}({p})" for name, p in parts if p is not None and p not in present_members]

            if present == total:
                priorities[1].append((row["곡명"], missing))
            elif present == total - 1:
                priorities[2].append((row["곡명"], missing))
            elif present == total - 2:
                priorities[3].append((row["곡명"], missing))

        found = False
        for level in [1, 2, 3]:
            if priorities[level]:
                if level == 1:
                    st.subheader("✅ 1순위 (모두 참석)")
                elif level == 2:
                    st.subheader("⚠️ 2순위 (1명 결원)")
                elif level == 3:
                    st.subheader("⚠️ 3순위 (2명 결원)")
                for song, missing in priorities[level]:
                    st.write(f"- {song} (부족한 파트: {', '.join(missing) if missing else '없음'})")
                found = True
        if not found:
            st.error("참석 인원으로 연주 가능한 곡이 없습니다.")


