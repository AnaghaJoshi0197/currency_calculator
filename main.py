import streamlit as st
import requests
import pandas as pd
import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Currency Master",
    page_icon="💱",
    layout="wide"  # <--- CHANGED TO 'WIDE' TO USE FULL SCREEN
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117; 
    }
    div.stButton > button {
        width: 100%;
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        padding: 10px;
        border-radius: 10px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND LOGIC ---
@st.cache_data
def get_rates():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    return response.json()["rates"]

@st.cache_data
def get_historical_data(base, target):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={target}"
    try:
        response = requests.get(url)
        data = response.json()
        if "rates" in data:
            dates = list(data["rates"].keys())
            values = [x[target] for x in data["rates"].values()]
            df = pd.DataFrame({"Date": dates, "Rate": values})
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
            return df
    except:
        return None
    return None

try:
    rates = get_rates()
    currency_list = list(rates.keys())
except:
    st.error("⚠️ Error: Check internet connection.")
    rates = {}
    currency_list = []

# --- 3. FRONTEND UI ---
st.title("💱 Global Currency Converter")
st.markdown("---") 

# CREATE THE MASTER LAYOUT (Left Side vs Right Side)
# [1, 2] means the Right side is 2x bigger than the Left side
left_col, right_col = st.columns([1, 2])

# --- LEFT COLUMN: The Controls ---
with left_col:
    st.subheader("Configuration")
    
    # Stack inputs vertically
    amount = st.number_input("Amount", min_value=0.01, value=1.00)
    from_curr = st.selectbox("From", currency_list, index=currency_list.index("USD") if "USD" in currency_list else 0)
    to_curr = st.selectbox("To", currency_list, index=currency_list.index("INR") if "INR" in currency_list else 0)
    
    st.write("") # Spacer
    
    # The Button
    calculate = st.button("Convert Now")

    # Placeholder for result (so it appears inside the left column)
    result_container = st.container()


# --- LOGIC TRIGGER ---
if calculate:
    if from_curr in rates and to_curr in rates:
        
        # 1. LIVE CALCULATION
        initial_rate = rates[from_curr]
        target_rate = rates[to_curr]
        result = amount * (target_rate / initial_rate)
        
        # Show Result in Left Column
        with left_col:
            st.markdown("---")
            st.success("Success!")
            st.metric(label=f"{amount} {from_curr} =", value=f"{result:,.2f} {to_curr}")
            st.caption(f"1 {from_curr} = {(target_rate/initial_rate):.4f} {to_curr}")

        # 2. CHART IN RIGHT COLUMN
        with right_col:
            st.subheader(f"📈 1 Year Trend ({from_curr} vs {to_curr})")
            
            with st.spinner("Analyzing market data..."):
                chart_data = get_historical_data(from_curr, to_curr)
                
                if chart_data is not None:
                    # Draw a big chart
                    st.line_chart(chart_data, color="#00FF00", height=400)
                else:
                    st.warning("History not available for this pair.")
    else:
        with left_col:
            st.error("Error fetching rates.")

# If button not clicked yet, show a welcome message on the right
elif not calculate:
    with right_col:
        st.info("👈 Enter an amount and click 'Convert Now' to see the exchange rate and historical trend.")