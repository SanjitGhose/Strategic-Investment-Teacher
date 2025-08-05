import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Strategic Investment Teacher",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #ffffff;
        border: 2px solid #dee2e6;
        padding: 1.2rem;
        border-radius: 0.8rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        color: #212529;
    }
    .stMetric .metric-value {
        color: #1f2937 !important;
        font-weight: bold !important;
    }
    .stMetric .metric-label {
        color: #4b5563 !important;
        font-weight: 500 !important;
    }
    .investment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
    }
    .goal-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        color: white;
        margin: 0.5rem 0;
    }
    .disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    .motivational-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Educational pop-ups data
EDUCATIONAL_CONTENT = {
    "mutual_funds": {
        "title": "📊 Mutual Funds",
        "content": """
        **What are Mutual Funds?**
        - Pool of money from many investors
        - Professionally managed by fund managers
        - Diversified portfolio of stocks, bonds, or other securities
        - Suitable for long-term wealth creation
        
        **Types:**
        - Equity Funds (High risk, high return)
        - Debt Funds (Low risk, moderate return)
        - Hybrid Funds (Balanced approach)
        """
    },
    "stocks": {
        "title": "📈 Stocks",
        "content": """
        **What are Stocks?**
        - Ownership shares in a company
        - Potential for high returns but volatile
        - Requires research and market knowledge
        - Best for long-term investment
        
        **Key Points:**
        - Dividend income + Capital appreciation
        - Market risk is high
        - Liquidity is good
        """
    },
    "fd": {
        "title": "🏛️ Fixed Deposits",
        "content": """
        **What are Fixed Deposits?**
        - Safe investment with guaranteed returns
        - Fixed interest rate for specific tenure
        - No market risk involved
        - Lower returns compared to equity
        
        **Features:**
        - Capital protection
        - Predictable returns
        - Various tenure options
        """
    },
    "bonds": {
        "title": "📜 Bonds",
        "content": """
        **What are Bonds?**
        - Debt instruments issued by companies/government
        - Regular interest payments (coupon)
        - Lower risk than stocks
        - Good for steady income
        
        **Types:**
        - Government Bonds (Safest)
        - Corporate Bonds (Higher yield)
        - Tax-saving bonds
        """
    },
    "aif": {
        "title": "🎯 Alternative Investment Funds",
        "content": """
        **What are AIFs?**
        - Privately pooled investment funds
        - Higher minimum investment
        - Less regulated than mutual funds
        - Potential for higher returns
        
        **Categories:**
        - Category I: Social ventures, SME funds
        - Category II: PE, Debt funds
        - Category III: Hedge funds
        """
    },
    "risk_free_rate": {
        "title": "🛡️ Risk-Free Rate",
        "content": """
        **What is Risk-Free Rate?**
        - Rate of return on investment with zero risk
        - Usually 10-year Government Bond yield
        - Used as benchmark for other investments
        - Currently around 7% in India
        
        **Why Important?**
        - Base for calculating expected returns
        - Helps in risk assessment
        - Used in CAPM model
        """
    },
    "beta": {
        "title": "📊 Beta",
        "content": """
        **What is Beta?**
        - Measures stock's volatility relative to market
        - Beta = 1: Moves with market
        - Beta > 1: More volatile than market
        - Beta < 1: Less volatile than market
        
        **Usage in Calculations:**
        - Helps determine expected returns
        - Risk assessment tool
        - Portfolio construction
        """
    },
    "standard_deviation": {
        "title": "📈 Standard Deviation",
        "content": """
        **What is Standard Deviation?**
        - Measures investment volatility
        - Higher SD = Higher risk
        - Shows how much returns deviate from average
        - Key risk metric for investments
        
        **In Investment Decisions:**
        - Risk assessment
        - Portfolio optimization
        - Return expectation setting
        """
    }
}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_amfi_data():
    """Fetch real-time mutual fund data from AMFI"""
    try:
        # AMFI NAV data URL
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.split('\n')
            data = []
            current_fund_house = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line and not line[0].isdigit():
                    if "Mutual Fund" in line:
                        current_fund_house = line
                else:
                    parts = line.split(';')
                    if len(parts) >= 6:
                        try:
                            scheme_code = parts[0]
                            scheme_name = parts[3]
                            nav = float(parts[4])
                            date = parts[5]
                            
                            # Determine plan type and charges
                            plan_type = "Regular"
                            expense_ratio = 2.0  # Default
                            
                            if "Direct" in scheme_name.upper():
                                plan_type = "Direct"
                                expense_ratio = 1.2
                            
                            if "GROWTH" in scheme_name.upper():
                                option = "Growth"
                            elif "DIVIDEND" in scheme_name.upper():
                                option = "Dividend"
                            else:
                                option = "Growth"
                            
                            data.append({
                                'fund_house': current_fund_house,
                                'scheme_code': scheme_code,
                                'scheme_name': scheme_name,
                                'nav': nav,
                                'date': date,
                                'plan_type': plan_type,
                                'option': option,
                                'expense_ratio': expense_ratio
                            })
                        except (ValueError, IndexError):
                            continue
            
            df = pd.DataFrame(data)
            return df.head(100)  # Return first 100 funds for demo
        else:
            # Fallback sample data
            return create_sample_mf_data()
    except Exception as e:
        st.warning(f"Unable to fetch live data: {e}. Using sample data.")
        return create_sample_mf_data()

def create_sample_mf_data():
    """Create sample mutual fund data"""
    sample_data = []
    fund_types = ['Large Cap', 'Mid Cap', 'Small Cap', 'Multi Cap', 'Debt', 'Hybrid']
    fund_houses = ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Aditya Birla']
    
    for i in range(60):
        fund_house = np.random.choice(fund_houses)
        fund_type = np.random.choice(fund_types)
        plan_type = np.random.choice(['Direct', 'Regular'])
        
        sample_data.append({
            'fund_house': f"{fund_house} Mutual Fund",
            'scheme_code': f"MF{1000+i:04d}",
            'scheme_name': f"{fund_house} {fund_type} Fund - {plan_type} Plan",
            'nav': round(np.random.uniform(10, 500), 2),
            'date': datetime.now().strftime('%d-%b-%Y'),
            'plan_type': plan_type,
            'option': 'Growth',
            'expense_ratio': 1.2 if plan_type == 'Direct' else 2.0
        })
    
    return pd.DataFrame(sample_data)

def calculate_investment_returns(amount, years, monthly_investment, allocation, scenario='normal'):
    """Calculate investment returns for different scenarios"""
    
    # Asset class expected returns and risks
    asset_returns = {
        'normal': {
            'mutual_funds': 0.12, 'stocks': 0.15, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.18
        },
        'bullish': {
            'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.28
        },
        'bearish': {
            'mutual_funds': 0.04, 'stocks': 0.02, 'fd': 0.06, 'bonds': 0.07, 'aif': 0.08
        }
    }
    
    asset_risks = {
        'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.02, 'bonds': 0.05, 'aif': 0.30
    }
    
    asset_betas = {
        'mutual_funds': 0.85, 'stocks': 1.2, 'fd': 0.0, 'bonds': 0.1, 'aif': 1.5
    }
    
    returns = asset_returns[scenario]
    risk_free_rate = 0.07
    
    # Calculate portfolio weighted return
    portfolio_return = sum(allocation[asset] * returns[asset] for asset in allocation)
    portfolio_risk = sum(allocation[asset] * asset_risks[asset] for asset in allocation)
    portfolio_beta = sum(allocation[asset] * asset_betas[asset] for asset in allocation)
    
    # Calculate future value with monthly investments
    months = years * 12
    monthly_return = portfolio_return / 12
    
    # Future value of lump sum
    fv_lumpsum = amount * (1 + portfolio_return) ** years
    
    # Future value of monthly investments (annuity)
    if monthly_investment > 0:
        fv_monthly = monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
    else:
        fv_monthly = 0
    
    total_future_value = fv_lumpsum + fv_monthly
    total_investment = amount + (monthly_investment * months)
    
    return {
        'total_investment': total_investment,
        'future_value': total_future_value,
        'gains': total_future_value - total_investment,
        'portfolio_return': portfolio_return,
        'portfolio_risk': portfolio_risk,
        'portfolio_beta': portfolio_beta,
        'years_to_goal': years
    }

def show_educational_popup(content_key):
    """Show educational content in expander"""
    content = EDUCATIONAL_CONTENT[content_key]
    with st.expander(f"💡 Learn about {content['title']}", expanded=False):
        st.markdown(content['content'])

def main():
    # Header
    st.markdown("""
    <div class="investment-card">
        <h1>🎓 Strategic Investment Teacher</h1>
        <p>Learn to plan your financial future with real-time data and sophisticated calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ IMPORTANT DISCLAIMER:</strong> This application is for educational purposes only. 
        The returns and calculations shown are based on historical data and mathematical models, and should not be considered as investment advice. 
        Past performance does not guarantee future results. Please consult with a SEBI registered investment advisor before making any investment decisions. 
        The developers are not responsible for any financial losses incurred based on the information provided in this application.
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch mutual fund data
    with st.spinner("Fetching real-time mutual fund data from AMFI..."):
        mf_data = fetch_amfi_data()
    
    st.success(f"✅ Loaded {len(mf_data)} mutual fund schemes with real-time NAV data")
    
    # Sidebar for inputs
    st.sidebar.header("📊 Investment Parameters")
    
    # Investment type selection
    st.sidebar.subheader("💰 Investment Type")
    investment_type = st.sidebar.radio(
        "Choose your investment approach:",
        ["Lump Sum", "SIP (Systematic Investment Plan)"],
        help="Select whether you want to invest a one-time amount or monthly installments"
    )
    
    if investment_type == "Lump Sum":
        initial_amount = st.sidebar.number_input(
            "💰 Total Lump Sum Investment (₹)",
            min_value=1000,
            value=100000,
            step=5000,
            help="Enter your one-time investment amount"
        )
        monthly_investment = 0
        total_investment_period = initial_amount
        st.sidebar.info(f"Total Investment: ₹{total_investment_period:,}")
        
    else:  # SIP
        monthly_investment = st.sidebar.number_input(
            "📅 Monthly SIP Amount (₹)",
            min_value=500,
            value=5000,
            step=500,
            help="Enter your monthly SIP amount"
        )
        initial_amount = 0
        
        # Time horizon for calculating total investment
        time_horizon_temp = st.sidebar.slider(
            "⏱️ Investment Time Horizon (Years)",
            min_value=1,
            max_value=30,
            value=10,
            help="How long do you plan to invest?"
        )
        
        total_investment_period = monthly_investment * time_horizon_temp * 12
        st.sidebar.info(f"Total Investment over {time_horizon_temp} years: ₹{total_investment_period:,}")
    
    # Time horizon (moved after investment type for SIP)
    if investment_type == "Lump Sum":
        time_horizon = st.sidebar.slider(
            "⏱️ Investment Time Horizon (Years)",
            min_value=1,
            max_value=30,
            value=10,
            help="How long do you plan to invest?"
        )
    else:
        time_horizon = time_horizon_temp
    
    # Investment goals
    st.sidebar.subheader("🎯 Investment Goals")
    goal_type = st.sidebar.selectbox(
        "Select Your Primary Goal",
        ["Retirement", "Child Education", "House Purchase", "Wealth Creation", "Emergency Fund"]
    )
    
    target_amount = st.sidebar.number_input(
        "🎯 Target Amount (₹)",
        min_value=50000,
        value=1000000,
        step=50000,
        help="How much do you want to accumulate?"
    )
    
    # Inflation adjustment
    inflation_rate = st.sidebar.slider(
        "📈 Expected Inflation Rate (%)",
        min_value=3.0,
        max_value=8.0,
        value=4.8,
        step=0.1,
        help="Adjust target amount for inflation"
    )
    
    # Adjust target amount for inflation
    real_target = target_amount * ((1 + inflation_rate/100) ** time_horizon)
    
    st.sidebar.metric("Inflation Adjusted Target", f"₹{real_target:,.0f}")
    
    # Asset allocation
    st.sidebar.subheader("📊 Asset Allocation")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        mf_allocation = st.slider("Mutual Funds (%)", 0, 100, 40)
        show_educational_popup("mutual_funds")
        
        stocks_allocation = st.slider("Stocks (%)", 0, 100, 20)
        show_educational_popup("stocks")
        
        fd_allocation = st.slider("Fixed Deposits (%)", 0, 100, 20)
        show_educational_popup("fd")
    
    with col2:
        bonds_allocation = st.slider("Bonds (%)", 0, 100, 15)
        show_educational_popup("bonds")
        
        aif_allocation = st.slider("AIF (%)", 0, 100, 5)
        show_educational_popup("aif")
    
    total_allocation = mf_allocation + stocks_allocation + fd_allocation + bonds_allocation + aif_allocation
    
    if total_allocation != 100:
        st.sidebar.error(f"Total allocation should be 100%. Current: {total_allocation}%")
        st.stop()
    
    allocation = {
        'mutual_funds': mf_allocation/100,
        'stocks': stocks_allocation/100,
        'fd': fd_allocation/100,
        'bonds': bonds_allocation/100,
        'aif': aif_allocation/100
    }
    
    # Monthly investment calculator
    if investment_type == "Lump Sum":
        st.sidebar.subheader("📅 Additional Monthly Investment (Optional)")
        additional_monthly = st.sidebar.number_input(
            "Additional Monthly SIP (₹)",
            min_value=0,
            value=0,
            step=500,
            help="Optional additional monthly investment amount"
        )
        # Update monthly_investment for calculations
        monthly_investment = additional_monthly
    
    # Educational content buttons
    st.sidebar.subheader("📚 Learn More")
    if st.sidebar.button("🛡️ Risk-Free Rate"):
        show_educational_popup("risk_free_rate")
    if st.sidebar.button("📊 Beta Coefficient"):
        show_educational_popup("beta")
    if st.sidebar.button("📈 Standard Deviation"):
        show_educational_popup("standard_deviation")
    
    # Main calculations
    col1, col2, col3 = st.columns(3)
    
    scenarios = ['normal', 'bullish', 'bearish']
    scenario_names = ['Normal Market', 'Bull Market', 'Bear Market']
    results = {}
    
    for scenario in scenarios:
        results[scenario] = calculate_investment_returns(
            initial_amount, time_horizon, monthly_investment, allocation, scenario
        )
    
    # Display results
    st.header("📊 Investment Analysis Results")
    
    # Metrics display
    for i, scenario in enumerate(scenarios):
        result = results[scenario]
        
        with [col1, col2, col3][i]:
            st.subheader(f"📈 {scenario_names[i]}")
            
            # Create readable metrics with better contrast
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Total Investment</h4>
                    <h3 style="color: #1f2937; margin: 0; font-size: 1.2rem;">₹{result['total_investment']:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Future Value</h4>
                    <h3 style="color: #059669; margin: 0; font-size: 1.2rem;">₹{result['future_value']:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Total Gains</h4>
                    <h3 style="color: #dc2626; margin: 0; font-size: 1.2rem;">₹{result['gains']:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Portfolio Return</h4>
                    <h3 style="color: #7c3aed; margin: 0; font-size: 1.2rem;">{result['portfolio_return']*100:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Portfolio Risk</h4>
                    <h3 style="color: #ea580c; margin: 0; font-size: 1.2rem;">{result['portfolio_risk']*100:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; border: 2px solid #e5e7eb; margin: 0.2rem 0;">
                    <h4 style="color: #374151; margin: 0; font-size: 0.9rem;">Portfolio Beta</h4>
                    <h3 style="color: #0891b2; margin: 0; font-size: 1.2rem;">{result['portfolio_beta']:.2f}</h3>
                </div>
                """, unsafe_allow_html=True)
    
    # Goal achievement check
    st.header("🎯 Goal Achievement Analysis")
    
    normal_result = results['normal']
    if normal_result['future_value'] >= real_target:
        st.markdown("""
        <div class="success-message">
            🎉 Congratulations! Your investment plan can help you achieve your goal!
            You're on track to reach your inflation-adjusted target of ₹{:,.0f}
        </div>
        """.format(real_target), unsafe_allow_html=True)
    else:
        shortfall = real_target - normal_result['future_value']
        additional_monthly = shortfall / (time_horizon * 12)
        
        st.markdown("""
        <div class="motivational-message">
            💪 Don't worry! You're making great progress. To reach your goal, consider:
            <br>• Increasing monthly SIP by ₹{:,.0f}
            <br>• Extending investment horizon
            <br>• Reviewing asset allocation for higher returns
            <br><br>Remember: Every investment step counts towards your financial freedom!
        </div>
        """.format(additional_monthly), unsafe_allow_html=True)
    
    # Time to goal calculation
    st.subheader("⏰ Time to Reach Goal")
    years_needed = np.log(real_target / initial_amount) / np.log(1 + normal_result['portfolio_return'])
    st.info(f"With current allocation, you'll need approximately {years_needed:.1f} years to reach your goal")
    
    # Investment breakdown chart
    st.header("📊 Investment Projections")
    
    # Create projection data
    years_range = list(range(1, time_horizon + 1))
    projection_data = {
        'Year': years_range,
        'Normal Market': [],
        'Bull Market': [],
        'Bear Market': []
    }
    
    for year in years_range:
        for i, scenario in enumerate(scenarios):
            temp_result = calculate_investment_returns(
                initial_amount, year, monthly_investment, allocation, scenario
            )
            projection_data[scenario_names[i]].append(temp_result['future_value'])
    
    # Create interactive chart
    fig = go.Figure()
    
    colors = ['#1f77b4', '#2ca02c', '#d62728']
    for i, scenario in enumerate(scenario_names):
        fig.add_trace(go.Scatter(
            x=projection_data['Year'],
            y=projection_data[scenario],
            mode='lines+markers',
            name=scenario,
            line=dict(color=colors[i], width=3),
            marker=dict(size=8)
        ))
    
    # Add target line
    fig.add_hline(
        y=real_target,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Target: ₹{real_target:,.0f}"
    )
    
    fig.update_layout(
        title="Investment Growth Projection",
        xaxis_title="Years",
        yaxis_title="Amount (₹)",
        hovermode='x unified',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Asset allocation pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        allocation_data = pd.DataFrame({
            'Asset Class': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        })
        
        fig_pie = px.pie(
            allocation_data, 
            values='Allocation (%)', 
            names='Asset Class',
            title='Portfolio Asset Allocation'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Risk-Return scatter plot
        asset_data = pd.DataFrame({
            'Asset': ['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'],
            'Expected Return (%)': [12, 15, 6, 7, 18],
            'Risk (%)': [18, 25, 2, 5, 30],
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        })
        
        fig_scatter = px.scatter(
            asset_data,
            x='Risk (%)',
            y='Expected Return (%)',
            size='Allocation (%)',
            hover_name='Asset',
            title='Risk vs Return Profile'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mutual funds selection
    st.header("📈 Available Mutual Funds (Real-time AMFI Data)")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_plan = st.selectbox("Plan Type", ['All', 'Direct', 'Regular'])
    with col2:
        search_term = st.text_input("Search Fund Name")
    with col3:
        min_nav = st.number_input("Minimum NAV", min_value=0.0, value=0.0)
    
    # Filter data
    filtered_mf = mf_data.copy()
    if selected_plan != 'All':
        filtered_mf = filtered_mf[filtered_mf['plan_type'] == selected_plan]
    if search_term:
        filtered_mf = filtered_mf[filtered_mf['scheme_name'].str.contains(search_term, case=False, na=False)]
    if min_nav > 0:
        filtered_mf = filtered_mf[filtered_mf['nav'] >= min_nav]
    
    # Display filtered data
    st.dataframe(
        filtered_mf[['scheme_name', 'nav', 'plan_type', 'expense_ratio', 'date']].head(20),
        use_container_width=True
    )
    
    # Monthly investment recommendation
    st.header("💡 Investment Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Optimal Monthly Investment")
        if normal_result['future_value'] < real_target:
            required_monthly = (real_target - initial_amount * (1 + normal_result['portfolio_return']) ** time_horizon) / (((1 + normal_result['portfolio_return']/12) ** (time_horizon * 12) - 1) / (normal_result['portfolio_return']/12))
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 0.8rem; border: 2px solid #3b82f6;">
                <h4 style="color: #1e40af; margin: 0 0 0.5rem 0;">Recommended Monthly SIP</h4>
                <h2 style="color: #1f2937; margin: 0;">₹{required_monthly:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #dcfce7; padding: 1.5rem; border-radius: 0.8rem; border: 2px solid #22c55e;">
                <h4 style="color: #15803d; margin: 0;">✅ Current plan is sufficient to meet your goal!</h4>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("⚖️ Risk Assessment")
        risk_level = "Low" if normal_result['portfolio_risk'] < 0.1 else "Medium" if normal_result['portfolio_risk'] < 0.2 else "High"
        risk_color = "#22c55e" if risk_level == "Low" else "#f59e0b" if risk_level == "Medium" else "#ef4444"
        
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 0.8rem; border: 2px solid {risk_color};">
            <h4 style="color: #374151; margin: 0 0 0.5rem 0;">Portfolio Risk Level</h4>
            <h2 style="color: {risk_color}; margin: 0 0 1rem 0;">{risk_level}</h2>
            <h4 style="color: #374151; margin: 0 0 0.5rem 0;">Sharpe Ratio</h4>
            <h3 style="color: #1f2937; margin: 0;">{(normal_result['portfolio_return'] - 0.07) / normal_result['portfolio_risk']:.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Try different combinations section
    st.header("🔄 Try Different Combinations")
    st.info("💡 Tip: Adjust the sliders in the sidebar to see how different asset allocations affect your returns in real-time!")
    
    # Export results
    if st.button("📊 Generate Detailed Report"):
        report_data = {
            'Investment Summary': {
                'Initial Amount': f"₹{initial_amount:,}",
                'Monthly SIP': f"₹{monthly_investment:,}",
                'Time Horizon': f"{time_horizon} years",
                'Target Amount': f"₹{target_amount:,}",
                'Inflation Adjusted Target': f"₹{real_target:,.0f}"
            },
            'Normal Market Scenario': {
                'Future Value': f"₹{normal_result['future_value']:,.0f}",
                'Total Gains': f"₹{normal_result['gains']:,.0f}",
                'Portfolio Return': f"{normal_result['portfolio_return']*100:.1f}%",
                'Portfolio Risk': f"{normal_result['portfolio_risk']*100:.1f}%"
            }
        }
        
        st.json(report_data)

if __name__ == "__main__":
    main()