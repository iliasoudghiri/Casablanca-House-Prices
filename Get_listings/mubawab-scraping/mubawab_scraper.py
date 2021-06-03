
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import numpy as np
import pandas as pd

def on_listings_page(browser):
    '''
    check if the browser is on a page with property listings on the mubawab website
    '''
    try:
        browser.find_element_by_xpath('/html/body/section/div[2]/div[1]/div[2]/i')
        return True
    except NoSuchElementException:
        return False

def get_listing(browser,ard,qrt,n=0):
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
    ls = [ard,qrt,loca,type_,title,price,other_tags]
    browser.back()
    return ls

def get_listings_pages(browser, ard,qrt, n_pages = None):
    '''
    This functions runs through all the pages of listings and returns an array with the listings informations
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

#initialize empty array to store all the different listings
all_data = []
        
#adding the incognito argument to webdriver
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
#option.headless = True

#create a new instance of Chrome
driver_path = '/Library/Application Support/Google/chromedriver'
browser = webdriver.Chrome(executable_path=driver_path, options=option)

#make the request to desired url
url = 'https://www.mubawab.ma/fr/mp/immobilier-a-vendre'
browser.get(url)

''' Code to wait for website to load   
# Wait 20 seconds for page to load
timeout = 20
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='na-map']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()
'''

#Select city and click on its button in the top cities list
city = 'casablanca' 
city_buttons = browser.find_elements_by_xpath('//*[@id="top-villes"]/div/div/button')
for button in city_buttons:
    if button.text.lower() == city.lower():
        click = button
try:
    click.click()
except:
    print(f'{city} not in top cities')

# Wait up to 10 seconds for page to load
timeout = 10
try:
    WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='na-map']")))
except TimeoutException:
    print("Timed out waiting for page to load")
    browser.quit()

url_ard = browser.current_url
n_arrondissements = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li'))
for n in range(1,n_arrondissements+1):
    arrondissement = browser.find_element_by_xpath(f'/html/body/section/div[2]/div[1]/div[2]/ul/li[{n}]/a')
    ard_text = arrondissement.text
    qrt_text = np.nan
    arrondissement.click() #add arrondissement selector
    if on_listings_page(browser):
        print(f'getting listings for {ard_text}')
        all_data.append(get_listings_pages(browser, ard=ard_text, qrt=qrt_text,n_pages = 3))
        browser.get(url_ard)
    else:
        url_qrt = browser.current_url
        n_quartiers = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li'))
        for nq in range(1,n_quartiers+1):
            quartier = browser.find_element_by_xpath(f'/html/body/section/div[2]/div[1]/div[2]/ul/li[{nq}]/a')
            qrt_text = quartier.text
            quartier.click()
            print(f'getting listings for {ard_text}, {qrt_text}')
            all_data.append(get_listings_pages(browser,ard = ard_text, qrt= qrt_text,n_pages = 3))
            browser.get(url_qrt)
        browser.get(url_ard)
'''
url_ard = browser.current_url
n_arrondissements = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li'))
for n in range(n_arrondissements):
    arrondissements = browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li')
    ard_text = arrondissements[n].text
    qrt_text = np.nan
    arrondissements[n].click() #add arrondissement selector
    try :
        all_data.append(get_listings_pages(browser, ard=ard_text, qrt=qrt_text))
        browser.get(url_ard)
    except:
        url_qrt = browser.current_url
        n_quartiers = len(browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li'))
        for nq in range(n_quartiers):
            quartiers = browser.find_elements_by_xpath('/html/body/section/div[2]/div[1]/div[2]/ul/li')
            qrt_text = quartiers[nq].text
            quartiers[nq].click()
            all_data.append(get_listings_pages(browser,ard = ard_text, qrt= qrt_text))
            browser.get(url_qrt)
        browser.get(url_ard)
'''
df = pd.concat([pd.DataFrame(lst) for lst in all_data]).reset_index(drop = True)


