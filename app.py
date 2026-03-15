import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import time

# 頁面配置
st.set_page_config(page_title="2026 年度跟刀記錄管理系統", layout="wide")

# --- CSS 視覺對齊修正：終極像素微調 ---
st.markdown("""
    <style>
    /* 基礎容器優化 */
    .block-container { padding-top: 1.5rem !important; max-width: 1100px; }
    h1 { text-align: center; font-size: 28px !important; margin-bottom: 20px !important; }

    /* 備註輸入框設定 */
    .stTextArea textarea {
        height: 38px !important; 
        min-height: 38px !important;
    }
    
    label { font-size: 14px !important; font-weight: bold !important; color: #34495e !important; }

    /* 核心對齊修正：將按鈕容器整體上提，對齊 Label 頂端 */
    div.stButton {
        transform: translateY(-35px) !important; /* 從 -28px 增加到 -35px，對齊備註文字頂部 */
    }

    div.stButton > button {
        width: 100%; 
        height: 82px !important; /* 維持完整塊狀高度 */
        font-size: 18px !important; 
        font-weight: bold !important; 
        background-color: #007bff; 
        color: white; 
        border-radius: 6px;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* 確保欄位底部對齊邏輯 */
    [data-testid="column"] {
        display: flex;
        align-items: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)

SPREADSHEET_ID = "1w2BDsPHHxgaz6PJhoPLXdh0UQJplA6rr42wLoLQIM9s"

# --- 選單內容 ---
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
    except Exception: return None

def main():
    st.markdown("<h1>📋 2026 年度跟刀記錄管理系統</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🖋️ 資料登錄", "📊 歷史紀錄", "🔍 預購追蹤"])

    client = get_g_client()
    main_df = pd.DataFrame()
    if client:
        try:
            ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
            data = ws.get_all_records()
            if data: main_df = pd.DataFrame(data)
        except Exception: pass

    with tab1:
        with st.form("main_form", clear_on_submit=True):
            # 第一列 & 第二列
            c1, c2, c3 = st.columns(3)
            with c1:
                f_date = st.date_input("使用日期", datetime.now()) 
                f_price = st.selectbox("批價內容", LIST_PRICE, index=1)
                f_hosp = st.selectbox("使用醫院", LIST_HOSP, index=0)
                f_dept = st.selectbox("使用科別", LIST_DEPT, index=0)
            with c2:
                f_doc = st.text_input("醫師姓名")
                f_prod = st.selectbox("產品項目", LIST_PROD, index=0)
                f_spec = st.text_input("規格")
                f_qty = st.text_input("數量", value="1")
            with c3:
                f_content = st.text_input("使用產品內容-含預購")
                f_pat = st.text_input("病人名")
                f_pid = st.text_input("病例號/ID")
                f_op = st.text_input("手術名稱/使用部位")

            c4, c5, c6 = st.columns(3)
            with c4: f_loc = st.text_input("使用地點")
            with c5: f_blood = st.selectbox("抽血人員", LIST_BLOOD, index=0)
            with c6: f_staff = st.text_input("跟刀(操作)人員")

            # --- 第三區：對齊位移修正 ---
            c7, c8, spacer = st.columns([6.5, 2.5, 1.0]) 
            with c7:
                f_note = st.text_area("備註")
            with c8:
                submit_btn = st.form_submit_button("🚀 提交數據")

            if submit_btn:
                if client:
                    try:
                        ws = client.open_by_key(SPREADSHEET_ID).worksheet("回應試算表")
                        ws.append_row([
                            f_date.strftime("%Y/%m/%d"), f_price, f_hosp, f_dept, f_doc,
                            f_prod, f_spec, f_qty, f_content, f_pat, f_pid, f_op,
                            f_loc, f_blood, f_staff, f_note
                        ])
                        st.success("✅ 提交成功！")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"錯誤：{e}")

    with tab2:
        if not main_df.empty: st.dataframe(main_df, use_container_width=True, hide_index=True)
    with tab3:
        if not main_df.empty:
            cols = main_df.columns.tolist()
            search_col = next((c for c in cols if "預購" in str(c)), None)
            if search_col:
                f_df = main_df[main_df[search_col].astype(str).str.contains("預購", na=False)]
                if not f_df.empty: st.dataframe(f_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
