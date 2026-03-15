import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

# 頁面配置：標題貼頂，字體放大
st.set_page_config(page_title="2026 慈榛驊管理系統", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1rem; max-width: 1100px;}
    h1 {text-align: center; font-size: 28px !important; margin-bottom: 20px;}
    label {font-size: 18px !important; font-weight: bold !important; color: #1E1E1E !important;}
    .stSelectbox div[data-baseweb="select"] {font-size: 18px !important;}
    input {font-size: 18px !important;}
    </style>
    """, unsafe_allow_html=True)

# 試算表 ID
SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

# --- 根據佰哥提供資料，直接內建選單，不再讀取 Settings 分頁 ---
LIST_PRICE = ["單次批價使用", "批價 + 預購", "使用前次預購", "使用他人預購", "純預購寄庫使用"]
LIST_HOSP = ["花蓮慈濟", "玉里慈濟", "關山慈濟", "門諾醫院", "國軍花蓮", "部立花蓮", "部立台東", "鳳林榮民", "玉里榮民", "台東榮民", "台東聖母", "東基", "宜蘭陽大", "羅東博愛", "羅東聖母", "其他"]
LIST_DEPT = ["骨科", "牙科", "眼科", "急診", "疼痛科", "復健科", "泌尿科", "婦產科", "神經外科", "整形外科", "胸腔外科", "一般外科", "耳鼻喉科", "大腸直腸科", "其他"]
LIST_PROD = ["3E PRP", "倍濃偲PRP", "其他(除PRP以外的產品)"]
LIST_BLOOD = ["佳瑾", "虹琳", "又溶", "孟庭", "筱涵", "無", "其他"]

def get_g_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds)
    except:
        return None

def main():
    st.markdown("<h1>📋 『2026』年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    
    with st.form("main_form", clear_on_submit=True):
        # 嚴格按照截圖 image_519458.png 的 A 到 P 欄位順序排列
        c1, c2, c3 = st.columns(3)
        
        with c1:
            f_date = st.date_input("使用日期 (A欄)", datetime.now()) 
            f_price = st.selectbox("批價內容 (B欄)", LIST_PRICE)
            f_hosp = st.selectbox("使用醫院 (C欄)", LIST_HOSP)
            f_dept = st.selectbox("使用科別 (D欄)", LIST_DEPT)
            f_doc = st.text_input("醫師姓名 (E欄)")
            
        with c2:
            f_prod = st.selectbox("產品項目 (F欄)", LIST_PROD)
            f_spec = st.text_input("規格 (G欄)")
            f_qty = st.text_input("數量 (H欄)", value="1")
            f_content = st.text_input("使用產品內容-含預購 (I欄)")
            f_pat = st.text_input("病人名 (J欄)")
            
        with c3:
            f_pid = st.text_input("病例號/ID (K欄)")
            f_op = st.text_input("手術名稱/使用部位 (L欄)")
            f_loc = st.text_input("使用地點 (M欄)")
            f_blood = st.selectbox("抽血人員 (N欄)", LIST_BLOOD)
            f_staff = st.text_input("跟刀(操作)人員 (O欄)")

        f_note = st.text_area("備註 (P欄)")

        if st.form_submit_button("🚀 提交數據"):
            client = get_g_client()
            if client:
                try:
                    ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                    # 精準排列數據：日期, 批價, 醫院, 科別, 醫師, 產品, 規格, 數量, 內容, 病人, ID, 部位, 地點, 抽血, 跟刀, 備註
                    ws.append_row([
                        f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                        f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                        f_loc, f_blood, f_staff, f_note
                    ])
                    st.success("✅ 資料錄入成功，已同步至雲端！")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"寫入失敗，請確認回應試算表分頁存在：{e}")
            else:
                st.error("❌ 雲端連線金鑰失效，請檢查 Streamlit Secrets 設定。")

if __name__ == "__main__":
    main()
