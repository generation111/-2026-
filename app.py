import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 1. 頁面配置
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

# CSS 樣式修正：標題貼頂，讓平板畫面更緊湊
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; max-width: 1000px;}
    h1 { font-size: 26px !important; color: #1E1E1E; text-align: center; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; border-radius: 10px; }
    .stSelectbox label, .stTextInput label, .stDateInput label { font-weight: 700 !important; color: #34495e !important; }
    .stButton button { width: 100%; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; height: 45px; font-weight: bold; border-radius: 8px; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

# 強制不使用緩存，確保每次都能抓到最新選單
def get_g_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # 雲端版必備：從 Secrets 讀取
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"⚠️ 金鑰讀取失敗，請確認 Streamlit 後台 Secrets 設定。")
        return None

def load_settings():
    client = get_g_client()
    if not client: return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # 精準對位：讀取「Settings」工作表
        ws = sh.worksheet("Settings")
        data = ws.get_all_values()
        # 將第一行作為標題轉為 DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        return df
    except Exception as e:
        st.error(f"❌ 讀取 Settings 失敗：{e}")
        return pd.DataFrame()

def main():
    st.markdown("<h1>📋 『2026』年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    # 載入選單資料
    df_set = load_settings()

    tab1, tab2, tab3 = st.tabs(["📝 資料錄入", "📊 年度明細清單", "🔔 須回診名單"])

    with tab1:
        if df_set.empty:
            st.warning("🔄 選單資料同步中... 若長時間未出現請重新整理頁面。")
        
        with st.form("main_form", clear_on_submit=True):
            def get_list(col_name):
                if col_name in df_set.columns:
                    return [v for v in df_set[col_name].unique() if v and v.strip()]
                return ["(欄位未找到)"]

            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("使用日期", datetime.now())
                f_price = st.selectbox("批價內容", get_list("批價內容"))
                f_hosp = st.selectbox("使用醫院", get_list("使用醫院"))
                f_dept = st.selectbox("使用科別", get_list("使用科別"))
            with c2:
                f_prod = st.selectbox("產品項目", get_list("產品項目"))
                f_spec = st.text_input("規格")
                f_qty = st.text_input("數量", value="1")
                f_content = st.text_input("使用產品內容(含預購)")
            with c3:
                f_pid = st.text_input("病例號/ID")
                f_op = st.text_input("手術名稱/使用部位")
                f_loc = st.text_input("使用地點")
                f_blood = st.selectbox("抽血人員", get_list("抽血人員"))

            f_doc = st.text_input("醫師姓名")
            f_pat = st.text_input("病人名")
            f_staff = st.text_input("跟刀(操作)人員")
            f_note = st.text_area("備註")

            if st.form_submit_button("🚀 提交數據"):
                client = get_g_client()
                if client:
                    try:
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        # 依照回應試算表的欄位順序寫入
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                            f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("✅ 數據已成功存檔至雲端試算表！")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"存檔失敗：{e}")

    with tab2:
        st.write("📖 此功能將於後續版本連動完整歷史數據。")

if __name__ == "__main__":
    main()
