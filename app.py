import streamlit as st
import pandas as pd

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_excel("band_songs.xlsx")
    return df.where(pd.notnull(df), None)

df = load_data()

st.title("🎸 밴드 합주 곡 세션별 확인")

members_input = st.text_input(
    "오늘 참석하는 멤버 이름을 쉼표로 입력하세요 (예: 요한,형준,경주):",
    ""
)

if st.button("곡 상태 보기"):
    present_members = [m.strip() for m in members_input.split(",") if m.strip()]
    if not present_members:
        st.warning("참석자를 입력하세요.")
    else:
        result_rows = []
        for _, row in df.iterrows():
            parts = [
                ("드럼", row["드럼"]),
                ("베이스", row["베이스"]),
                ("기타1", row["기타1"]),
                ("기타2", row["기타2"]),
                ("건반", row["건반"]),
                ("보컬", row["보컬"])
            ]

            total_parts = sum(1 for _, p in parts if p is not None)
            present_parts = sum(1 for _, p in parts if p is None or p in present_members)
            missing_parts = total_parts - present_parts

            part_status = {}
            for name, person in parts:
                if person is None:
                    part_status[name] = "-"
                elif person in present_members:
                    part_status[name] = "O"
                else:
                    part_status[name] = "X"

            result_rows.append({
                "곡명": row["곡명"],
                "드럼": part_status["드럼"],
                "베이스": part_status["베이스"],
                "기타1": part_status["기타1"],
                "기타2": part_status["기타2"],
                "건반": part_status["건반"],
                "보컬": part_status["보컬"],
                "참석 인원": present_parts,
                "총 파트 수": total_parts,
                "부족 인원": missing_parts
            })

        result_df = pd.DataFrame(result_rows)

        # 참석 인원 많은 순으로 정렬
        result_df = result_df.sort_values(by=["참석 인원"], ascending=False).reset_index(drop=True)

        # 표시용 열 만들기
        result_df["참석 인원"] = result_df["참석 인원"].astype(str) + " / " + result_df["총 파트 수"].astype(str)

        # "부족 인원" 색칠 함수
        def color_missing(val):
            if isinstance(val, int):
                if val == 0:
                    color = "background-color: #d4edda"  # 연두
                elif val == 1:
                    color = "background-color: #fff3cd"  # 연노랑
                else:
                    color = "background-color: #f8d7da"  # 연빨강
                return color
            return ""

        # 스타일 적용
        styled_df = result_df.style.applymap(color_missing, subset=["부족 인원"])

        st.dataframe(styled_df, use_container_width=True)


