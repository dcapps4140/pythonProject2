import json
from bs4 import BeautifulSoup
import pandas as pd
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
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'zguid=23|%243000923b-89c8-428d-b509-0ba18a0d03ce; _ga=GA1.2.1117637457.1636003865; _pxvid=6a042539-3d30-11ec-8adc-657144725868; _gcl_au=1.1.1703321702.1636003871; __pdst=e0205f2af7c145bda0387c70daa68e23; _fbp=fb.1.1636003881141.702124889; _pin_unauth=dWlkPVltVm1Oak0zWXpjdE56QTNNUzAwWVdGbUxUaGhZemd0TmpSbFpXVTBabUprTVRJeA; g_state={"i_l":0}; loginmemento=1|c6f8431dc8f743862fb15a1c92f5875e5ac95d046bc2ec204571bb0c9470eda9; userid=X|3|7a2721fd60a3d3d3%7C1%7CcWZKOdXXoQ4dP63qaC3xK_bkUVWJrCqX; zjs_user_id=%22X1-ZUxzdpy1x13rwp_7galw%22; __gads=ID=3b70885dde241d38:T=1636003972:S=ALNI_MZaKw3ASEvhztZO3fpMusYMNU5Q_w; zgcus_lbut=; zgcus_aeut=32319401; zgcus_lddid=0fba597c4bd05c898bec045700550511; zgcus_ludi=85f95378-3f91-11ec-88f7-12502e1e72a6-32319; optimizelyEndUserId=oeu1636265481634r0.3650156085522711; FSsampler=1614911018; _cs_c=0; OptanonConsent=isIABGlobal=false&datestamp=Sun+Nov+07+2021+01%3A12%3A22+GMT-0500+(Central+Daylight+Time)&version=5.11.0&landingPath=https%3A%2F%2Fwww.zillow.com%2Frental-manager%2Fproperties%3Fsource%3Dtopnav%26itc%3Dpostbutton_sitenav%26subNavFilterType%3Dall&groups=1%3A1%2C3%3A1%2C4%3A1; visitor_id701843=287994878; visitor_id701843-hash=b58d6dd7200ce6362ad2931b8352cdac2555eec4d50d226b3d59c979b1764590eb418f9051d63a8a384ab3c55cbb751d3dd22326; __stripe_mid=86a0bf58-d6a5-44e6-bec2-ff25adc355f67a26e1; _cs_id=7ac7e2ac-678e-a6f0-8d76-62ca1b2498dc.1636265531.14.1636307360.1636307360.1.1670429531171; zjs_anonymous_id=%223000923b-89c8-428d-b509-0ba18a0d03ce%22; KruxPixel=true; KruxAddition=true; JSESSIONID=CEA7320F9B58301608EE6FD14272F638; zgsession=1|9b88ee4a-80a2-4e47-90a0-542419d91ee3; ZILLOW_SID=1|AAAAAVVbFRIBVVsVEsMcDd5CyyGXU6Zn4wm8RCEF50%2Fs51GDH%2BqnNZZGyaZPBsNaktmOJ4pqOZZZF17dLAhdgtJoaiem; _gid=GA1.2.1677155920.1636636944; _gat=1; _pxff_bsco=1; _px3=02fcd30a9c4666d7eefba7839e31d345113ad7fbcfe78540acd42d2b8827875a:qUDIKOrTKoJJVdWm6iXdl6rshmBFSbMDe1UnggrSQtaP+18Rcdia5ZljpZUxoQOW2u9/Qw+dMk/l72J6uJgLXw==:1000:3pOItBQFVmPyKHhzag5Lk97HTOg0icsAiPR97qM+F7iDJ9J9Btwy17TNxdFNLSHiyo6Bu2nJJKJDRv8mVxstDSSn46ULxo4KvITWXOTkqhLjAJEBI+w3VBqpT7o9kIlPv3SPh8rkdNXMp0QNZ8tJDaSlIuFnE0HLcAaW++SLhaeErTh74ik2w1LJ/n5aOfy/FG8IXlANDt11dx3iWezcbg==; DoubleClickSession=true; _uetsid=73cb4a2042f211eca45f97ada49dc59e; _uetvid=6e74e1203d3011eca2f46b2661367a8d; utag_main=v_id:017ce96e113b0000511a5b97f37905072001706a0086e$_sn:6$_se:1$_ss:1$_st:1636638763580$dc_visit:4$ses_id:1636636963580%3Bexp-session$_pn:1%3Bexp-session$dcsyncran:1%3Bexp-session$tdsyncran:1%3Bexp-session$dc_event:1%3Bexp-session$dc_region:us-east-1%3Bexp-session$ttd_uuid:6fc6f450-3adc-4efe-b19f-8aa0a05af61f%3Bexp-session; AWSALB=GXGi20w9jiN1hNUycwHNVTC7XaCOqS5t/i+gVlSg4YSp0s+p5R6qukXT4EuhYCANJR/OmRYS+jG4RDi2vA34VZFoVN9OXGJvvkwCl/LhKUIO5cnTN8S6BwtFjW3g; AWSALBCORS=GXGi20w9jiN1hNUycwHNVTC7XaCOqS5t/i+gVlSg4YSp0s+p5R6qukXT4EuhYCANJR/OmRYS+jG4RDi2vA34VZFoVN9OXGJvvkwCl/LhKUIO5cnTN8S6BwtFjW3g; search=6|1639228983517%7Crect%3D40.6230601837222%252C-88.79387356738282%252C40.34626904524745%252C-89.16603543261719%26rid%3D23742%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26z%3D1%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%09%0923742%09%09%09%09%09%09',
    'dnt': '1',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
}

params = {'searchQueryState': '{"pagination":{"currentpage": 1},"mapBounds":{"west":-89.16603543261719,"east":-88.79387356738282,"south":40.34626904524745,"north":40.6230601837222},"regionSelection":[{"regionId":23742,"regionType":6}],"isMapVisible":true,"filterState":{"sortSelection":{"value":"globalrelevanceex"},"isAllHomes":{"value":true}},"isListVisible":true,"mapZoom":11}'}
# create url variables for each zillow page
with requests.Session() as s:
    city = 'peoria-il/'  # *****change this city to what you want!!!!*****

    url = 'https://www.zillow.com/homes/for_sale/' + city

    r = s.get(url, headers=req_headers)

    url_links = [url]

# add contents of urls to soup variable from each url
#soup = BeautifulSoup(r.content, 'html.parser')

# page_links = [soup, soup1, soup2, soup3, soup4, soup5, soup6, soup7, soup8, soup9]
results = []
# create the first two dataframes
#df = pd.DataFrame()
#*******************
response = requests.get(url, headers=headers, params=params)
content = BeautifulSoup(response, 'lxml')
deck = content.find('ul', {'class': 'photo-cards photo-cards_wow photo-cards_short photo-cards_extra-attribution'})
for card in deck.contents:
    script = card.find('script', {'type': 'application/ld+json'})
    if script:
        script_json = json.loads(script.contents[0])
        results.append({
            'address': script_json['address']['streetAddress'],
            'zipcode': script_json['address']['postalCode'],
            'links': script_json['url']
        })
        df = pd.DataFrame(results)
#*******************


# all for loops are pulling the specified variable using beautiful soup and inserting into said variable
for i in soup:
    #address = soup.find_all(class_='list-card-addr')
    price = list(soup.find_all(class_='list-card-price'))
    beds = list(soup.find_all("ul", class_="list-card-details"))
    details = soup.find_all('div', {'class': 'list-card-details'})
    home_type = soup.find_all('div', {'class': 'list-card-footer'})
    last_updated = soup.find_all('div', {'class': 'list-card-top'})
    brokerage = list(soup.find_all(class_='list-card-brokerage list-card-img-overlay', text=True))
    #link = soup.find_all(class_='list-card-link')

    # create dataframe columns out of variables
    df['prices'] = price
    #df['address'] = address
    df['beds'] = beds

# create empty url list
#urls = []
#
# # loop through url, pull the href and strip out the address tag
# for link in soup.find_all("article"):
#     try:
#         href = link.find('a', class_='list-card-link list-card-link-top-margin')
#         print('1', href)
#         addresses = href.find('address', class_='list-card-addr')
#         print('2', addresses)
#         addresses.extract()
#         #print(link.find('a', {'class': 'list-card-link list-card-link-top-margin'}).text)
#         urls.append(href)
#         print('3', urls)
#     except:
#         print('error')

print('import urls into a links column')
# df['links'] = urls
df['links'] = df['links'].astype('str')

print('remove html tags')
# df['links'] = df['links'].replace('<a class="list-card-link" href="', ' ', regex=True)
# df['links'] = df['links'].replace('" tabindex="0"></a>', ' ', regex=True)

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
# df['links'] = df.links.str.replace(' ', '')

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