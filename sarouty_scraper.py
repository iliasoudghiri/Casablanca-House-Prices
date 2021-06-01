#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:53:06 2021

@author: Ilyas
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def get_listings(n_page=10):
    '''
    Returns property data of properties listed on the sarouty website
    
    params:
        n_page (int): number of pages to scrape as an integer, defaults to 10
    
    returns:
        listings_df (DataFrame): dataframe of all listings scraped columns included are title, price,
                                    location, type, number of bedrooms, number of bathroom and area
    '''
    
    #check if n_page is an integer
    if not isinstance(n_page,int):
        raise TypeError("'n_page' must be an integer")
    
    #create a matrix to store the values
    data = []

    #iterate over the first n_page pages of the website
    for i in range(1,n_page+1):
        
        #get() request
        response = requests.get('https://www.sarouty.ma/fr/recherche?c=1&ob=mr&page='+str(i))
        
        #store the webpage content
        webpage = response.content
        
        #create beatiful soup object
        soup = BeautifulSoup(webpage,'html.parser')
        
        for item in soup.find_all('div',class_='card__content'):
            
            #create an empty list to store the card's informations
            lst = []
            
            #scrape the informations and add the to the list
            try:
                title = item.find('h2',class_="card__title card__title-link").text.strip()
            except:
                title = np.nan        
            lst.append(title)
            try:    
                price = item.find('span',class_='card__price-value').text.strip().replace('\n','').replace('   ','')
            except:
                price = np.nan
            lst.append(price)
            try:    
                location = item.find('span',class_='card__location-text').text.strip()
            except:
                location = np.nan
            lst.append(location)
            try:
                prop_type = item.find('p',class_="card__property-amenity card__property-amenity--property-type").text.strip()
            except:
                prop_type = np.nan
            lst.append(prop_type)
            try:
                nbed = item.find('p',class_="card__property-amenity card__property-amenity--bedrooms").text.strip()
            except:
                nbed = np.nan
            lst.append(nbed)
            try:    
                nbath = item.find('p',class_="card__property-amenity card__property-amenity--bathrooms").text.strip()
            except:
                nbath = np.nan    
            lst.append(nbath)
            try:    
                area = item.find('p',class_="card__property-amenity card__property-amenity--area").text.strip()
            except:
                area = np.nan          
            lst.append(area)
            
            #add the list to the data matrix
            data.append(lst)
    
    cols = ['title','price','location','type','bedrooms','bathrooms','area']
    listings_df= pd.DataFrame(data,columns=cols)
    return listings_df