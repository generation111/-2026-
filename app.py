import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 基本配置
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

# 試算表 ID
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        # 直接對應 Streamlit 後台 Secrets
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 連線失敗，請檢查 Secrets 設定：{e}")
        return None

def load_settings():
    client = get_g_client()
    if not client: return pd.DataFrame()
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # 根據 image_521837.png，分頁名稱是 Settings
        ws = sh.worksheet("Settings")
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ 讀取『Settings』分頁失敗。請確認試算表內分頁名稱是否正確。報錯：{e}")
        return pd.DataFrame()

def main():
    st.title("📋 『2026』年度跟刀記錄管理系統")
    
    # 載入選單
    df_set = load_settings()

    if df_set.empty:
        st.warning("⚠️ 系統目前抓不到選單資料。請檢查：1. 試算表是否已共用給 Service Account 2. 分頁名稱是否為 Settings")
        return

    # 清除欄位空格，避免抓不到
    df_set.columns = df_set.columns.str.strip()

    with st.form("main_form", clear_on_submit=True):
        def get_list(col_name):
            if col_name in df_set.columns:
                return [str(v).strip() for v in df_set[col_name].unique() if v and str(v).strip()]
            return ["(找不到欄位)"]

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
        f_staff = st.text_input("跟刀人員")
        f_note = st.text_area("備註")

        if st.form_submit_button("🚀 提交數據"):
            client = get_g_client()
            try:
                # 寫入至「回應試算表」分頁
                ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                ws.append_row([
                    f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                    f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                    f_loc, f_blood, f_staff, f_note
                ])
                st.success("🎉 資料已成功寫入試算表！")
            except Exception as e:
                st.error(f"寫入失敗：{e}")

if __name__ == "__main__":
    main()
