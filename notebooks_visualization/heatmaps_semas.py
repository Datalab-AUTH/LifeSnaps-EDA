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
# # What time do the users answer more?

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
from pymongo import MongoClient
import json
from bson import ObjectId
from pprint import pprint
import streamlit as st
import ast

# %%
cmap = ["#7570b3", "#1d84c6", "#0095bf", "#00a0a1", "#00a676", "#3da95b", "#63aa3a", 
          "#88a906", "#a0ab00", "#b7ac00", "#cfac00", "#e6ab01"]

#sns.set_palette(sns.color_palette(cmap))

# %%
sns.set_context("paper", rc={"font.size":30,"axes.titlesize":30,"axes.labelsize":30})  
sns.set(font_scale=3.5)
plt.rcParams['xtick.major.size'] = 4
plt.rcParams['xtick.major.width'] = 4
plt.rcParams['xtick.bottom'] = True
plt.rcParams['ytick.left'] = True
sns.set_style('ticks')

# %%
with open('../credentials.json') as f:
    data = json.load(f)
    username = data['username']
    password = data['password']

# %%
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))
db = client.rais1_anon

# %%
collection = db.sema
df = pd.DataFrame(list(collection.find()))
#df.head()

# %%
# Deleting the no-responses and nones
df=pd.DataFrame(list(collection.find( { '$and': [ {"data.MOOD": { "$ne": "<no-response>" }},{"data.MOOD": { "$ne": None }}, {"data.PLACE": { "$ne": "<no-response>" }},{"data.PLACE": { "$ne": None }} ] } )))

# %%
df=df[['user_id']].join(pd.DataFrame(df['data'].tolist(), index=df.index).add_prefix('data.'))
df.head()

# %%
df['Dates'] = pd.to_datetime(df['data.COMPLETED_TS'])
users=df['user_id']
days=df['Dates']
place=df['data.PLACE']
#mood=df['data.MOOD']
df = pd.concat([users, days, place],axis=1)
df = df.sort_values(by='Dates', ascending=True)
df['Dates'] = pd.to_datetime(df['Dates'].astype("str"), format='%Y-%m-%d')
df['Dates']=df['Dates'].dt.round('60min') 
#df
# Converting date to day of the week
df['DayName'] = pd.Series(df['Dates'].dt.day_name(), index=df.index) 
df

# %%
# Days of the week in ascending order
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#df

# %%
# Separating the Rounds
df1 = df[(df['Dates'] >= "2021-05-24") & (df['Dates'] <= "2021-07-26")] #Round1
df2 = df[(df['Dates'] >= "2021-11-15") & (df['Dates'] <= "2022-01-17")] #Round2
#df1

# %% [markdown]
# # Round1

# %%
# Splitting timestamp column into two separate date and time columns
df1['date']= pd.to_datetime(df1['Dates']).dt.date
df1['time']= pd.to_datetime(df1['Dates']).dt.time
days=df1['date']
hours=df1['time']
dayNames=df1['DayName']
users=df1['user_id']
place=df1['data.PLACE']
df1=pd.concat([days,hours, users, place,dayNames],axis=1)
#df1

df1['distinct_counts'] = df1.groupby(['date','time'])['user_id'].transform('nunique')

day=df1['DayName']
time=df1['time']
NumberOfAnswers=df1['distinct_counts']
df1 = df1.sort_values('DayName')
df1=pd.concat([day,time,NumberOfAnswers],axis=1)
df1.DayName = pd.Categorical(df1.DayName,categories=weekdays)

piv1 = pd.pivot_table(df1, values='distinct_counts',index=["time"], columns=["DayName"], fill_value=0)

# %% [markdown]
# # Round2

# %%
# Splitting timestamp column into two separate date and time columns
df2['date']= pd.to_datetime(df2['Dates']).dt.date
df2['time']= pd.to_datetime(df2['Dates']).dt.time
days=df2['date']
hours=df2['time']
dayNames=df2['DayName']
users=df2['user_id']
place=df2['data.PLACE']
df2=pd.concat([days,hours, users, place,dayNames],axis=1)
#df2

df2['distinct_counts'] = df2.groupby(['date','time'])['user_id'].transform('nunique')

day=df2['DayName']
time=df2['time']
NumberOfAnswers=df2['distinct_counts']
df2 = df2.sort_values('DayName')
df2=pd.concat([day,time,NumberOfAnswers],axis=1)
df2.DayName = pd.Categorical(df2.DayName,categories=weekdays)

piv2 = pd.pivot_table(df2, values='distinct_counts',index=["time"], columns=["DayName"], fill_value=0)

# %% [markdown]
# # Both Rounds

# %%
df=df1.append(df2)

# %%
piv = pd.pivot_table(df, values='distinct_counts',index=["time"], columns=["DayName"], fill_value=0)

# %%
fig, ax = plt.subplots(figsize = (20,15))
sns.heatmap(piv, cmap=cmap)
plt.tight_layout()
ax.set_rasterization_zorder(0)
#plt.xticks(size = 15)
#plt.yticks(size = 15)
plt.xlabel('')
plt.ylabel('Time of the day', fontsize=45)
plt.title('Temporal change in behavior: Rounds-1 and -2', fontsize=45)
plt.text(8, 15, 'Total number of Context and Mood \n sema surveys answered for all users', rotation=270, fontsize=35)
plt.show()

# %% [markdown]
# Timezone issues fixed
