
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import numpy as np
import pandas as pd

'''
This script scrapes the mubawab website starting from the properties for sale page. 
It gets to the listing page through city selection page, district selection page and 
when the district is large enough it also goes through the neighbourhood selection page to 
finally land on the listings pages and start scraping listing by listing and page by page.
'''

def on_listings_page(browser):
    '''
    Check if the browser is on a page with property listings on the mubawab website
    
    params
        browser: the selenium webdriver used to make requests
    '''
    try:
        browser.find_element_by_xpath('/html/body/section/div[2]/div[1]/div[2]/i')
        return True
    except NoSuchElementException:
        return False

def get_listing(browser,ard,qrt=None,n=0):
    '''
    This function gets the info of the n'th listing on a listings page and goes back to that page
    
    params
        browser: the selenium webdriver used to make requests
        ard: the district selected to land on listings page
        qrt: if it was used, the neighbourhood selected to land on listings page, otherwise None
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
    ls = [ard,qrt,type_,loca,lat,lon,title,price,other_tags]
    browser.back()
    return ls

def get_listings_pages(browser, ard, qrt = None, n_pages = None):
    '''
    This functions runs through all the pages of listings and returns an array with the listings informations
    
    params
        browser: the selenium webdriver used to make requests
        ard: the district selected to land on listings page
        qrt: if it was used, the neighbourhood selected to land on listings page, otherwise None
        n_pages: the number of pages to scrape from listings pages, if None will scrape all pages
    '''
    #initialize an empty array to store the listings info
    listings_info = []
    if not on_listings_page(browser):
        raise Exception('Not a listings page')
    else:
        n_pages_avl = len(browser.find_elements_by_class_name('Dots'))
        if n_pages is None:
            #initialize variable to stop the function when the last page has been ran through
            last_page = False
            i=1 #for debugging
            while not last_page:
                n_listings = len(browser.find_elements_by_xpath("//li[@class='listingBox w100']"))
                print(f'    should get {n_listings} listings from page {i}') #for debugging
                for n in range(n_listings):
                    ls = get_listing(browser,ard=ard,qrt=qrt,n=n)
                    listings_info.append(ls)
                    
                #go to next page if not on last page
                try:
                    arrows = browser.find_elements_by_class_name('arrowDot')
                    arrows[1].click()  
                    i+=1 #for debugging
                #if on last page stop 
                except : #ElementClickInterceptedException removed
                    last_page = True
            return listings_info
    
        else:
            if (n_pages > n_pages_avl) or (not isinstance(n_pages,int)) or (n_pages<=0):
                print(f'    n_pages must be positive integer smaller or equal to the number of pages, in this case {n_pages_avl}')
                n_pages = n_pages_avl
            for i in range(n_pages):
                n_listings = len(browser.find_elements_by_xpath("//li[@class='listingBox w100']"))
                print(f'should get {n_listings} listings form page {i}') #for debugging
                for n in range(n_listings):
                    ls = get_listing(browser,ard=ard,qrt=qrt,n=n)
                    listings_info.append(ls)
                    pass
                try:
                    arrows = browser.find_elements_by_class_name('arrowDot')
                    arrows[1].click()   
                except : #ElementClickInterceptedException removed
                    last_page = True
            return listings_info

def get_city_listings(browser,city,n_pages=None):
    '''
    This function return a dataframe with all the relevant property listings info scraped for a selected city

    Parameters
    ----------
    browser : webdriver
        The selenium webdriver used to make requests
    city : String
        The selected city to be scraped
    n_pages : int, optional
        The number of page to be scraped for each district or neihbourhood of the city The default is None.

    Returns
    -------
    df : DataFrame
        dataframe with following columns :
        'District','Neighbourhood','Type','Localisation','Latitude','Longitude','Title','Price','Tags'

    '''
    if not(isinstance(city,str)):
        raise TypeError('city must be of type string')
    else:
        #initialize empty array to store all the different listings
        all_data = []
        
        #make the request to desired url
        url = 'https://www.mubawab.ma/fr/mp/immobilier-a-vendre'
        browser.get(url)
        
        # Code to wait for website to load   
        # Wait 20 seconds for page to load
        timeout = 20
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='na-map']")))
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()
        #Select city and click on its button in the top cities list
        city = city.lower()
        city_buttons = browser.find_elements_by_xpath('//*[@id="top-villes"]/div/div/button')
        for button in city_buttons:
            if button.text.lower() == city.lower():
                click = button
        try:
            click.click()
        except:
            print(f'{city} not in top cities')
    
    # Wait up to 10 seconds for page to load or until map appears
    timeout = 10
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='na-map']")))
    except TimeoutException:
        print("Timed out waiting for district page to load")
        browser.quit()
    
    url_ard = browser.current_url #Get the city's district selection page url to get back to it later
    n_arrondissements = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li')) #Get the city's number districts to navigate
    
    #Start navigating district by district
    for n in range(1,n_arrondissements+1):
        arrondissement = browser.find_element_by_xpath(f'/html/body/section/div[2]/div[1]/div[2]/ul/li[{n}]/a') #Locate the n'th district to select
        ard_text = arrondissement.text #Get the district name
        arrondissement.click() 
        
        if on_listings_page(browser): #Check it this is a listings page or a neighbourhood selection page
            print(f'getting listings for {ard_text}') #To follow  progress along in headless mode
            all_data.append(get_listings_pages(browser, ard=ard_text,n_pages = n_pages)) #Scrape all or n_pages pages of listings
            browser.get(url_ard) #Go back to district selection page
        else:
            url_qrt = browser.current_url #Get the district's neighbourhood selection page url to get back to it later
            n_quartiers = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li')) #Get the district's number of neighbourhoods to navigate
            for nq in range(1,n_quartiers+1):
                quartier = browser.find_element_by_xpath(f'/html/body/section/div[2]/div[1]/div[2]/ul/li[{nq}]/a') #Locate the nq'th neighbourhood to select
                qrt_text = quartier.text #Get the neighbourhood name
                quartier.click()
                #Scrape the listings for neighbourhood nq
                print(f'getting listings for {ard_text}, {qrt_text}') #To follow progress along in headless mode
                all_data.append(get_listings_pages(browser,ard = ard_text, qrt= qrt_text,n_pages = n_pages)) #Scrape all or n_pages pages of listings
                browser.get(url_qrt) #Go back to neighbourhood selection page
            browser.get(url_ard) #Go back to district selection page
    
    #Convert all arrays into dataframes and concatenate all into a single dataframe
    df = pd.concat([pd.DataFrame(lst) for lst in all_data]).reset_index(drop = True)
    
    #Set the dataframe's columns
    df.columns = ['District','Neighbourhood','Type','Localisation','Latitude','Longitude','Title','Price','Tags']
    
    return df

        
#adding the incognito argument to webdriver
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
#option.headless = True

#create a new instance of Chrome
driver_path = '/Library/Application Support/Google/chromedriver'
browser = webdriver.Chrome(executable_path=driver_path, options=option)


df = get_city_listings(browser,'Casablanca',n_pages = 1)
df.to_csv('mubawab_listings_ard_qrt.cvs',index=False)
