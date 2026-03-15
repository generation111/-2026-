import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 頁面配置
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

# 1. 直接內建選單（完全跳過 Settings 分頁連動，保證不卡住）
LIST_PRICE = ["單次批價使用", "批價 + 預購", "使用前次預購", "使用他人預購", "純預購寄庫使用"]
LIST_HOSP = ["花蓮慈濟", "玉里慈濟", "關山慈濟", "門諾醫院", "國軍花蓮", "部立花蓮", "部立台東", "鳳林榮民", "玉里榮民", "台東榮民", "台東聖母", "東基", "宜蘭陽大", "羅東博愛", "羅東聖母", "其他"]
LIST_DEPT = ["骨科", "牙科", "眼科", "急診", "疼痛科", "復健科", "泌尿科", "婦產科", "神經外科", "整形外科", "胸腔外科", "一般外科", "耳鼻喉科", "大腸直腸科", "其他"]
LIST_PROD = ["3E PRP", "倍濃偲PRP", "其他(除PRP以外的產品)"]
LIST_BLOOD = ["佳瑾", "虹琳", "又溶", "孟庭", "筱涵", "無", "其他"]

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

def get_g_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except:
        return None

def main():
    st.markdown("<h1 style='text-align: center;'>📋 2026 年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            f_date = st.date_input("使用日期", datetime.now())
            f_price = st.selectbox("批價內容", LIST_PRICE)
            f_hosp = st.selectbox("使用醫院", LIST_HOSP)
            f_dept = st.selectbox("使用科別", LIST_DEPT)
        
        with col2:
            f_doc = st.text_input("醫師姓名")
            f_prod = st.selectbox("產品項目", LIST_PROD)
            f_spec = st.text_input("規格")
            f_qty = st.text_input("數量", value="1")
            
        with col3:
            f_content = st.text_input("使用產品內容-含預購")
            f_pat = st.text_input("病人名")
            f_pid = st.text_input("病例號/ID")
            f_op = st.text_input("手術名稱/使用部位")

        f_loc = st.text_input("使用地點")
        f_blood = st.selectbox("抽血人員", LIST_BLOOD)
        f_staff = st.text_input("跟刀(操作)人員")
        f_note = st.text_area("備註")

        if st.form_submit_button("🚀 提交數據"):
            client = get_g_client()
            if client:
                try:
                    ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                    ws.append_row([
                        f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                        f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                        f_loc, f_blood, f_staff, f_note
                    ])
                    st.success("✅ 資料錄入成功！")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗：{e}")

if __name__ == "__main__":
    main()
