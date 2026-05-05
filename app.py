import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 基礎設定
st.set_page_config(page_title="黑馬戰鬥機-5萬獲利版", layout="wide")

# 2. 核心 50 檔標的池 (初始名單)
if 'stock_pool' not in st.session_state:
    st.session_state.stock_pool = {
        "2603": "長榮", "2609": "陽明", "2303": "聯電", "3037": "欣興", "00922": "國泰領袖50",
        "2330": "台積電", "2317": "鴻海", "2382": "廣達", "3231": "緯創", "2454": "聯發科",
        "2615": "萬海", "2618": "長榮航", "2409": "友達", "3481": "群創", "2881": "富邦金"
        # 這裡可以持續增加到 50 檔...
    }

# --- 戰情室標題 ---
st.title("🚀 5萬獲利進度戰情室")

# --- 新增功能：顯示並管理標的池 ---
with st.expander("📂 管理監控清單 (目前共有 " + str(len(st.session_state.stock_pool)) + " 檔)"):
    # 顯示目前清單
    st.write("目前監控中：", ", ".join([f"{k} {v}" for k, v in st.session_state.stock_pool.items()]))
    
    st.divider()
    col_add1, col_add2, col_add3 = st.columns([1, 1, 1])
    new_id = col_add1.text_input("輸入代碼 (例: 6239)")
    new_nm = col_add2.text_input("輸入名稱 (例: 力成)")
    if col_add3.button("➕ 新增至清單"):
        if new_id and new_nm:
            st.session_state.stock_pool[new_id] = new_nm
            st.success(f"已加入 {new_nm}")
            st.rerun()

# --- 分頁功能 ---
tab1, tab2 = st.tabs(["🔥 黑馬診斷", "🌙 一夜持股"])

with tab1:
    if st.button("🔄 執行黑馬全掃描", use_container_width=True):
        pool = st.session_state.stock_pool
        sids = [f"{s}.TW" for s in pool.keys()]
        bh_results = []
        
        with st.spinner("正在掃描全台黑馬..."):
            # 使用批次下載提升速度
            data = yf.download(sids, period="1mo", progress=False, auto_adjust=True)
            close_data = data['Close'] if isinstance(data.columns, pd.MultiIndex) else data[['Close']]
            
            for sid_tw in sids:
                sid = sid_tw.replace(".TW", "")
                # 5 日線判斷邏輯
                history = close_data[sid_tw].dropna()
                if history.empty: continue
                
                curr_p = float(history.iloc[-1])
                ma5 = float(history.rolling(5).mean().iloc[-1])
                
                # 判定狀態
                status = "🟢 強勢持有" if curr_p >= ma5 else "🚨 轉弱出場"
                # 計算建議股數 (以 1.5 萬為基準)
                shares = int(15000 / curr_p) if status == "🟢 強勢持有" else 0
                
                bh_results.append({
                    "股票": f"{sid} {pool[sid]}",
                    "現價": round(curr_p, 1),
                    "狀態": status,
                    "建議買進(股)": shares,
                    "預計投入": int(shares * curr_p)
                })
        
        st.dataframe(pd.DataFrame(bh_results), use_container_width=True, hide_index=True)

with tab2:
    st.write("（此處保留原本的一夜持股邏輯...）")
