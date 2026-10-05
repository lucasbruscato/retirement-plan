import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale

# Add the current directory to the path to import the monte_carlo_simulation function
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the monte_carlo_simulation function from the separate file
from monte_carlo_simulation import monte_carlo_simulation

# Set the locale for formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except locale.Error:
    # Fallback for systems where en_US locale is not available
    locale.setlocale(locale.LC_ALL, '')

st.set_page_config(
    page_title="Retirement Portfolio Simulation",
    page_icon="💰",
    layout="wide"
)

st.title("🏦 Retirement Portfolio Simulation")
st.markdown("Analyze your retirement portfolio's potential outcomes using Monte Carlo simulation")

# Sidebar for input parameters
st.sidebar.header("📊 Simulation Parameters")

# Investment parameters
st.sidebar.subheader("⁉️ Input Definition")
input_definition = st.sidebar.selectbox(
    'Would you like to input the current investment OR the monthly withdrawal?',
    ('Monthly Withdrawal', 'Current Investment')
)


# Dynamic input order based on input_definition
if input_definition == "Current Investment":
    st.sidebar.subheader("💼 Investment Settings")
    initial_investment = st.sidebar.number_input(
        "Current Investment ($)", 
        min_value=10000, 
        max_value=10000000, 
        value=2200000, 
        step=50000,
        format="%d"
    )

    returns_mean = st.sidebar.slider(
        "Expected Annual Return (%)", 
        min_value=0.0, 
        max_value=20.0, 
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
        value=45, 
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

    # Show Monthly Withdrawal value as an informative text box (no decimals)
    monthly_withdrawal = int(withdrawal_value // 12)
    st.sidebar.info(f"Monthly Withdrawal: ${monthly_withdrawal:,}")

elif input_definition == "Monthly Withdrawal":
    st.sidebar.subheader("💸 Withdrawal Settings")
    monthly_withdrawal = st.sidebar.number_input(
        "Monthly Withdrawal ($)",
        min_value=1000,
        max_value=100000,
        value=5000,
        step=500,
        format="%d"
    )
    withdrawal_value = monthly_withdrawal * 12

    withdrawal_rate = st.sidebar.slider(
        "Initial Withdrawal Rate (%)", 
        min_value=1.0, 
        max_value=10.0, 
        value=2.7, 
        step=0.1
    ) / 100

    # Show Current Investment as an informative text box (no decimals)
    initial_investment = int(withdrawal_value / withdrawal_rate) if withdrawal_rate > 0 else 0
    st.sidebar.info(f"Current Investment: ${initial_investment:,}")

    # Investment settings
    st.sidebar.subheader("💼 Investment Settings")
    returns_mean = st.sidebar.slider(
        "Expected Annual Return (%)", 
        min_value=0.0, 
        max_value=20.0, 
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
        value=45, 
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
        col1, col2, col2_monthly, col3, col4 = st.columns(5)
        
        with col1:
            st.metric(
                "Current Investment", 
                f"${initial_investment:,.0f}"
            )

        with col2:
            st.metric(
                "Initial Annual Withdrawal", 
                f"${withdrawal_value:,.0f}"
            )

        with col2_monthly:
            st.metric(
                "Initial Monthly Withdrawal", 
                f"${(withdrawal_value/12):,.0f}"
            )
        
        with col3:
            st.metric(
                "Simulation Period", 
                f"{num_years} years"
            )
        
        with col4:
            success_rate = np.mean(final_portfolio_values > 0) * 100
            # Color code: green >=90, orange >=50, else red
            if success_rate >= 90:
                color = "#2ecc40"  # green
            elif success_rate >= 50:
                color = "#ffae42"  # orange
            else:
                color = "#e74c3c"  # red
            st.markdown(
                f"<div style='background-color:{color};padding:10px;border-radius:8px;text-align:center;'>"
                f"<span style='color:white;font-size:24px;font-weight:bold;'>{success_rate:.1f}%</span><br>"
                f"<span style='color:white;'>Success Rate</span></div>",
                unsafe_allow_html=True
            )
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Results Summary", "📈 Distributions", "🎯 Percentiles", "📉 Portfolio Paths"])
        
        with tab1:
            st.subheader(f"Simulation Results Summary (at the end of {num_years} years)")
            
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
            st.subheader(f"Portfolio Value Distributions (at the end of {num_years} years)")
            
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
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader(f"Percentile Analysis (at the end of {num_years} years)")
            
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
            st.subheader(f"Portfolio Evolution Over {num_years} Years (Sample Paths)")
            
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
                xaxis_title="Years from Now",
                yaxis_title="Portfolio Value ($)",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Configure your parameters in the sidebar and click 'Run Simulation' to see results!")

# Footer
st.markdown("---")
st.markdown("💡 **Note:** This simulation is for educational purposes only and should not be considered as financial advice.")
