# -*- coding: utf-8 -*-
"""""""""""""""""""""""""""""""""""""""""
Date: December 8, 2022                  " 
Author: Hiru Rodrigo                    " 
Subject: Empirical Test                 "
"""""""""""""""""""""""""""""""""""""""""
#################################################################### Code outline #########################################################################
#Library imports 
#Question 1: Compound Returns
#Question 2: 2-day Returns
#Question 3: Plot the coefficients
#Question 4: Interpretations


###################################################################### Library imports ####################################################################
import pandas as pd 
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

############################################################# Question 1: Compound Returns ##############################################################
#Read in data
url = (r'https://github.com/bocrodh/Work-Sample/blob/main/raw_data/49_Industry_Portfolios_Daily.csv?raw=true') 
df = pd.read_csv(url, header=5, usecols = [0,45]).iloc[5:].reset_index()

#Format data headers and date column
df.columns = ["index","date","bank"]
df = df[["date","bank"]]
df = df.dropna()
df["date"] = df["date"].apply(pd.to_datetime)
df["bank"] = df['bank'].astype(float)

#Subset data
df = df[(df['date'] >= '1994-1-3') & (df['date'] <= '2007-6-29')]

#Compute returns
df['return'] = np.log1p(df['bank'])

#Retrieving industry returns with market returns
industry = (r'https://github.com/bocrodh/Work-Sample/blob/main/raw_data/49_Industry_Portfolios_Daily.csv?raw=true') 
industry = pd.read_csv(industry, header=5).iloc[5:]

market = (r'https://github.com/bocrodh/Work-Sample/blob/main/raw_data/F-F_Research_Data_Factors_daily.csv?raw=true') 
market = pd.read_csv(market, header=3, usecols = [0,1]).iloc[3:]

#Format data headers and date column
industry = industry.dropna()
market = market.dropna()

#Merge industry and market data
merged = pd.merge(industry, market, on='Unnamed: 0') 
merged.rename(columns={ merged.columns[0]: "date" }, inplace = True)

#Retrieving shock and suprise data
crisis = (r'https://github.com/bocrodh/Work-Sample/blob/main/raw_data/daily_FF_surprises_July_2008.xls?raw=true') 
crisis = pd.read_excel(crisis, header=0)

replication = (r'https://github.com/bocrodh/Work-Sample/blob/main/raw_data/replication_dataset_gw.xlsx?raw=true') 
replication = pd.read_excel(replication,"Sheet2", header=0)

#Format data headers and date column
crisis = crisis.dropna() 
crisis.rename(columns={ crisis.columns[0]: "date" }, inplace = True) 

replication = market.dropna()
replication.rename(columns={ replication.columns[0]: "date" }, inplace = True)

merged["date"] = merged["date"].apply(pd.to_datetime)
crisis["date"] = crisis["date"].apply(pd.to_datetime)
replication["date"] = replication["date"].apply(pd.to_datetime)

#Merge industry, market, crisis, and replication data
dataset = merged.merge(crisis,on='date', how='outer').merge(replication,on='date', how='outer')
dataset = dataset.iloc[:, :-1] #Dropping last column because it is duplicated with another column

#Subset the entire dataframe for specific dates
dataset = dataset[(dataset['date'] >= '1994-1-3') & (dataset['date'] <= '2007-6-29')]
############################################################# Question 2: Two-Day Returns ##############################################################

#Computing 2-day returns  
returns = dataset.iloc[:, 1:51].apply(pd.to_numeric, errors='coerce', axis=1).apply(np.log)
returns_all = pd.concat([dataset[["date","Scheduled FOMC meeting"]],returns], axis=1)
    
#Substetting for FOMC and next day
returns_all['next_day_flag'] = returns_all['Scheduled FOMC meeting'].fillna(0).shift(1)   
returns_all["2_dayflag"] = returns_all["Scheduled FOMC meeting"].fillna(0) + returns_all["next_day_flag"]
returns_all = returns_all.loc[returns_all["2_dayflag"]>0]

#Computing mean
returns_all["Banks"].mean() #ANSWER:  -0.5669347194554428

############################################################# Question 3: Plot the Coefficients ##############################################################

#Merging tight suprise and returns_all
coefficients = returns_all.merge(dataset[["date","Surprise"]],on='date').fillna(0)

coefficients.drop(['date', 'Scheduled FOMC meeting','next_day_flag','2_dayflag'], axis=1, inplace=True)

coefficients_results = []

for column in coefficients:
    nonzero = coefficients.loc[coefficients[column]>0] 
    df = nonzero[[column, "Surprise"]]
    result = sm.OLS(df[column],df['Surprise']).fit()
    coefficients_results.append(result.params) 

coeff = pd.DataFrame([coefficients_results])
coeff =coeff.T.reset_index().replace("dty","").replace("_X","") 
coeff.columns = ["index","coeff"]
coeff = coeff[["coeff"]]
coeff_final = coeff.replace("dty","").replace("_X","").replace("dtype:","").replace("float64","")
#Saved on desktop, did splt to columns, then uploaded to Github

coeff_final.to_csv("Desktop/coeff2.csv")

#Plotting
df = pd.read_csv("https://github.com/bocrodh/Work-Sample/blob/main/raw_data/coeff.csv?raw=true", header=0) 

df = df[['industry','coeff']]
df_plot = df.sort_values(by=['coeff'], ascending=True) #The sorted dataframe is reflected in the plot

fig, ax = plt.subplots()

ax.bar(df_plot['industry'], df_plot['coeff'])[22].set_color('r')

ax.set_ylabel('OLS Coefficient')
ax.set_title('Coefficient Plots')
plt.xticks(rotation=90, size=10) 
plt.grid()

plt.show()
############################################################# Question 4: Interpretation ##############################################################

#Answer: The plotted coefficients illustrate that only 7 out of 49 industries have a positive response to the surprise. More specifically, a 1 unit change
#in surprise leads has a positive impact on wholesale, food products, utilities, restaurants and hotels, coals, candy and soda, and beer and liqduor. 
#Many of these industries are consumption goods. 

#Answer: A 1 unit increase in the suprise leads to a ~-2% in 2-day returns, all other factors remaining constant.   