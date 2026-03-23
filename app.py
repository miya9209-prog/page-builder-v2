import io
from typing import Dict

import streamlit as st
from openai import OpenAI
from docx import Document

st.set_page_config(page_title="PAGE BUILDER V2.3", layout="wide")

if "reset_nonce" not in st.session_state:
    st.session_state.reset_nonce = 0

st.title("PAGE BUILDER V2.3")
st.caption("AI 상세페이지 콘텐츠 생성기")

api_key = st.secrets.get("OPENAI_API_KEY", "")
if not api_key:
    st.warning("OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=api_key)

PROMPT = '''
너는 4050 여성 패션 전문 온라인몰 미샵(MISHARP)의 시니어 에디터다.

목표:
- 실제 구매전환이 일어날 수 있도록
- 고객의 고민을 해결하는 상세페이지 콘텐츠 작성

핵심 원칙:
- 고객 문제 해결 중심
- 체형, 핏, TPO 중심 설명
- 과장 금지
- 짧고 명확한 문장

출력 형식:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
상세페이지 본문 구조
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

H2. 이 상품을 추천하는 이유
H2. 원단과 소재의 장점
H2. 체형과 핏에 대하여
H2. 이런 분들께 추천합니다
H2. 이렇게 코디해보세요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
자주 하시는 상품 질문
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 질문+답변 4개 생성

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
먼저 입어본 스텝, 모델 반응
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 실제 착용한 스텝, 모델 코멘트처럼 자연스럽게 4~5개 작성

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
이미지 ALT 텍스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 6개 생성
'''

def build_prompt(data: Dict[str, str]) -> str:
    return PROMPT + "\n\n입력 정보:\n" + str(data)

def result_to_docx_bytes(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio.getvalue()

h1, h2 = st.columns([2,1])
with h1:
    st.subheader("V2.3 입력")
with h2:
    if st.button("초기화"):
        st.session_state.reset_nonce += 1
        st.rerun()

nonce = st.session_state.reset_nonce

left, right = st.columns(2)

with left:
    product_name = st.text_input("상품명", key=f"product_{nonce}")
    category = st.text_input("카테고리", key=f"cat_{nonce}")
    material = st.text_input("소재", key=f"mat_{nonce}")
    color = st.text_input("컬러", key=f"color_{nonce}")
    size = st.text_input("사이즈", key=f"size_{nonce}")
    fit = st.text_input("핏 특징", key=f"fit_{nonce}")
    detail = st.text_area("디테일", key=f"detail_{nonce}")

with right:
    customer_problem = st.text_area("고객 문제", key=f"prob_{nonce}")
    target = st.text_input("타겟", value="4050 여성", key=f"target_{nonce}")
    tpo = st.text_input("TPO", key=f"tpo_{nonce}")
    coordi = st.text_area("코디", key=f"coordi_{nonce}")

st.subheader("이미지 업로드")
st.file_uploader("이미지", accept_multiple_files=True, key=f"img_{nonce}")

st.subheader("동영상 업로드")
st.file_uploader("영상", accept_multiple_files=True, key=f"vid_{nonce}")

if st.button("생성하기"):
    data = {
        "product_name": product_name,
        "category": category,
        "material": material,
        "color": color,
        "size": size,
        "fit": fit,
        "detail": detail,
        "coordi": coordi,
        "target": target,
        "tpo": tpo,
        "customer_problem": customer_problem,
    }

    prompt = build_prompt(data)

    with st.spinner("생성중입니다..."):
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "구조 유지"},
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content

    st.text_area("결과", result, height=900)

    docx = result_to_docx_bytes(result)

    st.download_button(
        "TXT 다운로드",
        data=result,
        file_name=f"{product_name or 'page-builder-v2.3'}_output.txt",
        mime="text/plain"
    )
    st.download_button(
        "DOCX 다운로드",
        data=docx,
        file_name=f"{product_name or 'page-builder-v2.3'}_output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.markdown("---")
st.markdown("© MISHARP")
