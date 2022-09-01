# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # When and how much have our participants walked?

# %%
typee='steps'

# %%
import matplotlib.pyplot as plt
import numpy as np
import pickle
import seaborn as sns
import pandas as pd
from datetime import datetime
import matplotlib.ticker as mticker
import matplotlib.dates as md
import datetime

# %%
cmap = ["#7570b3", "#1d84c6", "#0095bf", "#00a0a1", "#00a676", "#3da95b", "#63aa3a", 
          "#88a906", "#a0ab00", "#b7ac00", "#cfac00", "#e6ab01"]

sns.set_palette(sns.color_palette(cmap))

# %%
# Loading the data
infile = open('../data/users_%s_hourly'%typee,'rb')
typee_hourly = pickle.load(infile)
infile.close()

typee_hourly # year-month-day e.g. 2021-05-24

# %%
typee_hourly.reset_index(inplace=True)

# Preprocessing 
typee_hourly['date'] = pd.to_datetime(typee_hourly.date, format='%m/%d/%y %H:%M:%S') 
typee_hourly[typee] = pd.to_numeric(typee_hourly[typee])
typee_hourly = typee_hourly.astype({"id": str})
typee_hourly = typee_hourly.sort_values('date')
#typee_hourly

# %%
typee_hourly=typee_hourly.resample('H', on='date').mean()
typee_hourly.reset_index(inplace=True)
#typee_hourly

# %%
# Splitting timestamp column into two separate date and time columns
typee_hourly['Dates'] = pd.to_datetime(typee_hourly['date']).dt.date
typee_hourly['Time'] = pd.to_datetime(typee_hourly['date']).dt.time
#typee_hourly

# %%
# Converting date to day of the week
typee_hourly['DayName'] = pd.Series(typee_hourly['date'].dt.day_name(), index=typee_hourly.index) 
# Days of the week in ascending order
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# Seperating the two rounds
typee_hourly['Dates'] = pd.to_datetime(typee_hourly.Dates, format='%Y/%m/%d') 
df1 = typee_hourly[(typee_hourly['Dates'] >= "2021-05-24") & (typee_hourly['Dates'] <= "2021-07-26")] #Round1
df2 = typee_hourly[(typee_hourly['Dates'] >= "2021-11-15") & (typee_hourly['Dates'] <= "2022-01-17")] #Round2
# Both rounds
df=df1.append(df2)
df.DayName = pd.Categorical(df.DayName,categories=weekdays)
df = df.sort_values('DayName')
# Rearranging the dataframe for the heatmap
df['Time'] = pd.to_datetime(df['date']).dt.time
days=df['DayName']
hours=df['Time']
freq=df[typee]
df=pd.concat([days,hours,freq],axis=1)
piv = pd.pivot_table(df, values=typee,index=["Time"], columns=["DayName"], fill_value=0)

# %%
fig, ax = plt.subplots(figsize = (15,8))
sns.heatmap(piv, cmap=cmap)
plt.tight_layout()
ax.yaxis.set_major_locator(md.HourLocator(interval = 100))
ax.yaxis.set_major_formatter(md.DateFormatter('%H:%M:%S'))
plt.xticks(size = 20)
plt.yticks(size = 20)
plt.xlabel('',size=30)
#plt.rcParams["font.weight"] = "bold"
#plt.rcParams["axes.labelweight"] = "bold"
plt.ylabel('Time of the day',fontsize=40)
plt.title('Average change in behavior: Rounds -1 and -2',fontsize=30)
plt.text(8, 18, 'Average %s for all users'%typee, fontsize=20, rotation=270)
plt.show()

# %% [markdown]
# # Exercise - When do people exercise more? 

# %%
# Loading the data
infile = open('../data/users_exercise_hourly','rb')
df = pickle.load(infile)
infile.close()

df.head()

# %%
df_new = df.copy()
df1 = df_new[(df_new['date'] >= "2021-05-24") & (df_new['date'] <= "2021-07-26")] #Round1
df2 = df_new[(df_new['date'] >= "2021-11-15") & (df_new['date'] <= "2022-01-17")] #Round2

df=df1.append(df2)
# %%
df.shape[0]
# %%
#df.reset_index(inplace=True)
# Preprocessing 
df['dateTime'] = pd.to_datetime(df.date, format='%m/%d/%y %H:%M:%S')
df['duration'] = pd.to_numeric(df['duration'])
df = df.astype({"id": str})
df['date'] = df['dateTime'].dt.date
df['hour'] = df['dateTime'].dt.hour
df['day'] = df["dateTime"].dt.day_name()
df
# %%
exercise_counts = df.groupby(['day', 'hour'])['activityType'].count()
exercise_counts
# %%
exercise_counts.hist()
# %%
exercise_counts = exercise_counts.reset_index(drop=False)
exercise_counts
# %%
# Rearranging the dataframe for the heatmap
days = exercise_counts['day']
hours = exercise_counts['hour']
freq = exercise_counts['activityType']
df = pd.concat([days, hours, freq], axis=1)

exercise_counts.day = pd.Categorical(exercise_counts.day,categories=weekdays)
exercise_counts = exercise_counts.sort_values('day')

piv = pd.pivot_table(exercise_counts, values='activityType', index=["hour"], columns=["day"], fill_value=0)

# %%
fig, ax = plt.subplots(figsize=(15, 8))
sns.heatmap(piv, cmap=cmap)
plt.tight_layout()
ax.yaxis.set_major_locator(md.HourLocator(interval=100))
ax.yaxis.set_major_formatter(md.DateFormatter('%H:%M:%S'))
plt.text(8, 19, 'Number of exercise sessions', fontsize=20, rotation=270)
plt.xticks(size=20)
plt.yticks(size=20, rotation=360)
plt.xlabel('', size=30)
plt.ylabel('Time of the day', fontsize=30)
plt.title('Temporal change in behavior: Rounds -1 and -2', fontsize=30)
plt.show()
