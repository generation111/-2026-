import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 1. 頁面配置：設定標題與側邊欄狀態
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="centered")

# 2. CSS 樣式：確保介面貼近上緣且欄位清晰
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; max-width: 850px;}
    h1 { font-size: 28px !important; color: #1E1E1E; text-align: center; margin-bottom: 20px; }
    
    /* 區塊標題樣式 */
    .section-head {
        font-size: 17px;
        font-weight: bold;
        color: #007bff;
        background-color: #f0f7ff;
        padding: 6px 12px;
        border-radius: 5px;
        margin: 15px 0 10px 0;
        border-left: 5px solid #007bff;
    }

    /* 標籤文字強化 */
    .stSelectbox label, .stTextInput label, .stDateInput label, .stTextArea label {
        font-weight: 700 !important;
        color: #34495e !important;
    }

    /* 分頁標籤美化 */
    .stTabs [data-baseweb="tab-list"] { background-color: #f8f9fa; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-size: 16px !important; font-weight: bold !important; }

    /* 提交按鈕 */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        height: 50px;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 10px;
        margin-top: 20px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 試算表 ID (請確保已共用權限給 Service Account Email)
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    """連線邏輯：優先讀取雲端 Secrets，失敗則讀取本地 creds.json"""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # 1. 嘗試讀取 Streamlit Cloud Secrets (GitHub 版)
    try:
        if "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(creds_info, scopes=scope)
            return gspread.authorize(creds)
    except:
        pass

    # 2. 嘗試讀取本地檔案 (VS Code 版)
    try:
        creds = Credentials.from_service_account_file("creds.json", scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 無法取得金鑰授權。請檢查 Secrets 設定或 creds.json 檔案。詳情: {e}")
        return None

@st.cache_data(ttl=10)
def load_data():
    client = get_g_client()
    if not client:
        return pd.DataFrame(), pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # 讀取 Settings (選單來源)
        s_ws = sh.worksheet("Settings")
        s_raw = s_ws.get_all_values()
        s_df = pd.DataFrame(s_raw[1:], columns=s_raw[0]) if len(s_raw) > 1 else pd.DataFrame()
        # 讀取 回應試算表 (歷史紀錄)
        m_ws = sh.worksheet("回應試算表")
        m_df = pd.DataFrame(m_ws.get_all_records())
        return s_df, m_df
    except Exception as e:
        st.warning(f"無法讀取試算表，請確認權限已開放給金鑰電郵。")
        return pd.DataFrame(), pd.DataFrame()

def main():
    st.markdown("<h1>📋 2026 年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 快速錄入", "📊 年度明細", "🔔 預購追蹤"])
    
    set_df, main_df = load_data()

    with tab1:
        with st.form("main_form", clear_on_submit=True):
            def get_opts(col_name):
                if not set_df.empty and col_name in set_df.columns:
                    vals = set_df[col_name].astype(str).str.strip()
                    opts = vals[vals.str.len() > 0].unique().tolist()
                    return opts if opts else ["(無資料)"]
                return ["(同步中...)"]

            # --- 行政資訊 ---
            st.markdown('<div class="section-head">📅 行政與醫院資訊</div>', unsafe_allow_html=True)
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

            # --- 產品資訊 ---
            st.markdown('<div class="section-head">📦 產品明細</div>', unsafe_allow_html=True)
            f_prod = st.selectbox("產品項目", get_opts("產品項目"))
            c4, c5, c6 = st.columns(3)
            with c4: f_spec = st.text_input("規格")
            with c5: f_qty = st.text_input("數量", value="1")
            with c6: f_loc = st.text_input("使用地點")
            f_detail = st.text_input("詳細內容 (預購備註)")

            # --- 病患資訊 ---
            st.markdown('<div class="section-head">👤 病患與備註</div>', unsafe_allow_html=True)
            c7, c8, c9 = st.columns(3)
            with c7: f_pat = st.text_input("病人名")
            with c8: f_pid = st.text_input("病例號/ID")
            with c9: f_blood = st.selectbox("抽血人員", get_opts("抽血人員"))
            f_op = st.text_input("手術部位/名稱")
            f_note = st.text_area("🗒️ 其他特殊紀錄備註")

            if st.form_submit_button("🚀 確認提交並同步至雲端"):
                client = get_g_client()
                if client:
                    try:
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc, 
                            f_prod, f_spec, f_qty, f_detail, f_pat, f_pid, f_op, 
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("🎉 資料已同步成功！")
                        st.cache_data.clear() # 強制更新快取
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入失敗: {e}")

    with tab2:
        if not main_df.empty:
            st.dataframe(main_df, use_container_width=True, hide_index=True)
        else:
            st.info("目前雲端尚無紀錄，或資料讀取中...")

    with tab3:
        if not main_df.empty:
            # 尋找包含「預購」關鍵字的欄位
            target_col = next((c for c in main_df.columns if "預購" in str(c) or "內容" in str(c)), None)
            if target_col:
                f_df = main_df[main_df[target_col].astype(str).str.contains("預購", na=False)]
                if not f_df.empty:
                    st.dataframe(f_df, use_container_width=True, hide_index=True)
                else:
                    st.success("目前暫無待追蹤的預購項目。")

if __name__ == "__main__":
    main()
