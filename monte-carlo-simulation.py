import numpy as np
import locale

# Set the locale for your desired formatting (e.g., en_US for US locale)
locale.setlocale(locale.LC_ALL, 'en_US')

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

# Input parameters
initial_investment = 2_200_000.0
returns_mean = 0.06
returns_std = 0.01
age = 50
num_years = 100 - age
num_simulations = 1_000_000
withdrawal_value = initial_investment * 0.027
inflation_mean = 0.03
inflation_std = 0.03

# Run the simulation
simulated_portfolios, cumulative_inflation_factors = monte_carlo_simulation(
    initial_investment, 
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

# Format numbers
initial_investment_str = locale.format_string("%.0f", initial_investment, grouping=True)
withdrawal_value_str = locale.format_string("%.0f", withdrawal_value, grouping=True)

# Output
print(f"Initial Investment: ${initial_investment_str}")
print(f"Initial Withdrawal: ${withdrawal_value_str} at a rate of: {np.round(withdrawal_value/initial_investment, 4)}")
print(f"\nPortfolio Value Percentiles after {num_years} years:")

# Print percentiles from 5 to 95 in increments of 5
for percentile in range(5, 100, 5):
    percentile_value = np.percentile(final_portfolio_values, percentile)
    percentile_value_str = locale.format_string("%.0f", percentile_value, grouping=True)
    print(f"{percentile}th Percentile: ${percentile_value_str}")

# Calculate inflation-adjusted values (real purchasing power in today's dollars)
# Using the actual withdrawal_growth_rates from each simulation
final_portfolio_values_real = final_portfolio_values / cumulative_inflation_factors

print(f"\nPortfolio Value Percentiles after {num_years} years (Inflation-Adjusted to today's purchasing power):")
print(f"Based on actual simulated withdrawal growth rates (inflation proxy)")

# Print inflation-adjusted percentiles from 5 to 95 in increments of 5
for percentile in range(5, 100, 5):
    percentile_value_real = np.percentile(final_portfolio_values_real, percentile)
    percentile_value_real_str = locale.format_string("%.0f", percentile_value_real, grouping=True)
    print(f"{percentile}th Percentile: ${percentile_value_real_str}")
