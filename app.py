import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import re
import google.generativeai as genai

# 網頁基本設定
st.set_page_config(page_title="個人股票 AI 分析平台", layout="wide")
st.title("📈 個人專屬股票分析平台")
st.caption("結合每日投資筆記、大數據與 Gemini AI 的滾動式分析系統")

# 設定 Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
except Exception as e:
    ai_ready = False
    st.error("⚠️ 尚未偵測到 Gemini API Key，請確認是否已在 Streamlit Secrets 中設定。")

# 側邊欄設定
st.sidebar.header("⏰ 盤前提醒")
pre_market_note = st.sidebar.text_area(
    "輸入今日開盤前的重要提醒：",
    value="留意美股科技股回檔賣壓，注意記憶體現貨價走勢。",
    height=150
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 常態追蹤清單")
manual_stocks = st.sidebar.text_input(
    "文章沒寫到，但今天特別想盯盤的個股代號 (請用逗號分隔)：",
    value="2408, 2344"
)

# 主畫面：每日投資內容輸入
st.header("✍️ 每日投資內容輸入")
investment_content = st.text_area(
    "請貼上今天的投資分析、籌碼觀察或新聞內容：",
    height=250
)

# 建立常用股票的「中文對照字典」
stock_mapping = {
    "南亞科": "2408",
    "華邦電": "2344",
    "旺宏": "2337",
    "台積電": "2330",
    "聯發科": "2454",
    "鴻海": "2317"
}

# 觸發分析按鈕
if st.button("🚀 執行滾動式大數據與 AI 分析"):
    if not investment_content:
        st.warning("請輸入今日的投資內容喔！")
    else:
        st.success("成功接收今日內容！正在擷取股票資訊並呼叫 AI 進行分析...")
        
        # 收集要分析的股票代號名單
        stock_ids = []
        stock_ids.extend(re.findall(r'\b\d{4}\b', investment_content))
        for name, code in stock_mapping.items():
            if name in investment_content:
                stock_ids.append(code)
        if manual_stocks:
            manual_list = [s.strip() for s in manual_stocks.split(',') if s.strip().isdigit()]
            stock_ids.extend(manual_list)
            
        stock_ids = list(set(stock_ids))
        
        if not stock_ids:
            st.info("今日內容偏向大盤總經分析，無偵測到特定個股。")
        else:
            st.write(f"🔍 今日系統追蹤個股： {', '.join(stock_ids)}")
            
            for stock_id in stock_ids:
                st.markdown(f"---")
                st.subheader(f"📊 個股追蹤與 AI 解讀：{stock_id}.TW")
                
                ticker = f"{stock_id}.TW"
                try:
                    # 抓取大數據
                    stock_data = yf.Ticker(ticker)
                    df = stock_data.history(period="1mo")
                    
                    if df.empty:
                        st.error(f"找不到 {ticker} 的股價資料，請確認代號是否正確。")
                        continue
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.line_chart(df['Close'])
                        
                    with col2:
                        latest_close = df['Close'].iloc[-1]
                        latest_vol = df['Volume'].iloc[-1]
                        prev_close = df['Close'].iloc[-2]
                        price_change = latest_close - prev_close
                        pct_change = (price_change / prev_close) * 100
                        
                        st.metric(label="最新收盤價", value=f"{latest_close:.2f} 元", delta=f"{price_change:.2f} ({pct_change:.2f}%)")
                        st.write(f"今日成交量： {latest_vol:,} 股")
                    
                    # 串接 Gemini AI 進行分析
                    st.markdown(f"🤖 **Gemini AI 滾動式投資建議**")
                    if ai_ready:
                        with st.spinner("AI 正在閱讀您的筆記與大數據，努力思考中..."):
                            # 這是告訴 AI 它要做什麼的「提示詞 (Prompt)」
                            prompt = f"""
                            你是一位專業的台股分析師。請綜合以下資訊，針對台灣股票代號 {stock_id} 給出簡短、客觀的分析與操作建議。
                            
                            1. 投資者盤前提醒：{pre_market_note}
                            2. 投資者今日閱讀的市場內容：{investment_content}
                            3. 該股最新大數據：收盤價 {latest_close:.2f} 元，今日漲跌幅 {pct_change:.2f}%。
                            
                            請直接輸出 3 到 4 條 bullet points 的重點分析，並給出「偏多、偏空或觀望」的總結。語氣請保持專業、精煉。
                            """
                            
                            response = model.generate_content(prompt)
                            st.write(response.text)
                    else:
                        st.info("AI 尚未連線，請確認 API Key 設定。")
                        
                except Exception as e:
                    st.error(f"處理 {ticker} 時發生錯誤: {e}")
