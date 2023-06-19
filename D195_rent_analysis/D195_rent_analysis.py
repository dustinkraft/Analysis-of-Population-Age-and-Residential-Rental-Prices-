import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.stats
import statistics
import seaborn as sns
sns.set_style('darkgrid')

# ---------------------------------------------------------------------------------------
# Import and prepare data

# read in the 3 csv files
df1 = pd.read_csv('population.csv', header=0)
df2 = pd.read_csv('rent.csv', header=0)
df3 = pd.read_csv('income.csv', header=0)

# join population and rent dataframes on PK
df4 = pd.merge(df1, df2, on=['id', 'geo_name'], how='outer')

# join df4 and income dataframe on PK
df5 = pd.merge(df4, df3, on=['id', 'geo_name'], how='outer')

# Handle 0-values in estimates
df5['est_perc_pop_20_to_24'].replace(0, 1, inplace=True)
df5['est_perc_pop_25_to_29'].replace(0, 1, inplace=True)
df5['est_perc_pop_30_to_34'].replace(0, 1, inplace=True)
df5['est_median_rent'].replace(0, 1, inplace=True)
df5['est_median_household_income'].replace(0, 1, inplace=True)

# calculate an error %; if margin of error is 0, enter "0"
df5["error_20_to_24"] = np.where(df5['moe_perc_pop_20_to_24'] != 0, (df5['moe_perc_pop_20_to_24'] / df5['est_perc_pop_20_to_24']), 0)
df5["error_25_to_29"] = np.where(df5['moe_perc_pop_25_to_29'] != 0, (df5['moe_perc_pop_25_to_29'] / df5['est_perc_pop_25_to_29']), 0)
df5["error_30_to_34"] = np.where(df5['moe_perc_pop_30_to_34'] != 0, (df5['moe_perc_pop_30_to_34'] / df5['est_perc_pop_30_to_34']), 0)
df5["error_rent"] = np.where(df5['moe_median_rent'] != 0, (df5['moe_median_rent'] / df5['est_median_rent']), 0)
df5["error_home_value"] = np.where(df5['moe_median_household_income'] != 0, (df5['moe_median_household_income'] / df5['est_median_household_income']), 0)

# combine data from to different age brackets to get pop between 20 and 34
df5["est_perc_pop_20_to_34"] = df5['est_perc_pop_20_to_24'] + df5['est_perc_pop_25_to_29'] + df5['est_perc_pop_30_to_34']

# create new column and populate with ratio of median rent to median income by ZCTA
df5["rent_to_income_ratio"] = ((df5['est_median_rent'] * 12) / df5['est_median_household_income']) * 100

# Export full dataset for deliverable
df5.to_csv('full_dataset.csv', index=False)

# ---------------------------------------------------------------------------------------
# Analysis

# Limit to records below max error %
error_limit = .25
df5 = df5.loc[df5["error_20_to_24"] < error_limit]
df5 = df5.loc[df5["error_25_to_29"] < error_limit]
df5 = df5.loc[df5["error_30_to_34"] < error_limit]
df5 = df5.loc[df5["error_rent"] < error_limit]
df5 = df5.loc[df5["error_home_value"] < error_limit]

# extract 2 attributes and PK for bivariate analysis
df6 = df5[["geo_name", "rent_to_income_ratio", "est_perc_pop_20_to_34"]].copy()

# remove outliers; limit ratios to 50%
df6 = df6.loc[df6["rent_to_income_ratio"] < 50]
df6 = df6.loc[df6["est_perc_pop_20_to_34"] > 0]

# drop the records that contain Null values
df6 = df6.dropna()

# break the 2 attributes in to 2 arrays
x = df6['est_perc_pop_20_to_34'].to_numpy(dtype=float)
y = df6['rent_to_income_ratio'].to_numpy(dtype=float)

# Histogram for x
plt.figure()
x_plot = sns.histplot(x, kde=True)
plt.xlabel('% aged 20 to 34')
plt.ylabel('Frequency')

# Statistics for x
print('Descriptive Stats for % aged 20 to 34 (X):')
print('Mean of X: ' + str(statistics.fmean(x)))
print('Median of X: ' + str(statistics.median(x)))
print('Mode of X: ' + str(statistics.mode(x)))
print('Variance of X: ' + str(statistics.variance(x)))
print('Standard Deviation of X: ' + str(statistics.stdev(x)))
print(' ')

# Histogram for y
plt.figure()
y_plot = sns.histplot(y, kde=True)
plt.xlabel('Rent-to-Income %')
plt.ylabel('Frequency')

# Statistics for y
print('Descriptive Stats for Rent-to-Income Ratio (Y):')
print('Mean of Y: ' + str(statistics.fmean(y)))
print('Median of Y: ' + str(statistics.median(y)))
print('Mode of Y: ' + str(statistics.mode(y)))
print('Variance of Y: ' + str(statistics.variance(y)))
print('Standard Deviation of Y: ' + str(statistics.stdev(y)))
print(' ')
# ---------------------------------------------------------------------------------------
# Create regression

slope, intercept, r, p, stderr = scipy.stats.linregress(x, y, alternative='greater')

line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}'
fig, ax = plt.subplots()
ax.plot(x, y, linewidth=0, marker='.', label='Data points')
ax.plot(x, intercept + slope * x, label=line)
ax.set_xlabel('% aged 20 to 34')
ax.set_ylabel('Rent-to-income %')
ax.legend(facecolor='white')
plt.show()

print('Regression Analysis:')
print("slope: ", slope)
print("intercept: ", intercept)
print("r: ", r)
print("p-value: ", p)
