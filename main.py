import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale
import sys
import os

# Add the current directory to the path to import the monte_carlo_simulation function
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the monte_carlo_simulation function from the separate file
def monte_carlo_simulation(
    initial_investment, 
    returns_mean, 
    returns_std, 
    num_years, 
    num_simulations, 
    withdrawal_value, 
    inflation_mean, 
    inflation_std):

    portfolio_values = np.zeros((num_years, num_simulations))
    portfolio_values[0, :] = initial_investment

    # Initialize withdrawals as a vector (per simulation)
    withdrawals = np.full(num_simulations, withdrawal_value)
    
    # Track cumulative inflation factors for each simulation
    cumulative_inflation_factors = np.ones(num_simulations)

    for i in range(1, num_years):
        annual_returns = np.random.normal(returns_mean, returns_std, num_simulations)

        # Apply return growth and then withdrawal per simulation
        portfolio_values[i, :] = portfolio_values[i - 1, :] * (1 + annual_returns) - withdrawals

        # Prevent portfolio from going negative
        portfolio_values[i, :] = np.maximum(portfolio_values[i, :], 0)

        # Generate random withdrawal growth rates for each simulation
        withdrawal_growth_rates = np.random.normal(inflation_mean, inflation_std, num_simulations)
        withdrawals *= (1 + withdrawal_growth_rates)
        
        # Track cumulative inflation for each simulation
        cumulative_inflation_factors *= (1 + withdrawal_growth_rates)

    return portfolio_values, cumulative_inflation_factors

# Set the locale for formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except locale.Error:
    # Fallback for systems where en_US locale is not available
    locale.setlocale(locale.LC_ALL, '')

st.set_page_config(
    page_title="Retirement Monte Carlo Simulation",
    page_icon="💰",
    layout="wide"
)

st.title("🏦 Retirement Portfolio Monte Carlo Simulation")
st.markdown("Analyze your retirement portfolio's potential outcomes using Monte Carlo simulation")

# Sidebar for input parameters
st.sidebar.header("📊 Simulation Parameters")

# Investment parameters
st.sidebar.subheader("💼 Investment Settings")
initial_investment = st.sidebar.number_input(
    "Initial Investment ($)", 
    min_value=10000, 
    max_value=10000000, 
    value=2200000, 
    step=50000,
    format="%d"
)

returns_mean = st.sidebar.slider(
    "Expected Annual Return (%)", 
    min_value=0.0, 
    max_value=15.0, 
    value=6.0, 
    step=0.1
) / 100

returns_std = st.sidebar.slider(
    "Return Volatility (Standard Deviation %)", 
    min_value=0.1, 
    max_value=10.0, 
    value=1.0, 
    step=0.1
) / 100

# Time parameters
st.sidebar.subheader("⏰ Time Settings")
age = st.sidebar.number_input(
    "Current Age", 
    min_value=18, 
    max_value=90, 
    value=50, 
    step=1
)

retirement_age = st.sidebar.number_input(
    "Life Expectancy Age", 
    min_value=age, 
    max_value=150, 
    value=100, 
    step=1
)

num_years = retirement_age - age

# Withdrawal parameters
st.sidebar.subheader("💸 Withdrawal Settings")
withdrawal_rate = st.sidebar.slider(
    "Initial Withdrawal Rate (%)", 
    min_value=1.0, 
    max_value=10.0, 
    value=2.7, 
    step=0.1
) / 100

withdrawal_value = initial_investment * withdrawal_rate

# Inflation parameters
st.sidebar.subheader("📈 Inflation Settings")
inflation_mean = st.sidebar.slider(
    "Expected Annual Inflation (%)", 
    min_value=0.0, 
    max_value=20.0, 
    value=3.0, 
    step=0.1
) / 100

inflation_std = st.sidebar.slider(
    "Inflation Volatility (%)", 
    min_value=0.1, 
    max_value=10.0, 
    value=3.0, 
    step=0.1
) / 100

# Simulation parameters
st.sidebar.subheader("🎲 Simulation Settings")
simulation_options = [10000, 50000, 100000, 500000, 1000000]
simulation_labels = [f"{v:,}" for v in simulation_options]
selected_label = st.sidebar.selectbox(
    "Number of Simulations",
    simulation_labels,
    index=2
)
num_simulations = simulation_options[simulation_labels.index(selected_label)]

# Main content
if st.sidebar.button("🚀 Run Simulation", type="primary"):
    with st.spinner("Running Monte Carlo simulation..."):
        # Run the simulation
        simulated_portfolios, cumulative_inflation_factors = monte_carlo_simulation(
            float(initial_investment), 
            returns_mean, 
            returns_std, 
            num_years, 
            num_simulations, 
            withdrawal_value, 
            inflation_mean, 
            inflation_std
        )
        
        # Extract final year results
        final_portfolio_values = simulated_portfolios[-1, :]
        final_portfolio_values_real = final_portfolio_values / cumulative_inflation_factors
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Initial Investment", 
                f"${initial_investment:,.0f}"
            )
        
        with col2:
            st.metric(
                "Annual Withdrawal", 
                f"${withdrawal_value:,.0f}"
            )
        
        with col3:
            st.metric(
                "Simulation Period", 
                f"{num_years} years"
            )
        
        with col4:
            success_rate = np.mean(final_portfolio_values > 0) * 100
            st.metric(
                "Success Rate", 
                f"{success_rate:.1f}%"
            )
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Results Summary", "📈 Distributions", "🎯 Percentiles", "📉 Portfolio Paths"])
        
        with tab1:
            st.subheader("Simulation Results Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Nominal Values (Future Monetary Values)**")
                median_nominal = np.median(final_portfolio_values)
                p5_nominal = np.percentile(final_portfolio_values, 5)
                p95_nominal = np.percentile(final_portfolio_values, 95)
                st.write(f"Median: ${median_nominal:,.0f}")
                st.write(f"5th Percentile: ${p5_nominal:,.0f}")
                st.write(f"95th Percentile: ${p95_nominal:,.0f}")

            with col2:
                st.markdown("**Real Values (Today's Purchasing Power)**")
                median_real = np.median(final_portfolio_values_real)
                p5_real = np.percentile(final_portfolio_values_real, 5)
                p95_real = np.percentile(final_portfolio_values_real, 95)
                st.write(f"Median: ${median_real:,.0f}")
                st.write(f"5th Percentile: ${p5_real:,.0f}")
                st.write(f"95th Percentile: ${p95_real:,.0f}")
        
        with tab2:
            st.subheader("Portfolio Value Distributions")
            
            # Create histogram
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Nominal Values", "Inflation-Adjusted Values"),
                x_title="Portfolio Value ($)"
            )
            
            # Nominal values histogram
            fig.add_trace(
                go.Histogram(
                    x=final_portfolio_values,
                    nbinsx=50,
                    name="Nominal",
                    opacity=0.7
                ),
                row=1, col=1
            )
            
            # Real values histogram
            fig.add_trace(
                go.Histogram(
                    x=final_portfolio_values_real,
                    nbinsx=50,
                    name="Real",
                    opacity=0.7
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=500,
                showlegend=False,
                title_text=f"Distribution of Portfolio Values After {num_years} Years"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Percentile Analysis")
            
            # Create percentile data
            percentiles = list(range(5, 100, 5))
            nominal_percentiles = [np.percentile(final_portfolio_values, p) for p in percentiles]
            real_percentiles = [np.percentile(final_portfolio_values_real, p) for p in percentiles]
            
            # Create DataFrame for display
            percentile_df = pd.DataFrame({
                'Percentile': [f"{p}th" for p in percentiles],
                'Nominal Value ($)': [f"${v:,.0f}" for v in nominal_percentiles],
                'Real Value ($)': [f"${v:,.0f}" for v in real_percentiles]
            })
            
            st.dataframe(percentile_df, use_container_width=True, hide_index=True)
            
            # Percentile chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=percentiles,
                y=nominal_percentiles,
                mode='lines+markers',
                name='Nominal Values',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=percentiles,
                y=real_percentiles,
                mode='lines+markers',
                name='Real Values',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title=f"Portfolio Value Percentiles After {num_years} Years",
                xaxis_title="Percentile",
                yaxis_title="Portfolio Value ($)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.subheader("Sample Portfolio Paths")
            
            # Show a sample of portfolio paths
            sample_size = min(1000, num_simulations)
            sample_indices = np.random.choice(num_simulations, sample_size, replace=False)
            sample_portfolios = simulated_portfolios[:, sample_indices]
            
            years = list(range(num_years))
            
            fig = go.Figure()
            
            # Add sample paths
            for i in range(min(100, sample_size)):  # Show max 100 paths for performance
                fig.add_trace(go.Scatter(
                    x=years,
                    y=sample_portfolios[:, i],
                    mode='lines',
                    line=dict(width=0.5, color='lightblue'),
                    showlegend=False,
                    hovertemplate=f'Year: %{{x}}<br>Value: $%{{y:,.0f}}<extra></extra>'
                ))
            
            # Add median path
            median_path = np.median(sample_portfolios, axis=1)
            fig.add_trace(go.Scatter(
                x=years,
                y=median_path,
                mode='lines',
                line=dict(width=3, color='red'),
                name='Median Path'
            ))
            
            # Add percentile bands
            p10_path = np.percentile(sample_portfolios, 10, axis=1)
            p90_path = np.percentile(sample_portfolios, 90, axis=1)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=p90_path,
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.add_trace(go.Scatter(
                x=years,
                y=p10_path,
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(0,100,80,0.2)',
                name='10th-90th Percentile Range',
                hoverinfo='skip'
            ))
            
            fig.update_layout(
                title=f"Portfolio Evolution Over {num_years} Years (Sample Paths)",
                xaxis_title="Years from Now",
                yaxis_title="Portfolio Value ($)",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Configure your parameters in the sidebar and click 'Run Simulation' to see results!")
    
    # Show example scenario
    st.subheader("📋 Example Scenario")
    st.markdown(f"""
    **Current Settings:**
    - Initial Investment: ${initial_investment:,.0f}
    - Expected Return: {returns_mean*100:.1f}% ± {returns_std*100:.1f}%
    - Annual Withdrawal: ${withdrawal_value:,.0f} ({withdrawal_rate*100:.1f}% of portfolio)
    - Simulation Period: {num_years} years (age {age} to {retirement_age})
    - Expected Inflation: {inflation_mean*100:.1f}% ± {inflation_std*100:.1f}%
    - Number of Simulations: {num_simulations:,}
    """)

# Footer
st.markdown("---")
st.markdown("💡 **Note:** This simulation is for educational purposes only and should not be considered as financial advice.")
