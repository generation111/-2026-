import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 頁面配置 (必須在程式碼第一行)
st.set_page_config(page_title="2026 年度跟刀管理系統", layout="wide")

# 強制讓分頁標籤與標題貼近頂部，並加大標籤文字
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # 標題
    st.title("📋 『2026』年度跟刀記錄管理系統")

    # --- 關鍵：先定義並顯示分頁標籤 ---
    # 不論後續資料讀取成功與否，這三個按鈕都會出現在標題下方
    tab1, tab2, tab3 = st.tabs(["📝 資料錄入", "📋 跟刀明細清單", "🔔 須回診名單"])

    # --- 分頁 1: 資料錄入 ---
    with tab1:
        st.subheader("跟刀紀錄快速錄入")
        # 即使連線失敗，表單也會顯示基本輸入框
        with st.form("entry_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                v1 = st.date_input("使用日期", datetime.now())
                v2 = st.selectbox("批價內容", ["(等待選單載入)", "單次批價使用", "批價 + 預購", "使用前次預購", "純預購寄庫"])
                v3 = st.text_input("使用醫院 (若選單未載入請手打)")
                v4 = st.text_input("使用科別")
                v5 = st.text_input("醫師姓名")
            with c2:
                v6 = st.text_input("產品項目")
                v7 = st.text_input("規格")
                v8 = st.text_input("數量", value="1")
                v9 = st.text_input("使用產品內容(含預購)")
                v10 = st.text_input("病人名")
            with c3:
                v11 = st.text_input("病例號/ID")
                v12 = st.text_input("手術名稱/使用部位")
                v13 = st.text_input("使用地點")
                v14 = st.text_input("抽血人員")
                v15 = st.text_input("跟刀(操作)人員")
                v16 = st.text_area("備註")
            
            st.form_submit_button("🚀 提交數據")

    # --- 分頁 2: 明細清單 ---
    with tab2:
        st.subheader("跟刀明細紀錄")
        st.warning("⏳ 正在嘗試連線雲端資料夾...")
        # 這裡未來會放置表格資料
        st.info("若此處持續空白，請檢查網路連線或 creds.json 設定。")

    # --- 分頁 3: 回診名單 ---
    with tab3:
        st.subheader("🔔 預購回診追蹤名單")
        st.info("系統將自動過濾『使用產品內容』中含『預購』之名單。")

if __name__ == "__main__":
    main()
