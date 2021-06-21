#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 09:40:06 2021

@author: Ilyas
"""
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import numpy as np
import pandas as pd

'''
This script scrapes the mubawab website starting from page 1 of the all 
properties for sale in Casablanca page. 
'''


def on_listings_page(browser):
    '''
    check if the browser is on a page with property listings on the mubawab website
    '''
    try:
        browser.find_element_by_xpath('/html/body/section/div[2]/div[1]/div[2]/i')
        return True
    except NoSuchElementException:
        return False

def get_listing(browser,n=0):
    '''
    This function gets the info of the n'th listing on the listings page and goes back to that page
    '''
    listing = browser.find_element_by_xpath(f"//li[@class='listingBox w100'][{n+1}]")
    listing.click()
    try:
        type_ = browser.find_element_by_xpath('/html/body/section/div[1]/div/div[1]/a[3]').text
    except:
        type_ = np.nan
    try:
        title = browser.find_element_by_xpath('/html/body/section/div[2]/div/div[1]/h1').text
    except:
        title = np.nan
    try:
        loca = browser.find_element_by_xpath('/html/body/section/div[2]/div/div[1]/h3').text
    except:
        loca = np.nan
    try:
        map_click = browser.find_element_by_xpath('/html/body/section/div[2]/div/div[8]/div[1]/div/a')
        map_click.click()
        coord = browser.find_element_by_xpath('/html/body/section/div[2]/div/div[8]/div[2]')
        lat = coord.get_attribute("lat")
        lon = coord.get_attribute("lon")
    except:
        lat = np.nan
        lon = np.nan
    try:
        price = browser.find_element_by_xpath('/html/body/section/div[2]/div/div[1]/div[1]/div[1]/h3').text
    except:
        price = np.nan
    try:
        tags = browser.find_elements_by_xpath('/html/body/section/div[2]/div/div[1]/div[2]/span')
    except:
        tags = np.nan
    try:
        other_tags = [tag.text for tag in tags]
    except:
        other_tags = np.nan
    ls = [type_,loca,lat,lon,title,price,other_tags]
    browser.back()
    return ls

def get_city_lisitings_pages(browser,n_pages=500):
    
    #make the request to desired url
    url = 'https://www.mubawab.ma/fr/ct/casablanca/immobilier-a-vendre'
    browser.get(url)
    
    #initialize empty array to store all the different listings
    listings_info = []
    last_page = False
    i=1 #page counter
    
    while i <n_pages+1 and (not last_page):
        n_listings = len(browser.find_elements_by_xpath("//li[@class='listingBox w100']"))
        print(f'    should get {n_listings} listings from page {i}') #for debugging
        for n in range(n_listings):
            ls = get_listing(browser,n=n)
            listings_info.append(ls)
            
        #go to next page if not on last page
        try:
            arrows = browser.find_elements_by_class_name('arrowDot')
            arrows[1].click()  
            i+=1 #for debugging
        #if on last page stop 
        except : #ElementClickInterceptedException removed
            last_page = True
    df = pd.DataFrame(listings_info)
    df.columns = ['Type','Localisation','Latitude','Longitude','Title','Price','Tags']
    return df


#adding the incognito argument to webdriver
option = webdriver.ChromeOptions()
option.add_argument(" --incognito")
option.add_argument('--headless')
#option.add_argument('--no-sandbox')
#option.add_argument('--disable-dev-shm-usage')

#create a new instance of Chrome
path = '/Library/Application Support/Google/chromedriver'
browser = webdriver.Chrome(executable_path= path, options=option)

df = get_city_lisitings_pages(browser,n_pages=100)

df.to_csv('mubawab_listings.csv',index=False)


