import numpy as np
import locale

# Set the locale for your desired formatting (e.g., en_US for US locale)
locale.setlocale(locale.LC_ALL, 'en_US')

def monte_carlo_simulation(
    initial_investment, 
    mean_return, 
    std_dev, 
    num_years, 
    num_simulations, 
    withdrawal_rate, 
    withdrawal_mean_growth, 
    withdrawal_std_dev_growth):

    portfolio_values = np.zeros((num_years, num_simulations))
    portfolio_values[0, :] = initial_investment

    for i in range(1, num_years):
        annual_returns = np.random.normal(mean_return, std_dev, num_simulations)
        portfolio_values[i, :] = portfolio_values[i - 1, :] * (1 + annual_returns) - withdrawal_rate

        # Generate random withdrawal growth rates for each year (inflation)
        withdrawal_growth_rates = np.random.normal(withdrawal_mean_growth, withdrawal_std_dev_growth, num_simulations)

        withdrawal_rate *= (1 + withdrawal_growth_rates)

    return portfolio_values

# The input for all calculations
initial_investment = 1_700_000
mean_return = 0.06
std_dev = 0.01
num_years = 63
num_simulations = 100_000
withdrawal_rate = initial_investment * 0.027
withdrawal_mean_growth = 0.03
withdrawal_std_dev_growth = 0.03

simulated_portfolios = monte_carlo_simulation(
    initial_investment, 
    mean_return, 
    std_dev, 
    num_years, 
    num_simulations, 
    withdrawal_rate, 
    withdrawal_mean_growth, 
    withdrawal_std_dev_growth
)

# Calculate the final portfolio value after all the years for each simulation
final_portfolio_values = simulated_portfolios[-1, :]
# print("final_portfolio_values:", final_portfolio_values)

# Calculate statistics of the final portfolio values
mean_portfolio_value = np.mean(final_portfolio_values)
median_portfolio_value = np.median(final_portfolio_values)
percentile_low = np.percentile(final_portfolio_values, 5)
percentile_high = np.percentile(final_portfolio_values, 95)

# Format the numbers with thousand commas using locale.format_string
initial_investment_str = locale.format_string("%.0f", initial_investment, grouping=True)
withdrawal_rate_str = locale.format_string("%.0f", withdrawal_rate, grouping=True)
mean_portfolio_value_str = locale.format_string("%.0f", mean_portfolio_value, grouping=True)
median_portfolio_value_str = locale.format_string("%.0f", median_portfolio_value, grouping=True)
percentile_low_str = locale.format_string("%.0f", percentile_low, grouping=True)
percentile_high_str = locale.format_string("%.0f", percentile_high, grouping=True)

print(f"Initial Investment: ${initial_investment_str}")
print(f"Initial Withdrawal: ${withdrawal_rate_str} at a rate of: {np.round(withdrawal_rate/initial_investment, 4)}")
print(f"Mean Portfolio Value after X years: ${mean_portfolio_value_str}")
print(f"Median Portfolio Value after X years: ${median_portfolio_value_str}")
print(f"Low Percentile after X years: ${percentile_low_str}")
print(f"High Percentile after X years: ${percentile_high_str}")
