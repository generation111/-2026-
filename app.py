import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="2026 年度跟刀記錄管理", layout="centered")

# 試算表 ID
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_client():
    try:
        # 這裡會讀取剛剛在 Secrets 設定的內容
        info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 無法讀取金鑰：{e}")
        return None

@st.cache_data(ttl=5)
def load_data():
    client = get_client()
    if not client: return pd.DataFrame(), pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # 讀取選單
        s_ws = sh.worksheet("Settings")
        s_df = pd.DataFrame(s_ws.get_all_records())
        # 讀取紀錄
        m_ws = sh.worksheet("回應試算表")
        m_df = pd.DataFrame(m_ws.get_all_records())
        return s_df, m_df
    except Exception as e:
        st.error(f"❌ 試算表讀取失敗：{e}")
        return pd.DataFrame(), pd.DataFrame()

# 介面顯示與邏輯保持不變...
s_df, m_df = load_data()

st.title("📋 『2026』年度跟刀記錄管理")
tab1, tab2, tab3 = st.tabs(["📝 紀錄錄入", "📊 資料清單", "🔔 預購追蹤"])

with tab1:
    if s_df.empty:
        st.warning("⚠️ 讀取不到選單資料，請確認試算表『Settings』分頁是否有內容。")
    else:
        with st.form("entry_form"):
            hosp_list = s_df['使用醫院'].dropna().unique().tolist()
            dept_list = s_df['使用科別'].dropna().unique().tolist()
            
            f_date = st.date_input("使用日期", datetime.now())
            f_hosp = st.selectbox("使用醫院", hosp_list)
            f_dept = st.selectbox("使用科別", dept_list)
            # ... 其他欄位保持一致
            if st.form_submit_button("提交數據"):
                st.success("測試點擊成功！")
