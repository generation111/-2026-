import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

st.set_page_config(page_title="2026 慈榛驊管理系統", layout="wide")

# CSS 強制字體大小，不再縮小，確保平板好讀
st.markdown("""
    <style>
    .block-container {padding-top: 1rem;}
    h1 {text-align: center; font-size: 28px !important; color: #1E1E1E;}
    label {font-size: 18px !important; font-weight: bold !important; color: #34495e !important;}
    .stSelectbox div[data-baseweb="select"] {font-size: 18px !important;}
    </style>
    """, unsafe_allow_html=True)

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ 金鑰連線失敗，請檢查 Secrets 設定。")
        return None

def load_hard_coded_menus():
    client = get_g_client()
    if not client: return {}
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        ws = sh.worksheet("Settings")
        # 直接抓取整張表，不靠標題對齊
        all_data = ws.get_all_values()
        if len(all_data) < 2: return {}
        
        df = pd.DataFrame(all_data)
        
        # 依照 Settings 分頁的物理位置強行抓取 (0 是 A 欄, 1 是 B 欄...)
        # 假設：A=批價, B=使用醫院, C=使用科別, D=產品項目, E=抽血人員
        menus = {
            "price": [v for v in df[0].unique() if v and v != df[0][0]],
            "hosp":  [v for v in df[1].unique() if v and v != df[1][0]],
            "dept":  [v for v in df[2].unique() if v and v != df[2][0]],
            "prod":  [v for v in df[3].unique() if v and v != df[3][0]],
            "blood": [v for v in df[4].unique() if v and v != df[4][0]]
        }
        return menus
    except Exception as e:
        st.error(f"❌ 讀取 Settings 物理欄位失敗: {e}")
        return {}

def main():
    st.markdown("<h1>📋 慈榛驊業務管理系統</h1>", unsafe_allow_html=True)
    
    # 載入選單
    m = load_hard_coded_menus()

    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_date = st.date_input("使用日期 (第一欄)", datetime.now())
            f_price = st.selectbox("批價內容", m.get("price", ["載入中..."]))
            f_hosp = st.selectbox("使用醫院", m.get("hosp", ["載入中..."]))
            f_dept = st.selectbox("使用科別", m.get("dept", ["載入中..."]))
        with c2:
            f_doc = st.text_input("醫師姓名")
            f_prod = st.selectbox("產品項目", m.get("prod", ["載入中..."]))
            f_spec = st.text_input("規格")
            f_qty = st.text_input("數量", value="1")
        with c3:
            f_content = st.text_input("使用產品內容(含預購)")
            f_pat = st.text_input("病人名")
            f_pid = st.text_input("病例號/ID")
            f_op = st.text_input("手術名稱/使用部位")

        f_loc = st.text_input("使用地點")
        f_blood = st.selectbox("抽血人員", m.get("blood", ["載入中..."]))
        f_staff = st.text_input("跟刀人員")
        f_note = st.text_area("備註")

        if st.form_submit_button("🚀 確認提交並寫入試算表"):
            client = get_g_client()
            if client:
                try:
                    ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                    # 按照您要求的第一欄日期順序寫入
                    ws.append_row([
                        f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                        f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                        f_loc, f_blood, f_staff, f_note
                    ])
                    st.success("🎉 資料同步成功！")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")

if __name__ == "__main__":
    main()
