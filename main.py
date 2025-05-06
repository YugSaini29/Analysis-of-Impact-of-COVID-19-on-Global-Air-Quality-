import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

df_2019_q4 = pd.read_csv('data2019_Q4.csv', skiprows=4)
df_2020_q3 = pd.read_csv('data2020_Q3.csv', skiprows=4)


def clean_air_data(df):
    df = df[~df['Date'].astype(str).str.contains('#', na=False)]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    return df

df_2019_q4 = clean_air_data(df_2019_q4)
df_2020_q3 = clean_air_data(df_2020_q3)


# Combine 2020 data to represent "after COVID" period

df_post_covid = df_2020_q3
# Geting unique pollutant species names
pollutants = sorted(df_2019_q4['Specie'].unique())

# Store t-test results
results = []

pollutants = ['pm25', 'pm10','so2','no2','co','o3']

# Perform t-test for pm2.5 and pm10 pollutants
for pollutant in pollutants:
    # Perform t-test for each pollutant, excluding AQI

    # Get pre-COVID data for this pollutant
    pre_covid = df_2019_q4[df_2019_q4['Specie'] == pollutant]['median'].dropna()
    
    # Get during-COVID data for this pollutant
    post_covid = df_post_covid[df_post_covid['Specie'] == pollutant]['median'].dropna()
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(pre_covid, post_covid, equal_var=False)
    
    # Calculate means of medians
    pre_mean = pre_covid.mean()
    post_mean = post_covid.mean()
    percent_change = ((post_mean - pre_mean) / pre_mean) * 100
    
    # Store results
    results.append({
        'Pollutant': pollutant,
        'Pre-COVID Mean': round(pre_mean, 2),
        'Post-COVID Mean': round(post_mean, 2),
        'Percent Change': round(percent_change, 2),
        'p-value': round(p_value, 4),
        'Significant': p_value < 0.05
    })

# Convert results to DataFrame for easier display
results_df = pd.DataFrame(results)
print("T-Test Results:")
print(results_df)

# Plot the results for significant changes
significant_results = results_df[results_df['Significant']]

if not significant_results.empty:
    plt.figure(figsize=(10, 6))
    
    # Prepare data for plotting
    pollutants = significant_results['Pollutant']
    pre_means = significant_results['Pre-COVID Mean']
    post_means = significant_results['Post-COVID Mean']
    
    # Set up bar positions
    x = np.arange(len(pollutants))
    width = 0.35
    
    # Create bars
    plt.bar(x - width/2, pre_means, width, label='Pre-COVID (2019 Q4)')
    plt.bar(x + width/2, post_means, width, label='After COVID (2020 Q3)')
    
    # Add labels and title
    plt.xlabel('Pollutants')
    plt.ylabel('Median Concentration')
    plt.title('Significant Changes in Air Quality Due to COVID-19')
    plt.xticks(x, pollutants)
    plt.legend()
    
    # this code displays the arrow and amount of decrease percentage wise
    for i, pollutant in enumerate(pollutants):
        percent = significant_results[significant_results['Pollutant'] == pollutant]['Percent Change'].values[0]
        direction = "↓" if percent < 0 else "↑"
        plt.annotate(f"{abs(percent):.1f}% {direction}", 
                     xy=(i, max(pre_means[i], post_means[i]) + 1),
                     ha='center')
    
    plt.tight_layout()
    plt.show()
else:
    print("No statistically significant changes were found.")
