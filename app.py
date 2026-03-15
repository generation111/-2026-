import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 1. 頁面配置
st.set_page_config(page_title="2026 年度跟刀管理", layout="centered")

# CSS 樣式
st.markdown("""
    <style>
    .block-container {padding-top: 3rem; max-width: 850px;}
    h1 { font-size: 30px !important; color: #1E1E1E; margin-bottom: 1rem; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; padding: 5px; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold !important; }
    .section-head { font-size: 18px; font-weight: bold; color: #007bff; background-color: #e7f1ff; padding: 8px 15px; border-radius: 5px; margin: 25px 0 10px 0; }
    .stButton button { width: 100%; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; height: 52px; font-size: 19px !important; font-weight: bold; border-radius: 10px; margin-top: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 固定您的試算表 ID
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    # 重要：從 Secrets 讀取金鑰，不找本機檔案
    try:
        creds_info = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 金鑰讀取失敗，請檢查 Secrets 設定：{e}")
        return None

@st.cache_data(ttl=5)
def load_data():
    client = get_g_client()
    if client:
        try:
            sh = client.open_by_key(SPREADSHEET_ID)
            s_ws = sh.worksheet("Settings")
            s_raw = s_ws.get_all_values()
            s_df = pd.DataFrame(s_raw[1:], columns=s_raw[0]) if len(s_raw) > 1 else pd.DataFrame()
            m_ws = sh.worksheet("回應試算表")
            m_df = pd.DataFrame(m_ws.get_all_records())
            return s_df, m_df
        except Exception as e:
            st.warning(f"⚠️ 讀取試算表失敗，請確認權限是否已開：{e}")
    return pd.DataFrame(), pd.DataFrame()

def main():
    st.markdown("<h1>📋 慈榛驊業務管理系統</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📝 快速錄入", "📊 數據清單", "🔔 預購追蹤"])
    set_df, main_df = load_data()

    with tab1:
        with st.form("main_form", clear_on_submit=True):
            def get_opts(col_name):
                if not set_df.empty and col_name in set_df.columns:
                    vals = set_df[col_name].astype(str).str.strip()
                    opts = vals[vals.str.len() > 0].unique().tolist()
                    return opts if opts else ["(無資料)"]
                return ["(欄位錯誤)"]

            st.markdown('<div class="section-head">📅 基礎行政資訊</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("使用日期", datetime.now())
                f_hosp = st.selectbox("使用醫院", get_opts("使用醫院"))
            with c2:
                f_price = st.selectbox("批價內容", ["單次批價使用", "批價 + 預購", "使用前次預購", "使用他人預購", "純預購寄庫"])
                f_dept = st.selectbox("使用科別", get_opts("使用科別"))
            with c3:
                f_doc = st.text_input("醫師姓名")
                f_staff = st.text_input("跟刀人員")

            st.markdown('<div class="section-head">📦 產品項目明細</div>', unsafe_allow_html=True)
            f_prod = st.selectbox("產品項目", get_opts("產品項目"))
            c4, c5, c6 = st.columns(3)
            with c4: f_spec = st.text_input("規格")
            with c5: f_qty = st.text_input("數量", value="1")
            with c6: f_loc = st.text_input("使用地點")
            f_detail = st.text_input("詳細內容 (預購備註)")

            st.markdown('<div class="section-head">👤 病患資料與備註</div>', unsafe_allow_html=True)
            c7, c8, c9 = st.columns(3)
            with c7: f_pat = st.text_input("病人名")
            with c8: f_pid = st.text_input("病例號/ID")
            with c9: f_blood = st.selectbox("抽血人員", get_opts("抽血人員"))
            f_op = st.text_input("手術部位/名稱")
            f_note = st.text_area("🗒️ 其他紀錄備註")

            if st.form_submit_button("🚀 確認提交並存檔"):
                client = get_g_client()
                if client:
                    try:
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc, 
                            f_prod, f_spec, f_qty, f_detail, f_pat, f_pid, f_op, 
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("🎉 資料已成功錄入試算表！")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入失敗：{e}")

    with tab2:
        if not main_df.empty:
            st.dataframe(main_df, use_container_width=True, hide_index=True)
        else:
            st.info("目前雲端暫無歷史紀錄。")

    with tab3:
        # 修正欄位名稱與實際試算表匹配
        target = '產品細節 (含預購說明)'
        if not main_df.empty:
            cols = main_df.columns.tolist()
            # 模糊搜尋包含「預購」字眼的欄位
            search_col = next((c for c in cols if "預購" in c), cols[8] if len(cols)>8 else None)
            if search_col:
                f_df = main_df[main_df[search_col].astype(str).str.contains("預購", na=False)]
                if not f_df.empty:
                    st.dataframe(f_df, use_container_width=True)
                else:
                    st.success("目前暫無待追蹤的預購項目。")

if __name__ == "__main__":
    main()
