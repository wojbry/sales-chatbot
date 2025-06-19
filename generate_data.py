import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

# --- Configuration ---
NUM_PRODUCTS = 10
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2023, 12, 1) # Including December 2023
OUTPUT_FILENAME = 'monthly_retail_sales_data.csv'

# Define product characteristics for more varied data
product_configs = [
    {"name": "Basic T-Shirt", "base_sales": 10000, "sales_std_dev": 1500, "growth_rate_per_month": 0.005, "seasonality": {1:0.9, 2:0.9, 3:1.0, 4:1.05, 5:1.1, 6:1.1, 7:1.05, 8:1.0, 9:0.95, 10:0.95, 11:1.0, 12:1.05}}, # Slight summer bump
    {"name": "Wireless Headphones", "base_sales": 5000, "sales_std_dev": 800, "growth_rate_per_month": 0.015, "seasonality": {1:0.8, 2:0.8, 3:0.9, 4:0.9, 5:1.0, 6:1.0, 7:1.05, 8:1.1, 9:1.2, 10:1.3, 11:1.5, 12:1.8}}, # Strong Q4
    {"name": "Coffee Maker", "base_sales": 3000, "sales_std_dev": 500, "growth_rate_per_month": 0.002, "seasonality": {1:1.2, 2:1.0, 3:0.9, 4:0.9, 5:0.95, 6:1.0, 7:1.0, 8:1.05, 9:1.1, 10:1.15, 11:1.2, 12:1.3}}, # Holiday gifts
    {"name": "Running Shoes", "base_sales": 7000, "sales_std_dev": 1000, "growth_rate_per_month": 0.008, "seasonality": {1:1.0, 2:1.1, 3:1.2, 4:1.15, 5:1.0, 6:0.9, 7:0.9, 8:1.0, 9:1.1, 10:1.15, 11:1.05, 12:1.0}}, # Spring/Fall running season
    {"name": "Denim Jeans", "base_sales": 8000, "sales_std_dev": 1200, "growth_rate_per_month": 0.003, "seasonality": {1:0.9, 2:0.9, 3:1.0, 4:1.0, 5:1.0, 6:0.95, 7:1.05, 8:1.2, 9:1.15, 10:1.1, 11:1.0, 12:0.95}}, # Back-to-school peak
    {"name": "Cookware Set", "base_sales": 1500, "sales_std_dev": 300, "growth_rate_per_month": -0.001, "seasonality": {1:0.8, 2:0.8, 3:0.9, 4:1.0, 5:1.1, 6:1.0, 7:0.9, 8:0.9, 9:1.0, 10:1.1, 11:1.2, 12:1.5}}, # Wedding and holiday season
    {"name": "Smartwatch", "base_sales": 4000, "sales_std_dev": 700, "growth_rate_per_month": 0.02, "seasonality": {1:0.9, 2:0.9, 3:1.0, 4:1.0, 5:1.05, 6:1.05, 7:1.1, 8:1.1, 9:1.2, 10:1.4, 11:1.6, 12:2.0}}, # High growth, strong Q4
    {"name": "Novelty Mug", "base_sales": 2000, "sales_std_dev": 400, "growth_rate_per_month": -0.005, "seasonality": {1:0.7, 2:0.75, 3:0.8, 4:0.85, 5:0.9, 6:0.95, 7:0.9, 8:0.85, 9:0.9, 10:1.0, 11:1.5, 12:2.5}}, # Huge Q4 spike for gifts
    {"name": "Camping Tent", "base_sales": 1000, "sales_std_dev": 200, "growth_rate_per_month": 0.001, "seasonality": {1:0.5, 2:0.6, 3:0.8, 4:1.2, 5:1.5, 6:1.8, 7:1.7, 8:1.3, 9:0.9, 10:0.7, 11:0.6, 12:0.5}}, # Peak in summer
    {"name": "Weighted Blanket", "base_sales": 2500, "sales_std_dev": 400, "growth_rate_per_month": -0.01, "seasonality": {1:1.8, 2:1.5, 3:1.0, 4:0.8, 5:0.7, 6:0.6, 7:0.6, 8:0.7, 9:0.8, 10:1.0, 11:1.3, 12:2.0}}, # Strong winter seasonality, declining overall
]

all_sales_data = []

current_date = START_DATE
month_index = 0 # To track overall month progression for growth rate

while current_date <= END_DATE:
    for i, config in enumerate(product_configs):
        product_id = f"P{i+1:02d}" # P01, P02, etc.
        product_name = config["name"]

        # Calculate base sales for the current month
        base_sales = config["base_sales"]

        # Apply overall growth/decline trend
        trend_factor = 1 + (config["growth_rate_per_month"] * month_index)
        trend_sales = base_sales * trend_factor

        # Apply seasonality based on month
        month = current_date.month
        seasonality_factor = config["seasonality"].get(month, 1.0) # Default to 1.0 if month not specified
        seasonal_sales = trend_sales * seasonality_factor

        # Add some random noise
        random_noise = random.normalvariate(1, config["sales_std_dev"] / base_sales) # ~10-20% std dev
        daily_sales = seasonal_sales * max(0.8, random_noise) # Ensure sales don't go too low

        # Ensure sales are non-negative
        daily_sales = max(0, round(daily_sales))

        all_sales_data.append({
            "Date": current_date.strftime("%Y-%m-%d"), # YYYY-MM-DD format
            "ProductId": product_id,
            "ProductName": product_name,
            "SalesRevenue": daily_sales
        })
    current_date += relativedelta(months=1)
    month_index += 1

# Create a Pandas DataFrame
df = pd.DataFrame(all_sales_data)

# Sort by Date and ProductId for better readability
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Date', 'ProductId']).reset_index(drop=True)

# Save to CSV
df.to_csv(OUTPUT_FILENAME, index=False)

print(f"Generated {len(df)} rows of data and saved to {OUTPUT_FILENAME}")
print("\nFirst 5 rows:")
print(df.head())
print(f"\nLast 5 rows:")
print(df.tail())