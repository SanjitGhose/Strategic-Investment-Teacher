import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Strategic Investment Teacher",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and professional styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
        background-color: #0e1117;
    }
    
    .investment-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
        border: 2px solid #475569;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        border: 2px solid #6b7280;
        margin: 0.3rem 0;
        color: white;
    }
    
    .metric-title {
        color: #d1d5db;
        font-size: 0.9rem;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    }
    
    .metric-value {
        color: #ffffff;
        font-size: 1.3rem;
        margin: 0;
        font-weight: bold;
    }
    
    .disclaimer {
        background: linear-gradient(135deg, #451a03 0%, #78350f 100%);
        border: 2px solid #d97706;
        padding: 1.2rem;
        border-radius: 0.8rem;
        margin: 1rem 0;
        color: white;
        font-size: 0.95rem;
    }
    
    .success-message {
        background: linear-gradient(135deg, #064e3b 0%, #047857 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        border: 2px solid #10b981;
        margin: 1rem 0;
    }
    
    .motivational-message {
        background: linear-gradient(135deg, #92400e 0%, #b45309 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        border: 2px solid #f59e0b;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
        padding: 1.2rem;
        border-radius: 0.8rem;
        color: white;
        border: 2px solid #6366f1;
        margin: 0.5rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #374151;
        color: white;
    }
    
    .stNumberInput > div > div > input {
        background-color: #374151;
        color: white;
    }
    
    .stSlider > div > div > div {
        background-color: #374151;
    }
    
    .scenario-header {
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border: 2px solid #6366f1;
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
    }
}

def calculate_investment_returns(amount, years, monthly_investment, allocation, scenario='normal'):
    """Calculate investment returns for different scenarios"""
    
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
    
    # Calculate portfolio weighted return
    portfolio_return = sum(allocation[asset] * returns[asset] for asset in allocation)
    portfolio_risk = sum(allocation[asset] * asset_risks[asset] for asset in allocation)
    portfolio_beta = sum(allocation[asset] * asset_betas[asset] for asset in allocation)
    
    # Calculate future value
    months = years * 12
    monthly_return = portfolio_return / 12
    
    # Future value of lump sum
    fv_lumpsum = amount * (1 + portfolio_return) ** years
    
    # Future value of monthly investments
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
        'portfolio_beta': portfolio_beta
    }

def show_educational_popup(content_key):
    """Show educational content in expander"""
    if content_key in EDUCATIONAL_CONTENT:
        content = EDUCATIONAL_CONTENT[content_key]
        with st.expander(f"💡 Learn about {content['title']}", expanded=False):
            st.markdown(content['content'])

def create_metric_card(title, value, color="#ffffff"):
    """Create a dark themed metric card"""
    return f"""
    <div class="metric-card">
        <h4 class="metric-title">{title}</h4>
        <h3 class="metric-value" style="color: {color};">{value}</h3>
    </div>
    """

def main():
    # Header
    st.markdown("""
    <div class="investment-card">
        <h1>🎓 Strategic Investment Teacher</h1>
        <p>Learn to plan your financial future with sophisticated calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>⚠️ IMPORTANT DISCLAIMER:</strong> This application is for educational purposes only. 
        The returns and calculations shown are based on hypothetical data and mathematical models, and should not be considered as investment advice. 
        Past performance does not guarantee future results. Please consult with a SEBI registered investment advisor before making any investment decisions. 
        The developers are not responsible for any financial losses incurred based on the information provided in this application.
    </div>
    """, unsafe_allow_html=True)
    
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
        
        time_horizon_temp = st.sidebar.slider(
            "⏱️ Investment Time Horizon (Years)",
            min_value=1,
            max_value=30,
            value=10,
            help="How long do you plan to invest?"
        )
        
        total_investment_period = monthly_investment * time_horizon_temp * 12
        st.sidebar.info(f"Total Investment over {time_horizon_temp} years: ₹{total_investment_period:,}")
    
    # Time horizon
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
    
    st.sidebar.markdown(f"""
    <div class="info-box">
        <strong>Inflation Adjusted Target:</strong><br>
        ₹{real_target:,.0f}
    </div>
    """, unsafe_allow_html=True)
    
    # Asset allocation
    st.sidebar.subheader("📊 Asset Allocation")
    
    mf_allocation = st.sidebar.slider("Mutual Funds (%)", 0, 100, 40)
    show_educational_popup("mutual_funds")
    
    stocks_allocation = st.sidebar.slider("Stocks (%)", 0, 100, 20)
    show_educational_popup("stocks")
    
    fd_allocation = st.sidebar.slider("Fixed Deposits (%)", 0, 100, 20)
    show_educational_popup("fd")
    
    bonds_allocation = st.sidebar.slider("Bonds (%)", 0, 100, 15)
    show_educational_popup("bonds")
    
    aif_allocation = st.sidebar.slider("AIF (%)", 0, 100, 5)
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
    
    # Additional monthly investment for lump sum
    if investment_type == "Lump Sum":
        st.sidebar.subheader("📅 Additional Monthly Investment (Optional)")
        additional_monthly = st.sidebar.number_input(
            "Additional Monthly SIP (₹)",
            min_value=0,
            value=0,
            step=500,
            help="Optional additional monthly investment amount"
        )
        monthly_investment = additional_monthly
    
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
    
    # Metrics display with dark theme
    for i, scenario in enumerate(scenarios):
        result = results[scenario]
        
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="scenario-header">
                <h3>📈 {scenario_names[i]}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Total Investment", f"₹{result['total_investment']:,.0f}", "#94a3b8"), unsafe_allow_html=True)
            st.markdown(create_metric_card("Future Value", f"₹{result['future_value']:,.0f}", "#22c55e"), unsafe_allow_html=True)
            st.markdown(create_metric_card("Total Gains", f"₹{result['gains']:,.0f}", "#f59e0b"), unsafe_allow_html=True)
            st.markdown(create_metric_card("Portfolio Return", f"{result['portfolio_return']*100:.1f}%", "#8b5cf6"), unsafe_allow_html=True)
            st.markdown(create_metric_card("Portfolio Risk", f"{result['portfolio_risk']*100:.1f}%", "#ef4444"), unsafe_allow_html=True)
            st.markdown(create_metric_card("Portfolio Beta", f"{result['portfolio_beta']:.2f}", "#06b6d4"), unsafe_allow_html=True)
    
    # Goal achievement check
    st.header("🎯 Goal Achievement Analysis")
    
    normal_result = results['normal']
    if normal_result['future_value'] >= real_target:
        st.markdown(f"""
        <div class="success-message">
            🎉 Congratulations! Your investment plan can help you achieve your goal!<br>
            You're on track to reach your inflation-adjusted target of ₹{real_target:,.0f}
        </div>
        """, unsafe_allow_html=True)
    else:
        shortfall = real_target - normal_result['future_value']
        additional_monthly_needed = shortfall / (time_horizon * 12)
        
        st.markdown(f"""
        <div class="motivational-message">
            💪 Don't worry! You're making great progress. To reach your goal, consider:<br>
            • Increasing monthly SIP by ₹{additional_monthly_needed:,.0f}<br>
            • Extending investment horizon<br>
            • Reviewing asset allocation for higher returns<br><br>
            Remember: Every investment step counts towards your financial freedom!
        </div>
        """, unsafe_allow_html=True)
    
    # Time to goal calculation
    st.subheader("⏰ Time to Reach Goal")
    if initial_amount > 0 and normal_result['portfolio_return'] > 0:
        years_needed = np.log(real_target / initial_amount) / np.log(1 + normal_result['portfolio_return'])
        st.markdown(f"""
        <div class="info-box">
            With current allocation, you'll need approximately <strong>{years_needed:.1f} years</strong> to reach your goal
        </div>
        """, unsafe_allow_html=True)
    
    # Charts section
    st.header("📊 Investment Projections")
    
    # Create projection data for native Streamlit charts
    years_range = list(range(1, min(time_horizon + 1, 21)))  # Limit to 20 years for performance
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

    df_projection = pd.DataFrame(projection_data)
    df_projection.set_index('Year', inplace=True)

    st.subheader("Investment Growth Projection")
    st.line_chart(df_projection)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Asset Allocation")
        allocation_data = pd.DataFrame({
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        }, index=['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'])
        st.bar_chart(allocation_data)
    
    with col2:
        st.subheader("Risk vs Return Profile")
        asset_data = pd.DataFrame({
            'Expected Return (%)': [12, 15, 6, 7, 18],
            'Risk (%)': [18, 25, 2, 5, 30]
        }, index=['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'])
        st.scatter_chart(asset_data, x='Risk (%)', y='Expected Return (%)')
    
    # Investment recommendations
    st.header("💡 Investment Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Optimal Monthly Investment")
        if normal_result['future_value'] < real_target:
            required_monthly = (real_target - initial_amount * (1 + normal_result['portfolio_return']) ** time_horizon) / (((1 + normal_result['portfolio_return']/12) ** (time_horizon * 12) - 1) / (normal_result['portfolio_return']/12))
            st.markdown(f"""
            <div class="info-box">
                <strong>Recommended Monthly SIP:</strong><br>
                ₹{required_monthly:,.0f}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-message">
                ✅ Current plan is sufficient to meet your goal!
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("⚖️ Risk Assessment")
        risk_level = "Low" if normal_result['portfolio_risk'] < 0.1 else "Medium" if normal_result['portfolio_risk'] < 0.2 else "High"
        risk_color = "#22c55e" if risk_level == "Low" else "#f59e0b" if risk_level == "Medium" else "#ef4444"
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Portfolio Risk Level:</strong> <span style="color: {risk_color};">{risk_level}</span><br>
            <strong>Sharpe Ratio:</strong> {(normal_result['portfolio_return'] - 0.07) / normal_result['portfolio_risk']:.2f}
        </div>
        """, unsafe_allow_html=True)
    
    # Educational section
    st.header("📚 Learn More About Investment Concepts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛡️ Risk-Free Rate"):
            st.markdown("""
            <div class="info-box">
                <strong>Risk-Free Rate (7%):</strong><br>
                • Government bond yield (10-year)<br>
                • Benchmark for other investments<br>
                • Used in CAPM calculations<br>
                • Currently around 7% in India
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📊 Beta Coefficient"):
            st.markdown("""
            <div class="info-box">
                <strong>Beta Coefficient:</strong><br>
                • Measures volatility vs market<br>
                • Beta = 1: Moves with market<br>
                • Beta > 1: More volatile<br>
                • Used for risk assessment
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📈 Standard Deviation"):
            st.markdown("""
            <div class="info-box">
                <strong>Standard Deviation:</strong><br>
                • Measures investment volatility<br>
                • Higher SD = Higher risk<br>
                • Shows return deviation<br>
                • Key risk metric
            </div>
            """, unsafe_allow_html=True)
    
    # Try different combinations section
    st.header("🔄 Try Different Combinations")
    st.markdown("""
    <div class="info-box">
        💡 <strong>Tip:</strong> Adjust the sliders in the sidebar to see how different asset allocations 
        affect your returns in real-time! Experiment with different scenarios to find your optimal investment strategy.
    </div>
    """, unsafe_allow_html=True)
    
    # Export results
    st.header("📊 Investment Summary Report")
    if st.button("📋 Generate Detailed Report", type="primary"):
        report_data = {
            'Investment Strategy': investment_type,
            'Initial Amount': f"₹{initial_amount:,}" if initial_amount > 0 else "₹0",
            'Monthly SIP': f"₹{monthly_investment:,}" if monthly_investment > 0 else "₹0",
            'Time Horizon': f"{time_horizon} years",
            'Target Amount': f"₹{target_amount:,}",
            'Inflation Adjusted Target': f"₹{real_target:,.0f}",
            'Asset Allocation': {
                'Mutual Funds': f"{mf_allocation}%",
                'Stocks': f"{stocks_allocation}%", 
                'Fixed Deposits': f"{fd_allocation}%",
                'Bonds': f"{bonds_allocation}%",
                'AIF': f"{aif_allocation}%"
            },
            'Projected Results (Normal Market)': {
                'Future Value': f"₹{normal_result['future_value']:,.0f}",
                'Total Investment': f"₹{normal_result['total_investment']:,.0f}",
                'Total Gains': f"₹{normal_result['gains']:,.0f}",
                'Portfolio Return': f"{normal_result['portfolio_return']*100:.1f}%",
                'Portfolio Risk': f"{normal_result['portfolio_risk']*100:.1f}%",
                'Portfolio Beta': f"{normal_result['portfolio_beta']:.2f}"
            }
        }
        
        st.json(report_data)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        <p>🎓 Strategic Investment Teacher - Educational Investment Planning Tool</p>
        <p>Made with ❤️ for financial literacy and investment education</p>
        <p><em>Remember: This tool is for educational purposes only. Always consult with a qualified financial advisor.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
