import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Strategic Investment Teacher",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, modern look
st.markdown("""
<style>
    .st-emotion-cache-18ni7ap { padding-top: 0rem; }
    .st-emotion-cache-p2w5e4 { padding-top: 0rem; }
    .st-emotion-cache-1j0bbv3 {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .st-emotion-cache-1r4qj8a {
        border-radius: 0.5rem;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
    }
    .stMetric > div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #64748b;
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .st-emotion-cache-1v0s1w-Tab-content {
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Educational Content & Data Functions ---
EDUCATIONAL_CONTENT = {
    "mutual_funds": {"title": "📊 Mutual Funds", "content": """**What are Mutual Funds?**\n- Pool of money from many investors\n- Professionally managed by fund managers\n- Diversified portfolio of stocks, bonds, or other securities\n- Suitable for long-term wealth creation\n\n**Types:**\n- Equity Funds (High risk, high return)\n- Debt Funds (Low risk, moderate return)\n- Hybrid Funds (Balanced approach)"""},
    "stocks": {"title": "📈 Stocks", "content": """**What are Stocks?**\n- Ownership shares in a company\n- Potential for high returns but volatile\n- Requires research and market knowledge\n- Best for long-term investment\n\n**Key Points:**\n- Dividend income + Capital appreciation\n- Market risk is high\n- Liquidity is good"""},
    "fd": {"title": "🏛️ Fixed Deposits", "content": """**What are Fixed Deposits?**\n- Safe investment with guaranteed returns\n- Fixed interest rate for specific tenure\n- No market risk involved\n- Lower returns compared to equity\n\n**Features:**\n- Capital protection\n- Predictable returns\n- Various tenure options"""},
    "bonds": {"title": "📜 Bonds", "content": """**What are Bonds?**\n- Debt instruments issued by companies/government\n- Regular interest payments (coupon)\n- Lower risk than stocks\n- Good for steady income\n\n**Types:**\n- Government Bonds (Safest)\n- Corporate Bonds (Higher yield)\n- Tax-saving bonds"""},
    "aif": {"title": "🎯 Alternative Investment Funds", "content": """**What are AIFs?**\n- Privately pooled investment funds\n- Higher minimum investment\n- Less regulated than mutual funds\n- Potential for higher returns\n\n**Categories:**\n- Category I: Social ventures, SME funds\n- Category II: PE, Debt funds\n- Category III: Hedge funds"""},
    "risk_free_rate": {"title": "🛡️ Risk-Free Rate", "content": """**What is Risk-Free Rate?**\n- Rate of return on investment with zero risk\n- Usually 10-year Government Bond yield\n- Used as benchmark for other investments\n- Currently around 7% in India\n\n**Why Important?**\n- Base for calculating expected returns\n- Helps in risk assessment\n- Used in CAPM model"""},
    "beta": {"title": "📊 Beta", "content": """**What is Beta?**\n- Measures stock's volatility relative to market\n- Beta = 1: Moves with market\n- Beta > 1: More volatile than market\n- Beta < 1: Less volatile than market\n\n**Usage in Calculations:**\n- Helps determine expected returns\n- Risk assessment tool\n- Portfolio construction"""},
    "standard_deviation": {"title": "📈 Standard Deviation", "content": """**What is Standard Deviation?**\n- Measures investment volatility\n- Higher SD = Higher risk\n- Shows how much returns deviate from average\n- Key risk metric for investments\n\n**In Investment Decisions:**\n- Risk assessment\n- Portfolio optimization\n- Return expectation setting"""}
}

def show_educational_popup(content_key):
    """Show educational content in an expander"""
    content = EDUCATIONAL_CONTENT[content_key]
    with st.expander(f"💡 Learn about {content['title']}", expanded=False):
        st.markdown(content['content'])

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_amfi_data():
    """Fetch real-time mutual fund data from AMFI"""
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.split('\n')
            data = []
            current_fund_house = ""
            for line in lines:
                line = line.strip()
                if not line: continue
                if not line[0].isdigit():
                    if "Mutual Fund" in line: current_fund_house = line
                else:
                    parts = line.split(';')
                    if len(parts) >= 6:
                        try:
                            scheme_name = parts[3]
                            nav = float(parts[4])
                            date = parts[5]
                            plan_type = "Direct" if "Direct" in scheme_name.upper() else "Regular"
                            expense_ratio = 1.2 if plan_type == 'Direct' else 2.0
                            data.append({'fund_house': current_fund_house,'scheme_name': scheme_name,'nav': nav,'date': date,'plan_type': plan_type,'expense_ratio': expense_ratio})
                        except (ValueError, IndexError): continue
            
            df = pd.DataFrame(data)
            return df
        else:
            st.error("Failed to fetch live data from AMFI. Using sample data.")
            return create_sample_mf_data()
    except Exception as e:
        st.error(f"Unable to fetch live data: {e}. Using sample data.")
        return create_sample_mf_data()

def create_sample_mf_data():
    """Create sample mutual fund data"""
    sample_data = []
    fund_types = ['Large Cap', 'Mid Cap', 'Small Cap', 'Multi Cap', 'Debt', 'Hybrid']
    fund_houses = ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Aditya Birla']
    for i in range(100):
        fund_house = np.random.choice(fund_houses)
        fund_type = np.random.choice(fund_types)
        plan_type = np.random.choice(['Direct', 'Regular'])
        sample_data.append({'fund_house': f"{fund_house} Mutual Fund", 'scheme_name': f"{fund_house} {fund_type} Fund - {plan_type} Plan", 'nav': round(np.random.uniform(10, 500), 2), 'date': datetime.now().strftime('%d-%b-%Y'), 'plan_type': plan_type, 'expense_ratio': 1.2 if plan_type == 'Direct' else 2.0})
    return pd.DataFrame(sample_data)

def calculate_investment_returns(amount, years, monthly_investment, allocation, scenario='normal'):
    """Calculate investment returns for different scenarios"""
    asset_returns = {
        'normal': {'mutual_funds': 0.12, 'stocks': 0.15, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.18},
        'bullish': {'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.28},
        'bearish': {'mutual_funds': 0.04, 'stocks': 0.02, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.08}
    }
    asset_risks = {'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.02, 'bonds': 0.05, 'aif': 0.30}
    asset_betas = {'mutual_funds': 0.85, 'stocks': 1.2, 'fd': 0.0, 'bonds': 0.1, 'aif': 1.5}
    
    returns = asset_returns[scenario]
    risk_free_rate = 0.07
    
    portfolio_return = sum(allocation[asset] * returns[asset] for asset in allocation)
    portfolio_risk = sum(allocation[asset] * asset_risks[asset] for asset in allocation)
    portfolio_beta = sum(allocation[asset] * asset_betas[asset] for asset in allocation)
    
    months = years * 12
    monthly_return = portfolio_return / 12
    
    fv_lumpsum = amount * (1 + portfolio_return) ** years
    fv_monthly = monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return) if monthly_investment > 0 and monthly_return > 0 else 0
    
    total_future_value = fv_lumpsum + fv_monthly
    total_investment = amount + (monthly_investment * months)
    
    return {'total_investment': total_investment, 'future_value': total_future_value, 'gains': total_future_value - total_investment, 'portfolio_return': portfolio_return, 'portfolio_risk': portfolio_risk, 'portfolio_beta': portfolio_beta}

# --- Main App Logic ---
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Strategic Investment Teacher</h1>
        <p>Plan your financial future with sophisticated calculations and real-time data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.warning("""
    **⚠️ IMPORTANT DISCLAIMER:** This application is for educational purposes only. The returns and calculations shown are based on mathematical models and should not be considered investment advice. Past performance is not a guarantee of future results.
    """)
    
    with st.spinner("Fetching real-time mutual fund data..."):
        mf_data = fetch_amfi_data()
    st.success(f"✅ Loaded {len(mf_data)} mutual fund schemes.")

    # Sidebar for inputs
    st.sidebar.header("📊 Investment Parameters")
    
    with st.sidebar.expander("💰 Investment Type", expanded=True):
        investment_type = st.radio("Choose your investment approach:", ["Lump Sum", "SIP"], key="inv_type")
        initial_amount = 0
        monthly_investment = 0
        if investment_type == "Lump Sum":
            initial_amount = st.number_input("Total Lump Sum Investment (₹)", min_value=1000, value=100000, step=5000)
            time_horizon = st.slider("Investment Time Horizon (Years)", min_value=1, max_value=30, value=10)
            monthly_investment = st.number_input("Additional Monthly SIP (Optional) (₹)", min_value=0, value=0, step=500)
        else:
            monthly_investment = st.number_input("Monthly SIP Amount (₹)", min_value=500, value=5000, step=500)
            time_horizon = st.slider("Investment Time Horizon (Years)", min_value=1, max_value=30, value=10)

    with st.sidebar.expander("🎯 Investment Goals", expanded=True):
        goal_type = st.selectbox("Select Your Primary Goal", ["Retirement", "Child Education", "House Purchase", "Wealth Creation", "Emergency Fund"])
        target_amount = st.number_input("Target Amount (₹)", min_value=50000, value=1000000, step=50000)
        inflation_rate = st.slider("Expected Inflation Rate (%)", min_value=3.0, max_value=8.0, value=4.8, step=0.1)
        real_target = target_amount * ((1 + inflation_rate/100) ** time_horizon)
        st.metric("Inflation Adjusted Target", f"₹{real_target:,.0f}")

    with st.sidebar.expander("📊 Asset Allocation", expanded=True):
        mf_allocation = st.slider("Mutual Funds (%)", 0, 100, 40)
        stocks_allocation = st.slider("Stocks (%)", 0, 100, 20)
        fd_allocation = st.slider("Fixed Deposits (%)", 0, 100, 20)
        bonds_allocation = st.slider("Bonds (%)", 0, 100, 15)
        aif_allocation = st.slider("AIF (%)", 0, 100, 5)
        total_allocation = mf_allocation + stocks_allocation + fd_allocation + bonds_allocation + aif_allocation
        if total_allocation != 100:
            st.error(f"Total allocation must be 100%. Current: {total_allocation}%")
            st.stop()
        allocation = {'mutual_funds': mf_allocation/100, 'stocks': stocks_allocation/100, 'fd': fd_allocation/100, 'bonds': bonds_allocation/100, 'aif': aif_allocation/100}

    with st.sidebar.expander("📚 Learn More"):
        for content_key in ["mutual_funds", "stocks", "fd", "bonds", "aif", "risk_free_rate", "beta", "standard_deviation"]:
            show_educational_popup(content_key)

    # --- Main Content ---
    st.header("📊 Investment Analysis Results")
    scenarios = ['normal', 'bullish', 'bearish']
    scenario_names = ['Normal Market', 'Bull Market', 'Bear Market']
    results = {s: calculate_investment_returns(initial_amount, time_horizon, monthly_investment, allocation, s) for s in scenarios}

    # Tabs for scenarios
    tabs = st.tabs(scenario_names)
    for i, tab in enumerate(tabs):
        with tab:
            result = results[scenarios[i]]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Investment", f"₹{result['total_investment']:,.0f}")
            with col2:
                st.metric("Future Value", f"₹{result['future_value']:,.0f}")
            with col3:
                st.metric("Total Gains", f"₹{result['gains']:,.0f}")
            with col4:
                st.metric("Portfolio Return", f"{result['portfolio_return']*100:.1f}%")

            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Portfolio Risk", f"{result['portfolio_risk']*100:.1f}%")
            with col_b:
                st.metric("Portfolio Beta", f"{result['portfolio_beta']:.2f}")

    # Goal achievement check
    st.header("🎯 Goal Achievement Analysis")
    normal_result = results['normal']
    if normal_result['future_value'] >= real_target:
        st.success(f"🎉 Your investment plan can help you achieve your inflation-adjusted target of ₹{real_target:,.0f}!")
    else:
        shortfall = real_target - normal_result['future_value']
        # Handle division by zero for monthly_return if it's 0 or close to 0
        monthly_return = normal_result['portfolio_return'] / 12
        if monthly_return > 1e-9: # Use a small epsilon to avoid division by zero
            required_monthly = shortfall / (((1 + monthly_return) ** (time_horizon * 12) - 1) / monthly_return)
            st.warning(f"💪 Your investment is on track, but you might fall short of your goal. Consider increasing your monthly SIP by ₹{required_monthly:,.0f} to reach your target.")
        else:
            st.warning("Your portfolio return is too low to meet the target. Consider adjusting your asset allocation.")
            
    # Investment breakdown chart
    st.header("📊 Investment Projections")
    years_range = list(range(1, time_horizon + 1))
    projection_data = pd.DataFrame(index=years_range)
    for i, scenario in enumerate(scenarios):
        scenario_values = [calculate_investment_returns(initial_amount, y, monthly_investment, allocation, scenario)['future_value'] for y in years_range]
        projection_data[scenario_names[i]] = scenario_values
    
    fig = px.line(projection_data, x=projection_data.index, y=projection_data.columns,
                  title="Investment Growth Projection",
                  labels={'x': 'Years', 'value': 'Amount (₹)', 'variable': 'Scenario'})
    fig.add_hline(y=real_target, line_dash="dash", line_color="red", annotation_text=f"Target: ₹{real_target:,.0f}")
    st.plotly_chart(fig, use_container_width=True)

    # Allocation & Risk charts
    st.header("📈 Portfolio Composition")
    col1, col2 = st.columns(2)
    with col1:
        allocation_data = pd.DataFrame({'Asset Class': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
                                        'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]})
        fig_pie = px.pie(allocation_data, values='Allocation (%)', names='Asset Class', title='Portfolio Asset Allocation')
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        asset_data = pd.DataFrame({'Asset': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
                                   'Expected Return (%)': [12, 15, 6, 7, 18],
                                   'Risk (%)': [18, 25, 2, 5, 30],
                                   'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]})
        fig_scatter = px.scatter(asset_data, x='Risk (%)', y='Expected Return (%)', size='Allocation (%)', hover_name='Asset', title='Risk vs Return Profile')
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mutual funds section
    st.header("📈 Available Mutual Funds (Real-time AMFI Data)")
    if not mf_data.empty:
        col_search, col_plan = st.columns(2)
        with col_search:
            search_term = st.text_input("Search Fund Name", key="search_fund")
        with col_plan:
            selected_plan = st.selectbox("Plan Type", ['All', 'Direct', 'Regular'], key="plan_type")

        filtered_mf = mf_data.copy()
        if selected_plan != 'All':
            filtered_mf = filtered_mf[filtered_mf['plan_type'] == selected_plan]
        if search_term:
            filtered_mf = filtered_mf[filtered_mf['scheme_name'].str.contains(search_term, case=False, na=False)]
        
        st.dataframe(filtered_mf[['fund_house', 'scheme_name', 'nav', 'plan_type', 'expense_ratio', 'date']].head(50), use_container_width=True)
    else:
        st.info("No mutual fund data available to display.")

if __name__ == "__main__":
    main()
