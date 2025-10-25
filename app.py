# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="さや比ビューア", layout="wide")
st.title("銘柄ペアのさや比グラフ")

# 日経225構成銘柄一覧を取得（キャッシュ付き）
@st.cache_data
def get_nikkei225_tickers():
    url = "https://indexes.nikkei.co.jp/nkave/index/component?idx=nk225"
    tables = pd.read_html(url)
    df_all = pd.concat(tables, ignore_index=True)
    df_all['コード'] = df_all['コード'].astype(str).str.zfill(4) + '.T'
    ticker_dict = dict(zip(df_all['コード'], df_all['銘柄名']))
    return ticker_dict

ticker_dict = get_nikkei225_tickers()
ticker_list = list(ticker_dict.keys())

# 銘柄選択UI
col1, col2 = st.columns(2)
with col1:
    code_a = st.selectbox("企業Aを選択", ticker_list, format_func=lambda x: f"{x} - {ticker_dict[x]}")
with col2:
    code_b = st.selectbox("企業Bを選択", ticker_list, format_func=lambda x: f"{x} - {ticker_dict[x]}")

# 実行ボタン
if st.button("グラフを表示"):
    if code_a != code_b:
        df_raw_a = yf.download(code_a, period="1y")
        df_raw_b = yf.download(code_b, period="1y")

        if not df_raw_a.empty and not df_raw_b.empty:
            df_a = df_raw_a["Close"]
            df_b = df_raw_b["Close"]
            df = pd.DataFrame({
                "企業A": df_a,
                "企業B": df_b
            }).dropna()

            df["さや比"] = df["企業A"] / df["企業B"]
            df["75日移動平均"] = df["さや比"].rolling(window=75).mean()

            st.subheader(f"{ticker_dict[code_a]} vs {ticker_dict[code_b]} のさや比推移")
            st.line_chart(df[["さや比", "75日移動平均"]])
        else:
            st.error("株価データの取得に失敗しました。銘柄コードを確認してください。")
    else:
        st.warning("異なる2銘柄を選択してください。")