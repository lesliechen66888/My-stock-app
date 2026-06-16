import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import re

# 網頁基本設定
st.set_page_config(page_title="個人股票 AI 分析平台", layout="wide")
st.title("📈 個人專屬股票分析平台")
st.caption("結合每日投資筆記與市場大數據的滾動式分析系統")

# 側邊欄：盤前提醒
st.sidebar.header("⏰ 盤前提醒")
pre_market_note = st.sidebar.text_area(
    "輸入今日開盤前的重要提醒：",
    value="留意美股科技股回檔賣壓，注意記憶體現貨價走勢。",
    height=150
)

# 主畫面：每日投資內容輸入
st.header("✍️ 每日投資內容輸入")
investment_content = st.text_area(
    "請貼上今天的投資分析、籌碼觀察或新聞內容：",
    value="今天外資持續買超南亞科(2408)，雖然消費性電子需求平平，但DDR5升級潮可能帶動下半年營運。另外華邦電(2344)投信也有小幅試單。",
    height=200
)

# 觸發分析按鈕
if st.button("🚀 執行滾動式大數據分析"):
    st.success("成功接收今日內容！正在擷取股票資訊...")
    
    # 利用正規表達式尋找台灣股票代碼 (4位數字)
    stock_ids = re.findall(r'\b\d{4}\b', investment_content)
    # 去除重複的代號
    stock_ids = list(set(stock_ids))
    
    if not stock_ids:
        st.warning("偵測不到明確的 4 位數台灣股票代號，請確保內容包含如 '2408' 或 '2344' 的字樣。")
    else:
        st.write(f"🔍 偵測到個股代號： {', '.join(stock_ids)}")
        
        # 針對偵測到的每檔股票進行大數據抓取與分析
        for stock_id in stock_ids:
            st.markdown(f"---")
            st.subheader(f"📊 個股追蹤：{stock_id}.TW")
            
            # 1. 抓取大數據 (yfinance)
            # 台股代碼在 yfinance 需要加上 .TW
            ticker = f"{stock_id}.TW"
            try:
                stock_data = yf.Ticker(ticker)
                # 抓取最近一個月的歷史股價
                df = stock_data.history(period="1mo")
                
                if df.empty:
                    st.error(f"找不到 {ticker} 的股價資料，請確認代號是否正確。")
                    continue
                
                # 2. 顯示大數據視覺化圖表
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("📈 最近 30 天收盤價走勢")
                    st.line_chart(df['Close'])
                    
                with col2:
                    st.write("🔢 最新市況數據")
                    latest_close = df['Close'].iloc[-1]
                    latest_vol = df['Volume'].iloc[-1]
                    prev_close = df['Close'].iloc[-2]
                    price_change = latest_close - prev_close
                    pct_change = (price_change / prev_close) * 100
                    
                    st.metric(label="最新收盤價", value=f"{latest_close:.2f} 元", delta=f"{price_change:.2f} ({pct_change:.2f}%)")
                    st.write(f"今日成交量： {latest_vol:,} 股")
                
                # 3. 滾動式 AI 分析區塊
                st.markdown(f"🤖 **AI 滾動式投資建議 ({stock_id})**")
                
                # 這裡未來可以串接 Gemini API 傳入：盤前提醒 + 投資內容 + 歷史股價 df
                # 目前先以系統模擬的邏輯結構呈現
                st.info(
                    f"【結合今日筆記與大數據解讀】\n\n"
                    f"1. **筆記多空解讀**：今日輸入內容提及「外資買超/投信試單」，籌碼面偏向正面。\n"
                    f"2. **技術面大數據**：目前該股收盤價為 {latest_close:.2f} 元，對比過去一個月走勢，處於相對位置。綜合今日盤前提醒之「美股科技股回檔」，建議開盤不宜過度追高。\n"
                    f"3. **滾動式建議**：建議設定分批布局策略，靜待盤中賣壓消化，並持續觀察報價變化。"
                )
                
            except Exception as e:
                st.error(f"處理 {ticker} 時發生錯誤: {e}")
