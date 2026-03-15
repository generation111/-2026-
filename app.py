import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 頁面基礎設定
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

# CSS 強制貼頂與美化
st.markdown("""<style>.block-container {padding-top: 1rem;} h1 {text-align: center; font-size: 26px !important; margin-bottom: 20px;}</style>""", unsafe_allow_html=True)

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # 確保抓取 Streamlit Cloud 後台設定的 Secrets
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 金鑰授權失敗，請確認 Secrets 設定。詳細錯誤：{e}")
        return None

def load_settings():
    client = get_g_client()
    if not client: return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # 依照您的截圖分頁名稱為 Settings
        ws = sh.worksheet("Settings")
        # 抓取所有原始資料
        data = ws.get_all_values()
        if not data: return pd.DataFrame()
        
        # 找到包含標題的那一行 (避免 A1 是空白的狀況)
        df = pd.DataFrame(data[1:], columns=data[0])
        # 強制清除欄位名稱的所有空格 (這最常導致連動失敗)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ 讀取選單失敗：{e}")
        return pd.DataFrame()

def main():
    st.markdown("<h1>📋 『2026』年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    # 載入最新的選單資料
    df_set = load_settings()

    tab1, tab2, tab3 = st.tabs(["📝 資料錄入", "📊 年度明細清單", "🔔 須回診名單"])

    with tab1:
        with st.form("main_form", clear_on_submit=True):
            # 選單抓取輔助工具
            def get_opts(col_name):
                if not df_set.empty and col_name in df_set.columns:
                    # 抓取唯一值並過濾掉空值
                    vals = [str(v).strip() for v in df_set[col_name].unique() if v and str(v).strip()]
                    return vals if vals else ["(無資料)"]
                return ["(欄位未找到)"]

            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("使用日期", datetime.now())
                f_price = st.selectbox("批價內容", get_opts("批價內容"))
                f_hosp = st.selectbox("使用醫院", get_opts("使用醫院"))
                f_dept = st.selectbox("使用科別", get_opts("使用科別"))
            with c2:
                f_prod = st.selectbox("產品項目", get_opts("產品項目"))
                f_spec = st.text_input("規格")
                f_qty = st.text_input("數量", value="1")
                f_content = st.text_input("使用產品內容(含預購)")
            with c3:
                f_pid = st.text_input("病例號/ID")
                f_op = st.text_input("手術名稱/使用部位")
                f_loc = st.text_input("使用地點")
                f_blood = st.selectbox("抽血人員", get_opts("抽血人員"))

            # 其他文字輸入欄位
            f_doc = st.text_input("醫師姓名")
            f_pat = st.text_input("病人名")
            f_staff = st.text_input("跟刀(操作)人員")
            f_note = st.text_area("備註")

            if st.form_submit_button("🚀 提交數據並同步雲端"):
                client = get_g_client()
                if client:
                    try:
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        # 依照回應試算表欄位順序寫入
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                            f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("🎉 資料已成功錄入試算表！")
                        st.cache_data.clear() # 提交後清除快取
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入失敗：{e}")

    with tab2:
        st.info("資料清單加載中...")

if __name__ == "__main__":
    main()
