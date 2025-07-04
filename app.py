import streamlit as st
import pandas as pd
import os

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_excel("band_songs.xlsx")
    return df

df = load_data()

# 멤버 파일 경로
MEMBER_FILE = "members.txt"

# 멤버 파일이 없으면 생성
if not os.path.exists(MEMBER_FILE):
    with open(MEMBER_FILE, "w", encoding="utf-8") as f:
        pass

# 멤버 읽기
def read_members():
    with open(MEMBER_FILE, "r", encoding="utf-8") as f:
        return sorted([line.strip() for line in f if line.strip()])

# 멤버 저장
def save_members(members):
    with open(MEMBER_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(set(members))))

# 현재 멤버
all_members = read_members()

st.title("🎸 밴드 합주 곡 세션 관리")

# ====== 이름 관리 UI ======
st.subheader("👥 멤버 관리")

col1, col2 = st.columns(2)

with col1:
    new_member = st.text_input("이름 추가", "")
    if st.button("추가"):
        if new_member.strip():
            all_members.append(new_member.strip())
            save_members(all_members)
            st.success(f"{new_member.strip()} 추가됨!")
            st.experimental_rerun()

with col2:
    remove_members = st.multiselect("삭제할 멤버 선택", options=all_members)
    if st.button("삭제"):
        all_members = [m for m in all_members if m not in remove_members]
        save_members(all_members)
        st.success("선택한 멤버 삭제됨!")
        st.experimental_rerun()

# ====== 참석자 선택 ======
st.subheader("✅ 오늘 참석자 선택")

selected_members = st.multiselect(
    "참석자:",
    options=all_members
)

if st.button("곡 상태 보기"):
    if not selected_members:
        st.warning("참석자를 선택하세요.")
    else:
        result_rows = []
        for _, row in df.iterrows():
            parts = []
            for name, person in [
                ("드럼", row["드럼"]),
                ("베이스", row["베이스"]),
                ("기타1", row["기타1"]),
                ("기타2", row["기타2"]),
                ("건반", row["건반"]),
                ("보컬", row["보컬"])
            ]:
                if pd.isna(person) or str(person).strip() == "":
                    parts.append((name, None))
                else:
                    parts.append((name, str(person).strip()))

            total_parts = sum(1 for _, p in parts if p is not None)
            present_parts = sum(1 for _, p in parts if p is not None and p in selected_members)
            missing_parts = total_parts - present_parts

            part_status = {}
            for name, person in parts:
                if person is None:
                    part_status[name] = "-"
                elif person in selected_members:
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

        result_df = result_df.sort_values(by=["참석 인원"], ascending=False).reset_index(drop=True)

        result_df["참석 인원"] = result_df["참석 인원"].astype(str) + " / " + result_df["총 파트 수"].astype(str)

        def color_missing(val):
            if isinstance(val, int):
                if val == 0:
                    return "background-color: #d4edda"
                elif val == 1:
                    return "background-color: #fff3cd"
                else:
                    return "background-color: #f8d7da"
            return ""

        styled_df = result_df.style.applymap(color_missing, subset=["부족 인원"])

        st.dataframe(styled_df, use_container_width=True)

