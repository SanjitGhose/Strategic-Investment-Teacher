import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Strategic Investment Planner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
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
    border: 1px solid #475569;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.metric-card {
    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
    padding: 1.2rem;
    border-radius: 0.8rem;
    border: 1px solid #6b7280;
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
    border: 1px solid #d97706;
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
    border: 1px solid #10b981;
    margin: 1rem 0;
}

.warning-message {
    background: linear-gradient(135deg, #92400e 0%, #b45309 100%);
    padding: 1.5rem;
    border-radius: 0.8rem;
    color: white;
    text-align: center;
    font-weight: bold;
    font-size: 1.1rem;
    border: 1px solid #f59e0b;
    margin: 1rem 0;
}

.info-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
    padding: 1.2rem;
    border-radius: 0.8rem;
    color: white;
    border: 1px solid #6366f1;
    margin: 0.5rem 0;
}

.debt-card {
    background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%);
    padding: 1.5rem;
    border-radius: 0.8rem;
    color: white;
    border: 1px solid #ea580c;
    margin: 1rem 0;
}

.scenario-header {
    background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
    padding: 1rem;
    border-radius: 0.5rem;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
    border: 1px solid #6366f1;
}

.time-to-goal {
    background: linear-gradient(135deg, #065f46 0%, #047857 100%);
    padding: 1rem;
    border-radius: 0.8rem;
    color: white;
    text-align: center;
    border: 1px solid #10b981;
    margin: 0.5rem 0;
    font-weight: bold;
}

.educational-card {
    background: linear-gradient(135deg, #581c87 0%, #6b21a8 100%);
    padding: 1.2rem;
    border-radius: 0.8rem;
    color: white;
    border: 1px solid #a855f7;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Educational content
EDUCATIONAL_CONTENT = {
    "mutual_funds": {
        "title": "Mutual Funds",
        "content": """
*What are Mutual Funds?*
- Pool of money from many investors
- Professionally managed by fund managers
- Diversified portfolio of stocks, bonds, or other securities
- Suitable for long-term wealth creation

*Types:*
- Equity Funds (High risk, high return)
- Debt Funds (Low risk, moderate return)
- Hybrid Funds (Balanced approach)

*Risk Factors:*
- Market risk varies with economic conditions
- Bull markets: Lower perceived risk due to optimism
- Bear markets: Higher risk due to uncertainty
        """
    },
    "stocks": {
        "title": "Stocks",
        "content": """
*What are Stocks?*
- Ownership shares in a company
- Potential for high returns but volatile
- Requires research and market knowledge
- Best for long-term investment

*Key Points:*
- Dividend income + Capital appreciation
- Market risk varies significantly with conditions
- Liquidity is good
- Beta typically higher in volatile markets
        """
    },
    "fd": {
        "title": "Fixed Deposits",
        "content": """
*What are Fixed Deposits?*
- Safe investment with guaranteed returns
- Fixed interest rate for specific tenure
- No market risk involved
- Lower returns compared to equity

*Features:*
- Capital protection (risk remains constant)
- Predictable returns
- Various tenure options
- Inflation risk in long term
        """
    },
    "bonds": {
        "title": "Bonds",
        "content": """
*What are Bonds?*
- Debt instruments issued by companies/government
- Regular interest payments (coupon)
- Lower risk than stocks
- Good for steady income

*Risk Variations:*
- Interest rate risk varies with market conditions
- Credit risk can change with issuer's financial health
- Duration risk affects bond prices
        """
    },
    "aif": {
        "title": "Alternative Investment Funds",
        "content": """
*What are AIFs?*
- Privately pooled investment funds
- Higher minimum investment
- Less regulated than mutual funds
- Potential for higher returns

*Risk Profile:*
- Highly sensitive to market conditions
- Risk multiplies in bear markets
- Can provide hedge in specific strategies
        """
    },
    "sharpe_ratio": {
        "title": "Sharpe Ratio",
        "content": """
*What is Sharpe Ratio?*
- Measures risk-adjusted return
- Formula: (Portfolio Return - Risk-free Rate) / Standard Deviation
- Higher ratio = Better risk-adjusted performance

*Interpretation:*
- > 1.0: Excellent risk-adjusted returns
- 0.5-1.0: Good risk-adjusted returns
- < 0.5: Poor risk-adjusted returns

*Investment Horizon Impact:*
- Calculated for your specific investment period
- Helps compare different strategies
- Time-weighted risk assessment
        """
    }
}

def calculate_scenario_risk_multipliers(scenario):
    """Calculate risk multipliers based on market scenarios"""
    multipliers = {
        'normal': {
            'mutual_funds': 1.0, 'stocks': 1.0, 'fd': 1.0, 'bonds': 1.0, 'aif': 1.0
        },
        'bullish': {
            'mutual_funds': 0.7, 'stocks': 0.8, 'fd': 1.0, 'bonds': 0.9, 'aif': 0.8
        },
        'bearish': {
            'mutual_funds': 1.4, 'stocks': 1.6, 'fd': 1.0, 'bonds': 1.2, 'aif': 1.8
        }
    }
    return multipliers[scenario]

def calculate_investment_returns(amount, years, monthly_investment, allocation, scenario='normal', debt_emi=0):
    """Enhanced calculation with scenario-based risk and debt obligations"""
    
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
    
    # Base risk levels
    base_asset_risks = {
        'mutual_funds': 0.18, 'stocks': 0.25, 'fd': 0.02, 'bonds': 0.05, 'aif': 0.30
    }
    
    # Apply scenario-based risk multipliers
    risk_multipliers = calculate_scenario_risk_multipliers(scenario)
    asset_risks = {
        asset: base_asset_risks[asset] * risk_multipliers[asset] 
        for asset in base_asset_risks
    }
    
    asset_betas = {
        'mutual_funds': 0.85, 'stocks': 1.2, 'fd': 0.0, 'bonds': 0.1, 'aif': 1.5
    }
    
    returns = asset_returns[scenario]
    
    # Calculate portfolio metrics
    portfolio_return = sum(allocation[asset] * returns[asset] for asset in allocation)
    portfolio_risk = sum(allocation[asset] * asset_risks[asset] for asset in allocation)
    portfolio_beta = sum(allocation[asset] * asset_betas[asset] for asset in allocation)
    
    # Calculate future value
    months = years * 12
    monthly_return = portfolio_return / 12
    
    # Adjust for debt EMI impact
    effective_monthly_investment = max(0, monthly_investment - debt_emi)
    
    # Future value of lump sum
    fv_lumpsum = amount * (1 + portfolio_return) ** years
    
    # Future value of monthly investments (adjusted for debt)
    if effective_monthly_investment > 0:
        fv_monthly = effective_monthly_investment * (((1 + monthly_return) ** months - 1) / monthly_return)
    else:
        fv_monthly = 0
    
    total_future_value = fv_lumpsum + fv_monthly
    total_investment = amount + (monthly_investment * months)
    total_debt_paid = debt_emi * months
    
    # Calculate time-adjusted Sharpe ratio
    risk_free_rate = 0.07
    excess_return = portfolio_return - risk_free_rate
    annualized_sharpe = excess_return / portfolio_risk if portfolio_risk > 0 else 0
    
    # Time-adjusted Sharpe ratio
    time_adjusted_sharpe = annualized_sharpe * np.sqrt(years)
    
    return {
        'total_investment': total_investment,
        'future_value': total_future_value,
        'gains': total_future_value - total_investment,
        'portfolio_return': portfolio_return,
        'portfolio_risk': portfolio_risk,
        'portfolio_beta': portfolio_beta,
        'sharpe_ratio': annualized_sharpe,
        'time_adjusted_sharpe': time_adjusted_sharpe,
        'effective_monthly_investment': effective_monthly_investment,
        'total_debt_paid': total_debt_paid
    }

def calculate_time_to_goal(target_amount, initial_amount, monthly_investment, portfolio_return, debt_emi=0):
    """Calculate time needed to reach goal considering debt obligations"""
    effective_monthly = max(0, monthly_investment - debt_emi)
    
    if portfolio_return <= 0 or (initial_amount <= 0 and effective_monthly <= 0):
        return None
    
    if initial_amount >= target_amount:
        return 0
    
    if effective_monthly <= 0:
        # Only lump sum
        years_needed = np.log(target_amount / initial_amount) / np.log(1 + portfolio_return)
    else:
        # Combined lump sum and SIP
        monthly_return = portfolio_return / 12
        if initial_amount > 0:
            # Complex calculation for combined investment
            # Using iterative approach for accuracy
            for months in range(1, 1200):  # Max 100 years
                fv_lump = initial_amount * (1 + portfolio_return) ** (months/12)
                if effective_monthly > 0:
                    fv_sip = effective_monthly * (((1 + monthly_return) ** months - 1) / monthly_return)
                else:
                    fv_sip = 0
                if fv_lump + fv_sip >= target_amount:
                    years_needed = months / 12
                    break
            else:
                years_needed = None
        else:
            # Only SIP
            months_needed = np.log(1 + (target_amount * monthly_return) / effective_monthly) / np.log(1 + monthly_return)
            years_needed = months_needed / 12
    
    return years_needed if years_needed and years_needed < 100 else None

def show_educational_popup(content_key):
    """Show educational content in expander"""
    if content_key in EDUCATIONAL_CONTENT:
        content = EDUCATIONAL_CONTENT[content_key]
        with st.expander(f"Learn about {content['title']}", expanded=False):
            st.markdown(f"""
            <div class="educational-card">
            {content['content']}
            </div>
            """, unsafe_allow_html=True)

def create_metric_card(title, value, color="#ffffff"):
    """Create a professional metric card"""
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
        <h1>Strategic Investment Planner</h1>
        <p>Professional investment planning with advanced scenario analysis and debt integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>IMPORTANT DISCLAIMER:</strong> This application is for educational purposes only.
        The returns and calculations shown are based on mathematical models and should not be considered as investment advice.
        Past performance does not guarantee future results. Please consult with a SEBI registered investment advisor.
        <br><br>
        <strong>Features:</strong> Includes debt analysis, scenario-based risk modeling, and time-weighted Sharpe ratios.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for inputs
    st.sidebar.header("Investment Parameters")
    
    # Investment type selection
    st.sidebar.subheader("Investment Strategy")
    investment_type = st.sidebar.radio(
        "Choose your investment approach:",
        ["Lump Sum", "SIP (Systematic Investment Plan)", "Hybrid (Lump Sum + SIP)"],
        help="Select your preferred investment strategy"
    )
    
    # Investment amounts based on type
    initial_amount = 0
    monthly_investment = 0
    
    if investment_type == "Lump Sum":
        initial_amount = st.sidebar.number_input(
            "Total Lump Sum Investment (₹)",
            min_value=1000,
            value=100000,
            step=5000,
            help="Enter your one-time investment amount"
        )
        monthly_investment = 0
    
    elif investment_type == "SIP (Systematic Investment Plan)":
        monthly_investment = st.sidebar.number_input(
            "Monthly SIP Amount (₹)",
            min_value=500,
            value=5000,
            step=500,
            help="Enter your monthly SIP amount"
        )
        initial_amount = 0
    
    else:  # Hybrid
        initial_amount = st.sidebar.number_input(
            "Initial Lump Sum Investment (₹)",
            min_value=1000,
            value=50000,
            step=5000,
            help="Enter your initial lump sum amount"
        )
        monthly_investment = st.sidebar.number_input(
            "Monthly SIP Amount (₹)",
            min_value=500,
            value=5000,
            step=500,
            help="Enter your monthly SIP amount"
        )
    
    # Time horizon
    time_horizon = st.sidebar.slider(
        "Investment Time Horizon (Years)",
        min_value=1,
        max_value=30,
        value=10,
        help="How long do you plan to invest?"
    )
    
    # Debt Management Section
    st.sidebar.subheader("Debt Analysis (Optional)")
    has_debt = st.sidebar.checkbox("I have existing debt obligations", help="Check if you have loans/debt to consider")
    
    debt_amount = 0
    debt_rate = 0
    debt_emi = 0
    debt_tenure = 0
    
    if has_debt:
        debt_amount = st.sidebar.number_input(
            "Total Debt Outstanding (₹)",
            min_value=0,
            value=0,
            step=10000,
            help="Enter your total outstanding debt"
        )
        
        debt_rate = st.sidebar.slider(
            "Debt Interest Rate (%)",
            min_value=5.0,
            max_value=25.0,
            value=12.0,
            step=0.5,
            help="Annual interest rate on your debt"
        )
        
        debt_emi_option = st.sidebar.radio(
            "EMI Calculation:",
            ["Let me enter EMI", "Calculate EMI for me"]
        )
        
        if debt_emi_option == "Let me enter EMI":
            debt_emi = st.sidebar.number_input(
                "Monthly EMI (₹)",
                min_value=0,
                value=0,
                step=1000,
                help="Enter your monthly EMI amount"
            )
        else:
            debt_tenure = st.sidebar.number_input(
                "Debt Tenure (Years)",
                min_value=1,
                max_value=30,
                value=5,
                help="Remaining years to pay off debt"
            )
            
            if debt_amount > 0 and debt_tenure > 0:
                monthly_rate = debt_rate / (12 * 100)
                num_payments = debt_tenure * 12
                if monthly_rate > 0:
                    debt_emi = debt_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
                else:
                    debt_emi = debt_amount / num_payments
                
                st.sidebar.markdown(f"""
                <div class="debt-card">
                    <strong>Calculated EMI:</strong><br>
                    ₹{debt_emi:,.0f} per month
                </div>
                """, unsafe_allow_html=True)
    
    # Investment goals
    st.sidebar.subheader("Investment Goals")
    goal_type = st.sidebar.selectbox(
        "Select Your Primary Goal",
        ["Retirement", "Child Education", "House Purchase", "Wealth Creation", "Emergency Fund", "Debt Freedom"]
    )
    
    target_amount = st.sidebar.number_input(
        "Target Amount (₹)",
        min_value=50000,
        value=1000000,
        step=50000,
        help="How much do you want to accumulate?"
    )
    
    # Inflation adjustment
    inflation_rate = st.sidebar.slider(
        "Expected Inflation Rate (%)",
        min_value=3.0,
        max_value=8.0,
        value=4.8,
        step=0.1,
        help="Adjust target amount for inflation"
    )
    
    real_target = target_amount * ((1 + inflation_rate/100) ** time_horizon)
    
    st.sidebar.markdown(f"""
    <div class="info-box">
        <strong>Inflation Adjusted Target:</strong><br>
        ₹{real_target:,.0f}
    </div>
    """, unsafe_allow_html=True)
    
    # Asset allocation
    st.sidebar.subheader("Portfolio Allocation")
    
    # Preset allocation options
    preset = st.sidebar.selectbox(
        "Choose Preset or Customize",
        ["Custom", "Conservative", "Balanced", "Aggressive", "Ultra Aggressive"]
    )
    
    if preset == "Conservative":
        mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation = 20, 10, 40, 25, 5
    elif preset == "Balanced":
        mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation = 40, 25, 15, 15, 5
    elif preset == "Aggressive":
        mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation = 50, 35, 5, 5, 5
    elif preset == "Ultra Aggressive":
        mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation = 40, 40, 0, 5, 15
    else:  # Custom
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
    
    if preset != "Custom":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.write(f"MF: {mf_allocation}%")
            st.write(f"FD: {fd_allocation}%")
            st.write(f"AIF: {aif_allocation}%")
        with col2:
            st.write(f"Stocks: {stocks_allocation}%")
            st.write(f"Bonds: {bonds_allocation}%")
    
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
    
    # Calculate total monthly outflow
    total_monthly_outflow = monthly_investment + debt_emi
    if total_monthly_outflow > 0:
        st.sidebar.markdown(f"""
        <div class="info-box">
            <strong>Monthly Financial Summary:</strong><br>
            Investment: ₹{monthly_investment:,.0f}<br>
            Debt EMI: ₹{debt_emi:,.0f}<br>
            <strong>Total Outflow: ₹{total_monthly_outflow:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Main calculations
    st.header("Investment Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    scenarios = ['normal', 'bullish', 'bearish']
    scenario_names = ['Normal Market', 'Bull Market', 'Bear Market']
    scenario_descriptions = [
        'Stable market conditions with average returns',
        'Rising market with above-average returns and lower risk',
        'Declining market with below-average returns and higher risk'
    ]
    
    results = {}
    time_to_goals = {}
    
    for scenario in scenarios:
        results[scenario] = calculate_investment_returns(
            initial_amount, time_horizon, monthly_investment, allocation, scenario, debt_emi
        )
        
        # Calculate time to goal for each scenario
        time_to_goals[scenario] = calculate_time_to_goal(
            real_target, initial_amount, monthly_investment, 
            results[scenario]['portfolio_return'], debt_emi
        )
    
    # Display results
    for i, scenario in enumerate(scenarios):
        result = results[scenario]
        time_to_goal = time_to_goals[scenario]
        
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="scenario-header">
                <h3>{scenario_names[i]}</h3>
                <p style="font-size: 0.9rem; margin: 0.5rem 0;">{scenario_descriptions[i]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Total Investment", 
                f"₹{result['total_investment']:,.0f}", "#94a3b8"), unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Future Value", 
                f"₹{result['future_value']:,.0f}", "#22c55e"), unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Total Gains", 
                f"₹{result['gains']:,.0f}", "#f59e0b"), unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Portfolio Return", 
                f"{result['portfolio_return']*100:.1f}%", "#8b5cf6"), unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Scenario Risk", 
                f"{result['portfolio_risk']*100:.1f}%", "#ef4444"), unsafe_allow_html=True)
            
            st.markdown(create_metric_card("Time-Adj Sharpe", 
                f"{result['time_adjusted_sharpe']:.2f}", "#06b6d4"), unsafe_allow_html=True)
            
            # Time to goal display
            if time_to_goal and time_to_goal < 100:
                st.markdown(f"""
                <div class="time-to-goal">
                    Time to Goal<br>
                    <strong>{time_to_goal:.1f} years</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #7c2d12; padding: 1rem; border-radius: 0.8rem; color: white; text-align: center; border: 1px solid #ea580c; margin: 0.5rem 0;">
                    Goal Not Achievable<br>
                    <strong>Review Strategy</strong>
                </div>
                """, unsafe_allow_html=True)
            
            # Debt impact display
            if debt_emi > 0:
                st.markdown(create_metric_card("Effective Investment", 
                    f"₹{result['effective_monthly_investment']:,.0f}/mo", "#f97316"), unsafe_allow_html=True)
    
    # Goal achievement analysis
    st.header("Goal Achievement Analysis")
    
    normal_result = results['normal']
    normal_time = time_to_goals['normal']
    
    col1, col2 = st.columns(2)
    
    with col1:
        if normal_result['future_value'] >= real_target:
            st.markdown(f"""
            <div class="success-message">
                Congratulations! Your investment plan will achieve your goal!<br>
                Target: ₹{real_target:,.0f}<br>
                Projected: ₹{normal_result['future_value']:,.0f}<br>
                <strong>Surplus: ₹{normal_result['future_value'] - real_target:,.0f}</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            shortfall = real_target - normal_result['future_value']
            additional_monthly_needed = shortfall / (time_horizon * 12)
            
            st.markdown(f"""
            <div class="warning-message">
                You're on the right track! To reach your goal:<br>
                • Increase monthly SIP by ₹{additional_monthly_needed:,.0f}<br>
                • Or extend timeline by {((real_target/normal_result['future_value'])(1/normal_result['portfolio_return']) - time_horizon):.1f} years<br>
                • Consider more aggressive allocation<br><br>
                <strong>Shortfall: ₹{shortfall:,.0f}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Scenario comparison
        st.markdown("""
        <div class="info-box">
            <h4>Scenario Comparison</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for i, scenario in enumerate(scenarios):
            time_val = time_to_goals[scenario]
            if time_val and time_val < 100:
                color = "#22c55e" if time_val <= time_horizon else "#f59e0b"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #374151 0%, #4b5563 100%); padding: 0.8rem; margin: 0.3rem 0; border-radius: 0.5rem; border-left: 4px solid {color};">
                    <strong>{scenario_names[i]}:</strong> {time_val:.1f} years
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #7c2d12 0%, #991b1b 100%); padding: 0.8rem; margin: 0.3rem 0; border-radius: 0.5rem; border-left: 4px solid #ef4444;">
                    <strong>{scenario_names[i]}:</strong> Goal not achievable
                </div>
                """, unsafe_allow_html=True)
    
    # Debt Impact Analysis (if applicable)
    if debt_emi > 0:
        st.header("Debt Impact Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_debt_interest = (debt_emi * debt_tenure * 12) - debt_amount if debt_tenure > 0 else 0
            st.markdown(f"""
            <div class="debt-card">
                <h4>Debt Summary</h4>
                Outstanding: ₹{debt_amount:,.0f}<br>
                Monthly EMI: ₹{debt_emi:,.0f}<br>
                Interest Rate: {debt_rate:.1f}%<br>
                Total Interest: ₹{total_debt_interest:,.0f}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Calculate scenario without debt
            no_debt_result = calculate_investment_returns(
                initial_amount, time_horizon, monthly_investment + debt_emi, allocation, 'normal', 0
            )
            
            opportunity_cost = no_debt_result['future_value'] - normal_result['future_value']
            st.markdown(f"""
            <div class="debt-card">
                <h4>Opportunity Cost</h4>
                Without Debt: ₹{no_debt_result['future_value']:,.0f}<br>
                With Debt: ₹{normal_result['future_value']:,.0f}<br>
                <strong>Lost Potential: ₹{opportunity_cost:,.0f}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Debt payoff recommendation
            debt_roi = debt_rate / 100
            portfolio_roi = normal_result['portfolio_return']
            
            recommendation = "Pay off debt first" if debt_roi > portfolio_roi else "Invest while servicing debt"
            color = "#ef4444" if debt_roi > portfolio_roi else "#22c55e"
            
            st.markdown(f"""
            <div class="debt-card">
                <h4>Recommendation</h4>
                Debt Cost: {debt_roi*100:.1f}%<br>
                Investment Return: {portfolio_roi*100:.1f}%<br>
                <strong style="color: {color};">{recommendation}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts Section
    st.header("Investment Projections & Analytics")
    
    # Create projection data
    years_range = list(range(1, min(time_horizon + 1, 21)))
    projection_data = {
        'Year': years_range,
        'Normal Market': [],
        'Bull Market': [],
        'Bear Market': []
    }
    
    for year in years_range:
        for i, scenario in enumerate(scenarios):
            temp_result = calculate_investment_returns(
                initial_amount, year, monthly_investment, allocation, scenario, debt_emi
            )
            projection_data[scenario_names[i]].append(temp_result['future_value'])
    
    df_projection = pd.DataFrame(projection_data)
    df_projection.set_index('Year', inplace=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Growth Projection")
        st.line_chart(df_projection)
        
        # Risk-Return scatter
        st.subheader("Risk vs Return Analysis")
        risk_return_data = pd.DataFrame({
            'Expected Return (%)': [
                results['normal']['portfolio_return'] * 100,
                results['bullish']['portfolio_return'] * 100,
                results['bearish']['portfolio_return'] * 100
            ],
            'Risk (%)': [
                results['normal']['portfolio_risk'] * 100,
                results['bullish']['portfolio_risk'] * 100,
                results['bearish']['portfolio_risk'] * 100
            ]
        }, index=['Normal', 'Bull', 'Bear'])
        st.scatter_chart(risk_return_data, x='Risk (%)', y='Expected Return (%)')
    
    with col2:
        st.subheader("Portfolio Allocation")
        allocation_data = pd.DataFrame({
            'Allocation (%)': [mf_allocation, stocks_allocation, fd_allocation, bonds_allocation, aif_allocation]
        }, index=['Mutual Funds', 'Stocks', 'Fixed Deposits', 'Bonds', 'AIF'])
        st.bar_chart(allocation_data)
        
        # Sharpe ratio comparison
        st.subheader("Time-Adjusted Sharpe Ratios")
        sharpe_data = pd.DataFrame({
            'Sharpe Ratio': [
                results['normal']['time_adjusted_sharpe'],
                results['bullish']['time_adjusted_sharpe'],
                results['bearish']['time_adjusted_sharpe']
            ]
        }, index=['Normal', 'Bull', 'Bear'])
        st.bar_chart(sharpe_data)
    
    # Learning Section
    st.header("Investment Education Hub")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Risk Management", type="secondary"):
            st.markdown(f"""
            <div class="educational-card">
                <h4>Risk Management in Different Markets</h4>
                <strong>Your Portfolio Risk Analysis:</strong><br>
                • Normal Market: {results['normal']['portfolio_risk']*100:.1f}%<br>
                • Bull Market: {results['bullish']['portfolio_risk']*100:.1f}%<br>
                • Bear Market: {results['bearish']['portfolio_risk']*100:.1f}%<br><br>
                
                <strong>Risk varies because:</strong><br>
                • Market sentiment affects volatility<br>
                • Bull markets reduce perceived risk<br>
                • Bear markets amplify uncertainty<br>
                • Asset correlations change with conditions
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Sharpe Ratio Deep Dive", type="secondary"):
            show_educational_popup("sharpe_ratio")
            st.markdown(f"""
            <div class="educational-card">
                <h4>Your Sharpe Ratio Analysis</h4>
                <strong>Time-Adjusted Sharpe Ratios:</strong><br>
                • Normal: {results['normal']['time_adjusted_sharpe']:.2f}<br>
                • Bull: {results['bullish']['time_adjusted_sharpe']:.2f}<br>
                • Bear: {results['bearish']['time_adjusted_sharpe']:.2f}<br><br>
                
                <strong>Investment Horizon: {time_horizon} years</strong><br>
                Higher ratios indicate better risk-adjusted returns over your investment period.
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Debt vs Investment", type="secondary"):
            debt_analysis = debt_rate - (normal_result['portfolio_return'] * 100) if has_debt else 0
            st.markdown(f"""
            <div class="educational-card">
                <h4>Debt vs Investment Strategy</h4>
                {"<strong>Your Situation:</strong><br>" if has_debt else ""}
                {f"• Debt Interest: {debt_rate:.1f}%<br>" if has_debt else ""}
                {f"• Portfolio Return: {normal_result['portfolio_return']*100:.1f}%<br>" if has_debt else ""}
                {f"• Cost Difference: {debt_analysis:+.1f}%<br><br>" if has_debt else ""}
                
                <strong>General Strategy:</strong><br>
                • High-interest debt (>15%): Pay off first<br>
                • Medium debt (8-15%): Balance both<br>
                • Low-interest debt (<8%): Invest more<br>
                • Consider tax implications
            </div>
            """, unsafe_allow_html=True)
    
    # Optimization Suggestions
    st.header("Portfolio Optimization Suggestions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Allocation Recommendations")
        
        # Age-based allocation suggestion
        user_age = st.number_input("Enter your age for personalized advice", min_value=18, max_value=80, value=35)
        equity_percent = min(100 - user_age, 80)
        debt_percent = 100 - equity_percent
        
        st.markdown(f"""
        <div class="info-box">
            <h4>Age-Based Allocation (Rule of Thumb)</h4>
            <strong>Age {user_age} Suggestion:</strong><br>
            • Equity (MF + Stocks + AIF): {equity_percent}%<br>
            • Debt (FD + Bonds): {debt_percent}%<br><br>
            
            <strong>Your Current Allocation:</strong><br>
            • Equity: {(mf_allocation + stocks_allocation + aif_allocation)}%<br>
            • Debt: {(fd_allocation + bonds_allocation)}%
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Timeline Optimization")
        
        optimal_scenarios = []
        for scenario in scenarios:
            time_val = time_to_goals[scenario]
            if time_val and time_val <= time_horizon:
                optimal_scenarios.append((scenario_names[scenarios.index(scenario)], time_val))
        
        if optimal_scenarios:
            best_scenario = min(optimal_scenarios, key=lambda x: x[1])
            st.markdown(f"""
            <div class="success-message">
                Best Case Scenario<br>
                <strong>{best_scenario[0]}</strong><br>
                Goal achievable in {best_scenario[1]:.1f} years
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-message">
                Consider These Optimizations:<br>
                • Increase monthly investment<br>
                • Extend timeline<br>
                • Higher equity allocation<br>
                • Reduce debt burden
            </div>
            """, unsafe_allow_html=True)
    
    # Export Results
    st.header("Investment Report Generator")
    
    if st.button("Generate Comprehensive Report", type="primary"):
        report_data = {
            'Investment Profile': {
                'Strategy': investment_type,
                'Initial Amount': f"₹{initial_amount:,}" if initial_amount > 0 else "₹0",
                'Monthly SIP': f"₹{monthly_investment:,}" if monthly_investment > 0 else "₹0",
                'Time Horizon': f"{time_horizon} years",
                'Target Amount': f"₹{target_amount:,}",
                'Inflation Adjusted Target': f"₹{real_target:,.0f}",
                'Primary Goal': goal_type
            },
            'Debt Profile': {
                'Has Debt': has_debt,
                'Debt Amount': f"₹{debt_amount:,}" if has_debt else "None",
                'Interest Rate': f"{debt_rate}%" if has_debt else "N/A",
                'Monthly EMI': f"₹{debt_emi:,.0f}" if has_debt else "None",
                'Effective Investment': f"₹{normal_result['effective_monthly_investment']:,.0f}/mo"
            },
            'Asset Allocation': {
                'Mutual Funds': f"{mf_allocation}%",
                'Stocks': f"{stocks_allocation}%",
                'Fixed Deposits': f"{fd_allocation}%",
                'Bonds': f"{bonds_allocation}%",
                'AIF': f"{aif_allocation}%"
            },
            'Scenario Analysis': {
                scenario: {
                    'Future Value': f"₹{results[scenario]['future_value']:,.0f}",
                    'Total Investment': f"₹{results[scenario]['total_investment']:,.0f}",
                    'Total Gains': f"₹{results[scenario]['gains']:,.0f}",
                    'Portfolio Return': f"{results[scenario]['portfolio_return']*100:.1f}%",
                    'Portfolio Risk': f"{results[scenario]['portfolio_risk']*100:.1f}%",
                    'Time-Adj Sharpe': f"{results[scenario]['time_adjusted_sharpe']:.2f}",
                    'Time to Goal': f"{time_to_goals[scenario]:.1f} years" if time_to_goals[scenario] and time_to_goals[scenario] < 100 else "Not achievable"
                } for scenario in scenarios
            },
            'Recommendations': {
                'Goal Achievable': normal_result['future_value'] >= real_target,
                'Best Scenario': min([(s, time_to_goals[s]) for s in scenarios if time_to_goals[s] and time_to_goals[s] < 100], key=lambda x: x[1], default=(None, None))[0],
                'Risk Level': "Low" if normal_result['portfolio_risk'] < 0.1 else "Medium" if normal_result['portfolio_risk'] < 0.2 else "High",
                'Debt Recommendation': "Pay off debt first" if (has_debt and debt_rate/100 > normal_result['portfolio_return']) else "Continue balanced approach"
            }
        }
        
        st.json(report_data)
        
        # Success message
        st.markdown("""
        <div class="success-message">
            Report Generated Successfully!<br>
            Copy the JSON data above to save your investment analysis
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Tips
    st.header("Investment Tips")
    
    tip_category = st.selectbox("Choose tip category:", [
        "Risk Management", "Tax Planning", "Market Timing", "Rebalancing", "Emergency Planning"
    ])
    
    tips = {
        "Risk Management": "Diversify across asset classes and review your risk tolerance annually. Your current portfolio risk varies from {:.1f}% to {:.1f}% across market scenarios.".format(
            results['bullish']['portfolio_risk']*100, results['bearish']['portfolio_risk']*100),
        "Tax Planning": "Consider ELSS funds for tax saving under 80C. Debt funds held >3 years get indexation benefits.",
        "Market Timing": "Time in the market beats timing the market. Your SIP approach helps average market volatility.",
        "Rebalancing": "Rebalance your portfolio annually or when allocation deviates by >5% from target.",
        "Emergency Planning": "Maintain 6-12 months of expenses in liquid funds before investing in growth assets."
    }
    
    st.markdown(f"""
    <div class="info-box">
        <h4>{tip_category}</h4>
        {tips[tip_category]}
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem; padding: 2rem;">
        <h3 style="color: #8b5cf6;">Strategic Investment Planner</h3>
        <p>Advanced Financial Planning & Investment Education Platform</p>
        <p>Features: Scenario Analysis | Debt Integration | Time-Weighted Sharpe Ratios | Risk Modeling</p>
        <p><em>Educational purposes only. Consult certified financial advisors for investment decisions.</em></p>
        
        <div style="margin-top: 2rem; padding: 1rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 0.5rem;">
            <p style="color: #22c55e; font-weight: bold;">Made for Financial Literacy</p>
            <p style="font-size: 0.8rem;">Empowering investors with sophisticated tools and real-world scenarios</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if _name_ == "_main_":
    main()
