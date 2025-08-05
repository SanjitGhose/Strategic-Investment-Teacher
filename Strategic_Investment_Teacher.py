import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# --- Page Configuration ---
st.set_page_config(
    page_title="Strategic Investment Teacher",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a Clean, Modern Look (Simplified for readability) ---
st.markdown("""
<style>
    /* Remove default padding at the top of the main content area */
    .st-emotion-cache-18ni7ap { padding-top: 0rem; } 
    .st-emotion-cache-p2w5e4 { padding-top: 0rem; }

    /* Style for the main header banner */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .main-header h1 {
        color: white; /* Ensure header text is white */
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: #e0e0e0; /* Lighter text for subtitle */
        font-size: 1.1rem;
    }

    /* Streamlit Metric styling for better visibility */
    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b; /* Darker text for values */
    }
    .stMetric > div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #64748b; /* Muted text for labels */
    }
    .stMetric {
        background-color: #f8fafc; /* Light background for metrics */
        border: 1px solid #e2e8f0; /* Subtle border */
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem; /* Space between metrics */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }

    /* General header styling */
    h1, h2, h3 {
        color: #1e293b; /* Consistent dark color for all headers */
    }

    /* Streamlit tabs content padding adjustment */
    .st-emotion-cache-1v0s1w-Tab-content {
        padding: 0; /* Remove extra padding inside tabs */
    }

    /* Sidebar expander styling */
    .streamlit-expanderHeader {
        background-color: #e0e7ff; /* Light blue background for expander headers */
        color: #312e81; /* Dark blue text */
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
    }
    .streamlit-expanderContent {
        background-color: #f0f4ff; /* Lighter blue for expander content */
        border-radius: 0.5rem;
        padding: 1rem;
        border: 1px solid #c7d2fe;
    }
</style>
""", unsafe_allow_html=True)


# --- Educational Content Data ---
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

# --- Helper Functions ---
def show_educational_popup(content_key):
    """Displays educational content in an expander within the sidebar."""
    content = EDUCATIONAL_CONTENT[content_key]
    with st.expander(f"💡 Learn about {content['title']}", expanded=False):
        st.markdown(content['content'])

@st.cache_data(ttl=3600)  # Cache data for 1 hour to avoid excessive API calls
def fetch_amfi_data():
    """
    Fetches real-time mutual fund data from AMFI India.
    Includes a fallback to sample data if the API call fails.
    """
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=10) # Added timeout for robustness
        
        if response.status_code == 200:
            lines = response.text.split('\n')
            data = []
            current_fund_house = ""
            for line in lines:
                line = line.strip()
                if not line: continue # Skip empty lines
                
                # Identify fund house lines (start with non-digit)
                if not line[0].isdigit():
                    if "Mutual Fund" in line: 
                        current_fund_house = line
                else:
                    # Parse scheme data lines
                    parts = line.split(';')
                    if len(parts) >= 6: # Ensure enough parts for relevant data
                        try:
                            scheme_name = parts[3]
                            nav = float(parts[4])
                            date = parts[5]
                            # Simple logic to infer plan type and expense ratio
                            plan_type = "Direct" if "Direct" in scheme_name.upper() else "Regular"
                            expense_ratio = 1.2 if plan_type == 'Direct' else 2.0 # Example values
                            data.append({
                                'fund_house': current_fund_house,
                                'scheme_name': scheme_name,
                                'nav': nav,
                                'date': date,
                                'plan_type': plan_type,
                                'expense_ratio': expense_ratio
                            })
                        except (ValueError, IndexError):
                            # Skip lines that cannot be parsed
                            continue
            
            df = pd.DataFrame(data)
            # Filter out any schemes with NaN NAV or other issues
            df = df.dropna(subset=['nav'])
            return df
        else:
            st.warning(f"Failed to fetch live data from AMFI (Status: {response.status_code}). Using sample data.")
            return create_sample_mf_data()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error fetching live data: {e}. Using sample data.")
        return create_sample_mf_data()
    except Exception as e:
        st.error(f"An unexpected error occurred during data fetch: {e}. Using sample data.")
        return create_sample_mf_data()

def create_sample_mf_data():
    """Generates sample mutual fund data for demonstration or fallback."""
    sample_data = []
    fund_types = ['Large Cap', 'Mid Cap', 'Small Cap', 'Multi Cap', 'Debt', 'Hybrid']
    fund_houses = ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Aditya Birla']
    for i in range(100):
        fund_house = np.random.choice(fund_houses)
        fund_type = np.random.choice(fund_types)
        plan_type = np.random.choice(['Direct', 'Regular'])
        sample_data.append({
            'fund_house': f"{fund_house} Mutual Fund",
            'scheme_name': f"{fund_house} {fund_type} Fund - {plan_type} Plan",
            'nav': round(np.random.uniform(10, 500), 2),
            'date': datetime.now().strftime('%d-%b-%Y'),
            'plan_type': plan_type,
            'expense_ratio': 1.2 if plan_type == 'Direct' else 2.0
        })
    return pd.DataFrame(sample_data)

def calculate_investment_returns(amount, years, monthly_investment, allocation, scenario='normal'):
    """
    Calculates projected investment returns based on initial amount, monthly SIP,
    time horizon, asset allocation, and market scenario.
    """
    # Expected returns for different asset classes and market scenarios
    asset_returns = {
        'normal': {'mutual_funds': 0.12, 'stocks': 0.15, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.18},
        'bullish': {'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.28},
        'bearish': {'mutual_funds': 0.04, 'stocks': 0.02, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.08}
    }
    # Risk (Standard Deviation) for different asset classes
    asset_risks = {'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.02, 'bonds': 0.05, 'aif': 0.30}
    # Beta for different asset classes (market sensitivity)
    asset_betas = {'mutual_funds': 0.85, 'stocks': 1.2, 'fd': 0.0, 'bonds': 0.1, 'aif': 1.5}
    
    returns = asset_returns[scenario]
    risk_free_rate = 0.07 # Assumed risk-free rate for Sharpe Ratio

    # Calculate weighted average portfolio return, risk, and beta based on allocation
    portfolio_return = sum(allocation[asset] * returns[asset] for asset in allocation)
    portfolio_risk = sum(allocation[asset] * asset_risks[asset] for asset in allocation)
    portfolio_beta = sum(allocation[asset] * asset_betas[asset] for asset in allocation)
    
    months = years * 12
    monthly_return = portfolio_return / 12
    
    # Future value of lump sum investment
    fv_lumpsum = amount * (1 + portfolio_return) ** years
    
    # Future value of monthly investments (SIP) - using annuity formula
    fv_monthly = 0
    if monthly_investment > 0 and monthly_return > 1e-9: # Avoid division by zero
        fv_monthly = monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
    elif monthly_investment > 0 and monthly_return <= 1e-9: # If return is effectively zero
        fv_monthly = monthly_investment * months
    
    total_future_value = fv_lumpsum + fv_monthly
    total_investment = amount + (monthly_investment * months)
    
    return {
        'total_investment': total_investment,
        'future_value': total_future_value,
        'gains': total_future_value - total_investment,
        'portfolio_return': portfolio_return,
        'portfolio_risk': portfolio_risk,
        'portfolio_beta': portfolio_beta
    }

# --- Main Streamlit Application ---
def main():
    # --- Header Section ---
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Strategic Investment Teacher</h1>
        <p>Plan your financial future with sophisticated calculations and real-time data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- Disclaimer ---
    st.warning("""
    **⚠️ IMPORTANT DISCLAIMER:** This application is for educational purposes only. The returns and calculations shown are based on mathematical models and should not be considered investment advice. Past performance is not a guarantee of future results. Please consult with a SEBI registered investment advisor before making any investment decisions.
    """)
    
    # --- Data Fetch Status ---
    with st.spinner("Attempting to fetch real-time mutual fund data from AMFI..."):
        mf_data = fetch_amfi_data()
    if not mf_data.empty:
        st.success(f"✅ Successfully loaded {len(mf_data)} mutual fund schemes.")
    else:
        st.error("❌ Could not fetch live mutual fund data. Displaying sample data only.")

    # --- Sidebar for Investment Parameters ---
    st.sidebar.header("📊 Investment Parameters")
    
    # Investment Type (Lump Sum / SIP)
    with st.sidebar.expander("💰 Investment Type", expanded=True):
        investment_type = st.radio("Choose your investment approach:", ["Lump Sum", "SIP"], key="inv_type_radio")
        
        initial_amount = 0
        monthly_investment = 0
        
        if investment_type == "Lump Sum":
            initial_amount = st.number_input("Total Lump Sum Investment (₹)", min_value=0, value=100000, step=5000, key="lump_sum_input")
            time_horizon = st.slider("Investment Time Horizon (Years)", min_value=1, max_value=30, value=10, key="lump_sum_years")
            monthly_investment = st.number_input("Additional Monthly SIP (Optional) (₹)", min_value=0, value=0, step=500, key="additional_sip_input")
        else: # SIP
            monthly_investment = st.number_input("Monthly SIP Amount (₹)", min_value=0, value=5000, step=500, key="monthly_sip_input")
            time_horizon = st.slider("Investment Time Horizon (Years)", min_value=1, max_value=30, value=10, key="sip_years")
            initial_amount = st.number_input("Initial Lump Sum (Optional) (₹)", min_value=0, value=0, step=5000, key="initial_lump_sum_sip")

    # Investment Goals
    with st.sidebar.expander("🎯 Investment Goals", expanded=True):
        goal_type = st.selectbox("Select Your Primary Goal", ["Retirement", "Child Education", "House Purchase", "Wealth Creation", "Emergency Fund"], key="goal_type_select")
        target_amount = st.number_input("Target Amount (₹)", min_value=1000, value=1000000, step=50000, key="target_amount_input")
        inflation_rate = st.slider("Expected Inflation Rate (%)", min_value=0.0, max_value=10.0, value=4.8, step=0.1, key="inflation_rate_slider")
        
        # Calculate inflation-adjusted target
        real_target = target_amount * ((1 + inflation_rate/100) ** time_horizon)
        st.metric("Inflation Adjusted Target", f"₹{real_target:,.0f}")

    # Asset Allocation
    with st.sidebar.expander("📊 Asset Allocation", expanded=True):
        st.write("Allocate your portfolio across different asset classes:")
        mf_allocation = st.slider("Mutual Funds (%)", 0, 100, 40, key="mf_alloc_slider")
        stocks_allocation = st.slider("Stocks (%)", 0, 100, 20, key="stocks_alloc_slider")
        fd_allocation = st.slider("Fixed Deposits (%)", 0, 100, 20, key="fd_alloc_slider")
        bonds_allocation = st.slider("Bonds (%)", 0, 100, 15, key="bonds_alloc_slider")
        aif_allocation = st.slider("AIF (%)", 0, 100, 5, key="aif_alloc_slider")
        
        total_allocation = mf_allocation + stocks_allocation + fd_allocation + bonds_allocation + aif_allocation
        
        if total_allocation != 100:
            st.error(f"Total allocation must be 100%. Current: {total_allocation}%")
            # If allocation is not 100%, stop execution to prevent incorrect calculations
            # or allow user to correct before proceeding. For a live app, stopping is better.
            st.stop() 
        
        allocation = {
            'mutual_funds': mf_allocation/100,
            'stocks': stocks_allocation/100,
            'fd': fd_allocation/100,
            'bonds': bonds_allocation/100,
            'aif': aif_allocation/100
        }

    # Learn More Section (Educational Popups)
    st.sidebar.header("📚 Learn More About Terms")
    with st.sidebar.container(): # Group buttons for better layout
        for content_key in ["mutual_funds", "stocks", "fd", "bonds", "aif", "risk_free_rate", "beta", "standard_deviation"]:
            show_educational_popup(content_key)

    # --- Main Content Area: Investment Analysis Results ---
    st.header("📊 Investment Analysis Results")
    scenarios = ['normal', 'bullish', 'bearish']
    scenario_names = ['Normal Market', 'Bull Market', 'Bear Market']
    
    # Calculate results for all scenarios
    results = {s: calculate_investment_returns(initial_amount, time_horizon, monthly_investment, allocation, s) for s in scenarios}

    # Display results using tabs for each scenario
    tabs = st.tabs(scenario_names)
    for i, tab in enumerate(tabs):
        with tab:
            result = results[scenarios[i]]
            st.subheader(f"{scenario_names[i]} Scenario Projections")
            
            # Use columns for a cleaner metric display
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Total Investment", f"₹{result['total_investment']:,.0f}")
            with col2: st.metric("Future Value", f"₹{result['future_value']:,.0f}")
            with col3: st.metric("Total Gains", f"₹{result['gains']:,.0f}")
            with col4: st.metric("Portfolio Return", f"{result['portfolio_return']*100:.1f}%")

            st.markdown("---") # Separator for more metrics
            col_a, col_b = st.columns(2)
            with col_a: st.metric("Portfolio Risk (Std Dev)", f"{result['portfolio_risk']*100:.1f}%")
            with col_b: st.metric("Portfolio Beta", f"{result['portfolio_beta']:.2f}")

    # --- Goal Achievement Analysis ---
    st.header("🎯 Goal Achievement Analysis")
    normal_result = results['normal']
    
    if normal_result['future_value'] >= real_target:
        st.success(f"🎉 Congratulations! Your investment plan is on track to achieve your inflation-adjusted target of ₹{real_target:,.0f}!")
    else:
        shortfall = real_target - normal_result['future_value']
        
        # Calculate required additional monthly investment (SIP)
        # Avoid division by zero if portfolio return is zero or very close to it
        monthly_rate_of_return = normal_result['portfolio_return'] / 12
        
        if monthly_rate_of_return > 1e-9: # Check if rate is significantly positive
            # Formula for required monthly payment to reach a future value
            required_monthly_sip = shortfall * monthly_rate_of_return / ((1 + monthly_rate_of_return)**(time_horizon * 12) - 1)
            st.warning(f"💪 Your current plan might fall short. To reach your inflation-adjusted target of ₹{real_target:,.0f}, consider increasing your monthly investment by **₹{required_monthly_sip:,.0f}**.")
        else:
            st.warning("Your current portfolio return is too low to meet the target. Consider adjusting your asset allocation for higher returns or extending your investment horizon.")

    # --- Investment Projections Chart ---
    st.header("📊 Investment Growth Projection")
    years_range = list(range(1, time_horizon + 1))
    
    # Prepare data for the projection chart
    projection_data = pd.DataFrame(index=years_range)
    for i, scenario in enumerate(scenarios):
        scenario_values = [
            calculate_investment_returns(initial_amount, y, monthly_investment, allocation, scenario)['future_value']
            for y in years_range
        ]
        projection_data[scenario_names[i]] = scenario_values
    
    # Create interactive line chart
    fig = px.line(
        projection_data, 
        x=projection_data.index, 
        y=projection_data.columns,
        title="Investment Growth Projection Over Time",
        labels={'index': 'Years', 'value': 'Amount (₹)', 'variable': 'Market Scenario'},
        line_dash_map={'Normal Market': 'solid', 'Bull Market': 'dash', 'Bear Market': 'dot'},
        color_discrete_map={'Normal Market': '#1f77b4', 'Bull Market': '#2ca02c', 'Bear Market': '#d62728'}
    )
    
    # Add target line
    fig.add_hline(
        y=real_target,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Target: ₹{real_target:,.0f}",
        annotation_position="top left"
    )
    
    fig.update_layout(hovermode='x unified', height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- Portfolio Composition Charts ---
    st.header("📈 Portfolio Composition")
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for Asset Allocation
        allocation_data = pd.DataFrame({
            'Asset Class': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        })
        fig_pie = px.pie(
            allocation_data, 
            values='Allocation (%)', 
            names='Asset Class',
            title='Current Portfolio Asset Allocation',
            hole=0.3 # Creates a donut chart
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Scatter plot for Risk vs Return Profile
        asset_data = pd.DataFrame({
            'Asset': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
            'Expected Return (%)': [12, 15, 6, 7, 18], # Example returns for normal scenario
            'Risk (%)': [18, 25, 2, 5, 30], # Example risks
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        })
        fig_scatter = px.scatter(
            asset_data,
            x='Risk (%)',
            y='Expected Return (%)',
            size='Allocation (%)', # Size of marker based on allocation
            hover_name='Asset',
            title='Asset Class Risk vs Return Profile',
            color='Asset', # Color points by asset type
            size_max=40 # Max size for markers
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # --- Mutual Funds Data Display ---
    st.header("🔎 Explore Mutual Funds (Live AMFI Data)")
    if not mf_data.empty:
        col_search, col_plan = st.columns(2)
        with col_search:
            search_term = st.text_input("Search Fund Name", key="search_fund_input", placeholder="e.g., HDFC Equity Fund")
        with col_plan:
            selected_plan = st.selectbox("Filter by Plan Type", ['All', 'Direct', 'Regular'], key="plan_type_select")

        filtered_mf = mf_data.copy()
        if selected_plan != 'All':
            filtered_mf = filtered_mf[filtered_mf['plan_type'] == selected_plan]
        if search_term:
            filtered_mf = filtered_mf[filtered_mf['scheme_name'].str.contains(search_term, case=False, na=False)]
        
        st.dataframe(
            filtered_mf[['fund_house', 'scheme_name', 'nav', 'plan_type', 'expense_ratio', 'date']].head(50), 
            use_container_width=True,
            height=300 # Set a fixed height for the dataframe
        )
        if filtered_mf.empty:
            st.info("No mutual funds match your search criteria.")
    else:
        st.info("Mutual fund data is not available to display at this time.")

    st.markdown("---")
    st.info("💡 **Tip:** Adjust the parameters in the sidebar to see how different investment strategies impact your financial future!")

if __name__ == "__main__":
    main()
