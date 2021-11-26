import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import numpy as np
import pandas as pd
import regex as re
import requests
import lxml
from lxml.html.soupparser import fromstring
import prettify
import numbers
import htmltext

# add headers in case you use chromedriver (captchas are no fun); namely used for chromedriver
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# create url variables for each zillow page
with requests.Session() as s:
    city = 'peoria/'  # *****change this city to what you want!!!!*****

    url = 'https://www.zillow.com/homes/for_sale/' + city

    r = s.get(url, headers=req_headers)

    url_links = [url]

# add contents of urls to soup variable from each url
soup = BeautifulSoup(r.content, 'html.parser')

# page_links = [soup, soup1, soup2, soup3, soup4, soup5, soup6, soup7, soup8, soup9]

# create the first two dataframes
df = pd.DataFrame()

# all for loops are pulling the specified variable using beautiful soup and inserting into said variable
for i in soup:
    address = soup.find_all(class_='list-card-addr')
    price = list(soup.find_all(class_='list-card-price'))
    beds = list(soup.find_all("ul", class_="list-card-details"))
    details = soup.find_all('div', {'class': 'list-card-details'})
    home_type = soup.find_all('div', {'class': 'list-card-footer'})
    last_updated = soup.find_all('div', {'class': 'list-card-top'})
    brokerage = list(soup.find_all(class_='list-card-brokerage list-card-img-overlay', text=True))
    link = soup.find_all(class_='list-card-link')

    # create dataframe columns out of variables
    df['prices'] = price
    df['address'] = address
    df['beds'] = beds

# create empty url list
urls = []

# loop through url, pull the href and strip out the address tag
for link in soup.find_all("article"):
    try:
        href = link.find('a', class_='list-card-link list-card-link-top-margin')
        print('1', href)
        addresses = href.find('address', class_='list-card-addr')
        print('2', addresses)
        addresses.extract()
        #print(link.find('a', {'class': 'list-card-link list-card-link-top-margin'}).text)
        urls.append(href)
        print('3', urls)
    except:
        print('error')

print('import urls into a links column')
df['links'] = urls
df['links'] = df['links'].astype('str')

print('remove html tags')
df['links'] = df['links'].replace('<a class="list-card-link" href="', ' ', regex=True)
df['links'] = df['links'].replace('" tabindex="0"></a>', ' ', regex=True)

print('convert columns to str')
df['prices'] = df['prices'].astype('str')
df['address'] = df['address'].astype('str')
df['beds'] = df['beds'].astype('str')

print('remove html tags')
df['prices'] = df['prices'].replace('<div class="list-card-price">', ' ', regex=True)
df['address'] = df['address'].replace('<address class="list-card-addr">', ' ', regex=True)
df['prices'] = df['prices'].replace('</div>', ' ', regex=True)
df['address'] = df['address'].replace('</address>', ' ', regex=True)
df['prices'] = df['prices'].str.replace(r'\D', '', regex=True)

print('remove html tags from beds column')
df['beds'] = df['beds'].replace('<ul class="list-card-details"><li class="">', ' ', regex=True)
df['beds'] = df['beds'].replace('<abbr class="list-card-label"> <!-- -->bds</abbr></li><li class="">', ' ', regex=True)
df['beds'] = df['beds'].replace('<abbr class="list-card-label"> <!-- -->ba</abbr></li><li class="">', ' ', regex=True)
df['beds'] = df['beds'].replace('<abbr class="list-card-label"> <!-- -->bd</abbr></li><li class="">', ' ', regex=True)
df['beds'] = df['beds'].replace('<abbr class="list-card-label"> <!-- -->sqft</abbr></li><li class="list-card-statusText">- House for sale</li></ul>', ' ', regex=True)
df['beds'] = df['beds'].replace('Studio</li><li>', '0 ', regex=True)

print('split beds column into beds, bath and sq_feet')
df[['beds', 'baths', 'sq_feet']] = df.beds.str.split(expand=True)

print('remove commas from sq_feet and convert to float')
df.replace(',', '', regex=True, inplace=True)

print('drop nulls')
df = df[(df['prices'] != '') & (df['prices'] != ' ')]

print('convert column to float')
df['prices'] = df['prices'].astype('float')
# d['sq_feet'] = df['sq_feet'].astype('float')

print('remove spaces from link column')
df['links'] = df.links.str.replace(' ', '')

print(df['links'])

print('The column datatypes are:')
print(df.dtypes)
print('The dataframe shape is:', df.shape)

print('rearrange the columns')
df = df[['prices', 'address', 'links', 'beds', 'baths', 'sq_feet']]

print('calculate the zestimate and insert into a dataframe')
zillow_zestimate = []
for link in df['links']:
    print(link)
    r = s.get(link, headers=req_headers)
    print(r)
    soup = BeautifulSoup(r.content, 'html.parser')
    home_value = soup.select_one('h4:contains("Home value")')
    if not home_value:
        home_value = soup.select_one('.zestimate').text.split()[-1]
    else:
        home_value = home_value.find_next('p').get_text(strip=True)
    zillow_zestimate.append(home_value)

cols = ['zestimate']
zestimate_result = pd.DataFrame(zillow_zestimate, columns=cols)
# zestimate_result

# convert zestimate column to float, and remove , and $
zestimate_result['zestimate'] = zestimate_result['zestimate'].str.replace('$', '')
zestimate_result['zestimate'] = zestimate_result['zestimate'].str.replace('/mo', '')
zestimate_result['zestimate'] = zestimate_result['zestimate'].str.replace(',', '')


print('covert rows with non zestimate to 0')
def non_zestimate(zestimate_result):
    if len(zestimate_result['zestimate']) > 20:
        return '0'
    elif len(zestimate_result['zestimate']) < 5:
        return '0'
    else:
        return zestimate_result['zestimate']


zestimate_result['zestimate'] = zestimate_result.apply(non_zestimate, axis=1)

# zestimate_result

# concat zestimate dataframe and original df
df = pd.concat([df, zestimate_result], axis=1)
df['zestimate'] = df['zestimate'].astype('float')

print('create best deal column and sort by best_deal')
df['best_deal'] = df['prices'] - df['zestimate']
df = df.sort_values(by='best_deal')

print('df')