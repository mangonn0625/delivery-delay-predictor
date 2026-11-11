from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

데이터파일 = Path(__file__).resolve().parent / "data.csv"   # 캐글 Train.csv를 data.csv로 저장해 둔 파일

열_한글 = {
    "Warehouse_block": "창고 구역",
    "Mode_of_Shipment": "배송 방식",
    "Customer_care_calls": "고객센터 문의 횟수",
    "Customer_rating": "고객 평점",
    "Cost_of_the_Product": "제품 가격",
    "Prior_purchases": "이전 구매 횟수",
    "Product_importance": "제품 중요도",
    "Gender": "성별",
    "Discount_offered": "할인율(%)",
    "Weight_in_gms": "무게(g)",
    "지연": "지연 여부 (1=지연, 0=정시)",
}


@st.cache_data(show_spinner="데이터를 불러오는 중...")
def 데이터_읽기() -> pd.DataFrame:
    """data.csv를 읽고 ID 열은 버린다. 목표 열 이름을 '지연'으로 바꾼다(1=지연, 0=정시 도착)."""
    df = pd.read_csv(데이터파일, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Reached.on.Time_Y.N": "지연"})
    df = df.drop(columns=["ID"], errors="ignore").dropna().drop_duplicates()
    return df.reset_index(drop=True)


st.set_page_config(page_title="배송 지연 예측 실습실", page_icon="📦", layout="wide")

st.title("📦 배송 지연 예측 실습실")
st.write("쇼핑몰 배송 기록을 읽어 와서 들여다보고, 모델을 만들고, 채점하고, 직접 예측해 봅니다. "
         "왼쪽 메뉴에서 페이지를 넘기세요.")

try:
    df = 데이터_읽기()
except FileNotFoundError:
    st.error("data.csv 파일이 없습니다. 캐글 'E-Commerce Shipping Data'의 Train.csv를 "
             "data.csv로 이름을 바꿔 main.py와 같은 폴더에 넣어 주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

st.subheader("한눈에 보기")
칸1, 칸2, 칸3, 칸4 = st.columns(4)
칸1.metric("전체 주문 수", f"{len(df):,}건")
칸2.metric("열 개수", f"{df.shape[1]}개")
칸3.metric("지연된 주문", f"{int(df['지연'].sum()):,}건")
칸4.metric("지연 비율", f"{df['지연'].mean() * 100:.1f}%")

st.subheader("지연 비율 한눈에 보기")
그래프칸1, 그래프칸2 = st.columns(2)

with 그래프칸1:
    비율표 = df["지연"].map({0: "정시 도착", 1: "지연"}).value_counts().reset_index()
    비율표.columns = ["상태", "주문 수"]
    파이 = px.pie(비율표, names="상태", values="주문 수", hole=0.4,
                  title="전체 주문의 정시 · 지연 비율")
    파이.update_traces(textinfo="percent+label")
    st.plotly_chart(파이, use_container_width=True)

with 그래프칸2:
    방식별 = df.groupby("Mode_of_Shipment")["지연"].mean().mul(100).round(1).reset_index()
    방식별.columns = ["배송 방식", "지연 비율(%)"]
    막대 = px.bar(방식별, x="배송 방식", y="지연 비율(%)", text="지연 비율(%)",
                  title="배송 방식별 지연 비율")
    st.plotly_chart(막대, use_container_width=True)

st.subheader("열마다 무엇이 들어 있는가")


def 값의_종류(열):
    """숫자 열은 가장 작은 값과 가장 큰 값을, 글자 열은 값의 가짓수와 실제 값을 적는다."""
    칸 = df[열].dropna()
    if 칸.dtype != object and 칸.nunique() > 2:
        return f"숫자 {칸.min():g} ~ {칸.max():g}"
    값들 = sorted(칸.unique().astype(str))
    return f"{len(값들)}가지 · " + " · ".join(값들)


st.dataframe(
    {
        "열 이름": list(df.columns),
        "우리말 뜻": [열_한글.get(c, "") for c in df.columns],
        "값의 종류": [값의_종류(c) for c in df.columns],
        "빈 값 개수": [int(df[c].isna().sum()) for c in df.columns],
    },
    width="stretch",
    hide_index=True,
)

st.subheader("앞 다섯 줄 그대로 보기")
st.dataframe(df.head(5), width="stretch", hide_index=True)

st.subheader("이 데이터는 어디서 왔는가")
st.text_area(
    "출처 (직접 확인해서 고쳐 적으세요)",
    value="출처: 캐글 E-Commerce Shipping Data\n"
          "원본 주소: https://www.kaggle.com/datasets (사이트에서 'E-Commerce Shipping Data' 검색)\n"
          "용도: 이 수업에서는 교육 목적으로만 사용합니다.",
    height=130,
)
st.caption("출처와 용도는 다운로드 페이지에서 직접 확인하세요. 이 데이터로 얻은 결과는 "
           "수업용 연습이며 실제 물류 의사결정에 그대로 쓰면 안 됩니다.")
