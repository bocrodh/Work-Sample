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
import statsmodels.formula.api as smf

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
returns_all["Banks"].mean()

############################################################# Question 3: Plot the Coefficients ##############################################################

#Merging tight suprise and returns_all
coefficients = returns_all.merge(dataset[["date","Surprise"]],on='date').fillna(0)

coefficients.drop(['date', 'Scheduled FOMC meeting','next_day_flag','2_dayflag'], axis=1, inplace=True)

for column in coefficients:
    nonzero = coefficients.loc[coefficients[column]>0] 
    df = nonzero[[column, "Surprise"]]
    model = sm.OLS(df[column], df["Surprise"]).fit()

#Did not get a chance to complete the loop

############################################################# Question 4: Interpretation ##############################################################

#Out of the 49 industries, only 7 industries returns increase when there is a 1 unit change in the suprise. Interestingly, they are all inferior goods. 
#A 1 unit increase in the tight surpise leads to a ~-3.0% change in the 2=day returns