import numpy as np
import locale

# Set the locale for your desired formatting (e.g., en_US for US locale)
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def _lognormal_rate_params(mean, std):
    """Parameters of a normal log-rate whose simple rate has this mean and std.

    A simple rate drawn as exp(X) - 1, with X normal, stays above -100%.
    The returned mean and std are for X, chosen so the simple rate matches
    the mean and standard deviation passed in.
    """
    gross = 1.0 + mean
    variance = np.log(1.0 + (std / gross) ** 2)
    return np.log(gross) - 0.5 * variance, np.sqrt(variance)

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

    return_mu, return_sigma = _lognormal_rate_params(returns_mean, returns_std)
    inflation_mu, inflation_sigma = _lognormal_rate_params(inflation_mean, inflation_std)

    for i in range(1, num_years):
        annual_returns = np.exp(np.random.normal(return_mu, return_sigma, num_simulations)) - 1.0

        # Apply return growth and then withdrawal per simulation
        portfolio_values[i, :] = portfolio_values[i - 1, :] * (1 + annual_returns) - withdrawals

        # Prevent portfolio from going negative
        portfolio_values[i, :] = np.maximum(portfolio_values[i, :], 0)

        # Generate random withdrawal growth rates for each simulation
        withdrawal_growth_rates = np.exp(np.random.normal(inflation_mu, inflation_sigma, num_simulations)) - 1.0
        withdrawals *= (1 + withdrawal_growth_rates)
        
        # Track cumulative inflation for each simulation
        cumulative_inflation_factors *= (1 + withdrawal_growth_rates)

    return portfolio_values, cumulative_inflation_factors
