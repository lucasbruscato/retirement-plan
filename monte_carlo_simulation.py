import numpy as np
import locale

# Set the locale for your desired formatting (e.g., en_US for US locale)
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

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

    # Initialize withdrawals as a vector (per simulation), ensure float dtype
    withdrawals = np.full(num_simulations, float(withdrawal_value), dtype=float)
    
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
