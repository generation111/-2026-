import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

st.markdown("""<style>.block-container {padding-top: 1rem;} h1 {text-align: center; font-size: 24px !important;}</style>""", unsafe_allow_html=True)

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Secrets 金鑰連線失敗，請檢查後台設定。")
        return None

def load_settings():
    client = get_g_client()
    if not client: return {}
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet("Settings")
        data = ws.get_all_values()
        if len(data) < 2: return {}
        
        # 轉成 DataFrame 並清除所有欄位名稱的空格
        df = pd.DataFrame(data[1:], columns=data[0])
        df.columns = df.columns.str.strip()
        
        # 將每一欄轉成清單，過濾空值
        res = {}
        for col in df.columns:
            res[col] = [v.strip() for v in df[col].unique() if v and v.strip()]
        return res
    except Exception as e:
        st.error(f"❌ 讀取 Settings 失敗，請確認分頁名稱是否完全正確：{e}")
        return {}

def main():
    st.markdown("<h1>📋 『2026』年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    # 載入選單字典
    menu_data = load_settings()

    with st.form("main_form", clear_on_submit=True):
        def get_opts(name):
            return menu_data.get(name, ["(載入中或欄位不符)"])

        c1, c2, c3 = st.columns(3)
        with c1:
            # 依據您提醒的順序：使用日期是第一欄
            f_date = st.date_input("使用日期", datetime.now())
            f_price = st.selectbox("批價內容", get_opts("批價內容"))
            f_hosp = st.selectbox("使用醫院", get_opts("使用醫院"))
            f_dept = st.selectbox("使用科別", get_opts("使用科別"))
        with c2:
            f_doc = st.text_input("醫師姓名")
            f_prod = st.selectbox("產品項目", get_opts("產品項目"))
            f_spec = st.text_input("規格")
            f_qty = st.text_input("數量", value="1")
        with c3:
            f_content = st.text_input("使用產品內容(含預購)")
            f_pat = st.text_input("病人名")
            f_pid = st.text_input("病例號/ID")
            f_op = st.text_input("手術名稱/使用部位")

        f_loc = st.text_input("使用地點")
        f_blood = st.selectbox("抽血人員", get_opts("抽血人員"))
        f_staff = st.text_input("跟刀人員")
        f_note = st.text_area("備註")

        if st.form_submit_button("🚀 確認提交並存檔"):
            client = get_g_client()
            if client:
                try:
                    ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                    # 寫入順序：日期, 批價, 醫院, 科別, 醫師, 產品, 規格, 數量, 內容, 病人, ID, 部位, 地點, 抽血, 跟刀, 備註
                    ws.append_row([
                        f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                        f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                        f_loc, f_blood, f_staff, f_note
                    ])
                    st.success("🎉 資料已成功錄入！")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")

if __name__ == "__main__":
    main()
