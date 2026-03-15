import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 1. 頁面配置
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="centered")

# CSS 樣式：保留您要求的極致細節與三欄排版
st.markdown("""
    <style>
    .block-container {padding-top: 2rem; max-width: 850px;}
    h1 { font-size: 28px !important; color: #1E1E1E; margin-bottom: 1rem; text-align: center; }
    
    /* 分頁美化 */
    .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; padding: 5px; border-radius: 12px; border: 1px solid #e9ecef; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold !important; color: #495057; }
    .stTabs [aria-selected="true"] { color: #007bff !important; border-bottom: 3px solid #007bff !important; }

    /* 標籤間距強化 */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stDateInput label {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #34495e !important;
        padding-top: 8px !important;
        margin-bottom: 4px !important;
    }
    
    /* 區塊標題 */
    .section-head {
        font-size: 17px;
        font-weight: bold;
        color: #007bff;
        background-color: #e7f1ff;
        padding: 8px 15px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
        border-left: 5px solid #007bff;
    }

    /* 提交按鈕 */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        height: 52px;
        font-size: 19px !important;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        margin-top: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# 試算表 ID
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # 優先嘗試讀取雲端 Secrets (GitHub/Streamlit 佈署用)
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    # 如果 Secrets 找不到，再嘗試讀取本地檔案 (VS Code 開發用)
    else:
        try:
            creds = Credentials.from_service_account_file("creds.json", scopes=scope)
        except Exception as e:
            st.error("找不到金鑰：雲端 Secrets 或本地 creds.json 皆無效。")
            return None
            
    return gspread.authorize(creds)

@st.cache_data(ttl=5)
def load_data():
    try:
        client = get_g_client()
        if not client: return pd.DataFrame(), pd.DataFrame()
        sh = client.open_by_key(SPREADSHEET_ID)
        
        # 讀取 Settings
        s_ws = sh.worksheet("Settings")
        s_raw = s_ws.get_all_values()
        s_df = pd.DataFrame(s_raw[1:], columns=s_raw[0]) if len(s_raw) > 1 else pd.DataFrame()
        
        # 讀取 回應試算表
        m_ws = sh.worksheet("回應試算表")
        m_df = pd.DataFrame(m_ws.get_all_records())
        return s_df, m_df
    except:
        return pd.DataFrame(), pd.DataFrame()

def main():
    st.markdown("<h1>📋 2026 年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)

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
            f_note = st.text_area("🗒️ 其他特殊紀錄備註")

            if st.form_submit_button("🚀 確認提交並存檔"):
                with st.spinner("正在同步至雲端..."):
                    try:
                        client = get_g_client()
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc, 
                            f_prod, f_spec, f_qty, f_detail, f_pat, f_pid, f_op, 
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("🎉 2026 年度紀錄存檔成功！")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"連線失敗: {e}")

    with tab2:
        if not main_df.empty:
            st.dataframe(main_df, use_container_width=True, hide_index=True)
        else:
            st.info("目前雲端暫無歷史紀錄。")

    with tab3:
        # 根據您試算表的實際標題做比對，確保篩選正常
        if not main_df.empty:
            search_col = next((c for c in main_df.columns if "預購" in str(c) or "內容" in str(c)), None)
            if search_col:
                f_df = main_df[main_df[search_col].astype(str).str.contains("預購", na=False)]
                st.dataframe(f_df, use_container_width=True)

if __name__ == "__main__":
    main()
