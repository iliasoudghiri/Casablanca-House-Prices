#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 13:33:12 2021

@author: Ilyas
"""
import pandas as pd 
import numpy as np

df = pd.read_csv('mubawab_listings.csv',dtype = object )

#clean type column to keep only the first word
df['Type'] = df['Type'].apply(lambda x: str(x).split(' ')[0])

#clean localisation to get the neighbourhood
df['Localisation'] = df['Localisation'].apply(lambda x: x.split('à')[0])

#remove rows with missing price and clean price (remove DH and change type)
df = df.dropna(subset = ['Price']).reset_index(drop=True)
df['Price'] = df.Price.str.replace(r'\D+','')
df['Price'] = df.Price.astype('int')

#convert tags from string to list
df['Tags'] = df.Tags.apply(eval)
#df['Tags'] = df.Tags.apply(lambda x: x.replace("'","").strip("][").split(", "))

#extract area, rooms, bedrooms and bathrooms from tags

for i in range(len(df)):
    tags = df.loc[i,'Tags']
    to_pop = []
    for t in range(len(tags)):
        if "m²" in tags[t]:
            df.loc[i,'Area'] = tags[t]
            to_pop.append(t)

        if "Pièces" in tags[t] or "Pièce" in tags[t]:
            df.loc[i,'Rooms'] = tags[t]
            to_pop.append(t)
        if "Chambres" in tags[t] or "Chambre" in tags[t]:
            df.loc[i,'Bedrooms'] = tags[t]
            to_pop.append(t)
        if "Salles de bains" in tags[t] or "Salle de bain" in tags[t]:

            df.loc[i,'Bathrooms'] = tags[t]
            to_pop.append(t)
        if "étage" in tags[t]:
            df.loc[i,'Floor'] = tags[t]
            to_pop.append(t)

    Other_tags = list([tags[k] for k in range(len(tags)) if k not in to_pop])
    df.loc[i,'Other_tags'] = str(Other_tags)
    
#clean area, rooms, bedrooms, bathrooms and floor columns
df['Area'] = df['Area'].str.replace(r'\D+','').astype('float')
df['Rooms'] = df['Rooms'].str.replace(r'\D+','').astype('float')
df['Bedrooms'] = df['Bedrooms'].str.replace(r'\D+','').astype('float')
df['Bathrooms'] = df['Bathrooms'].str.replace(r'\D+','').astype('float')
df['Floor'] = df['Floor'].str.replace(r'\D+','').astype('float')

#Drop Tags collumn as it has been extracted to other columns
df = df.drop(['Tags'],axis=1).reset_index(drop = True)

#set nan values to np.nan
df = df.replace('nan',np.nan)

#Fill the listings with missing type from title
missing_type = df['Type'].isna()[df['Type'].isna()].index

for idx in missing_type:
    if df.loc[idx,'Title'].lower().find('appartement') != -1:
        df.loc[idx,'Type'] = 'Appartements' 
    if df.loc[idx,'Title'].lower().find('villa') != -1:
        df.loc[idx,'Type'] = 'Villas' 
    if df.loc[idx,'Title'].lower().find('maison') != -1:
        df.loc[idx,'Type'] = 'Maisons' 
    if df.loc[idx,'Title'].lower().find('riad') != -1:
        df.loc[idx,'Type'] = 'Riad' 

#Drop listings with missing type for which title didn't contain type either
df = df.dropna(subset = ['Type']).reset_index(drop = True)


#Check and drop duplicates
df.duplicated(subset = ['Type', 'Area', 'Price', 'Localisation']).sum()
df = df.drop_duplicates(subset = ['Type', 'Area', 'Price', 'Localisation']).reset_index(drop= True)

#Remove space after neighbourhoods
df['Localisation'] = df.Localisation.str.strip()

#Set value of floor to 0 for Villas, Riads and Houses
df.loc[df[df['Type' ]!= 'Appartements'].index ,'Floor'] = 0

#Drop title as we can't be sure about objectivity of informations
df = df.drop(['Title'],axis=1)

#Add Price_m2 column
df['Price_m2'] = df['Price']/df['Area']


#Save df to csv file for further analysis and preprocessing
df.to_csv('mubawab_listings_clean.csv',index=False)
