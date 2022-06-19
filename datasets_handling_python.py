# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#Import pandas to 
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

##Question 1: Load and Merge Datasets
speeches = pd.read_csv('speeches.csv', sep='|', skiprows=21)
speeches = speeches.rename(columns={'</div>date':'date'})
speeches = speeches[['date', 'contents']]
speeches = speeches.groupby("date")['contents'].apply(lambda x: " ".join(x.astype(str))).reset_index()
fx = pd.read_csv('fx.csv')[['Date', 'USD']]
fx = fx.rename(columns={'Date':'date'})
joined_df = speeches.merge(fx, how = 'outer', on = 'date')
joined_df['date'] = pd.to_datetime(joined_df['date'])
joined_df.set_index('date', inplace=True)
joined_df.sort_index(inplace=True)

##Question2: Remove entries of outliers and mistakes
#view if any outliers in the charting of date against USD
joined_df.describe()
joined_df.plot()
#From plots there is no obvious outliers or mistakes to be taken out.

#Question 3: handling missing exchange rate
##Since Euro is not rolled out before 1 Jan 1999, Thus the ECB speeches before that can be omited.
joined_df = joined_df['1999-01-01':'2099-12-31']
#Fill the USD value by the last exchange rate
joined_df["USD"] = joined_df["USD"].fillna(method = 'ffill')
##Remove any dates without speeches
joined_df = joined_df[~joined_df["contents"].isnull()]

#Question 4: Calculate exchange rate of return
joined_df['percentage'] = joined_df['USD'].pct_change() *100
joined_df['good_news'] = joined_df['percentage'].apply(lambda x: 1 if x > 0.5 else 0)
joined_df['bad_news'] = joined_df['percentage'].apply(lambda x: 1 if x <-0.5 else 0)


#Question 5: Concatenate all good news text
def bag_of_words(df, column, filename):
    shortlist = df[df[column] == True]['contents'].tolist()
    vectorizer = CountVectorizer(stop_words = 'english')
    words = vectorizer.fit_transform(shortlist)
    counts = pd.DataFrame(words.toarray()).sum(axis=0).tolist()
    output = pd.DataFrame([vectorizer.get_feature_names(), counts], index = ["word", "count"]).transpose().sort_values(by=["count", "word"], ascending = [False, True])
    output.to_csv(filename, index=False)
    
bag_of_words(joined_df, 'good_news', 'good_indicators_python.csv')
bag_of_words(joined_df, 'bad_news', 'bad_indicators_python.csv')
