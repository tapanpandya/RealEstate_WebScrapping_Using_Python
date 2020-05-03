from bs4 import BeautifulSoup
from requests import get
from datetime import datetime, timedelta
import re
import pandas as pd
import seaborn as sns
sns.set()

class DataAPI:

    def request(self):
        url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?proptype=Residential-House,Villa&cityName=Ahmedabad"
        response = get(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        containers = html_soup.find_all('div', class_="flex relative clearfix m-srp-card__container")
        return containers


class DataExtractor:
    def __init__(self):
        self.title = self.get_Title()
        self.sqrFt = self.get_SqrFt()
        self.date = self.get_Date()
        self.price = self.get_Price()
        self.prSqrFt = self.get_Per_Sq_Price()


    def totalPages(self):
        total_properties = 0
        house_containers = DataAPI.request()
        number_of_properties = str(house_containers.find_all('h1', class_="SRHeading"))
        p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
        if re.search(p, number_of_properties) is not None:
            for catch in re.finditer(p, number_of_properties):
                if int(catch[0]) > 1:
                    total_properties = int(catch[0])
        return int(total_properties)

    def get_Title(self):
        house_containers = DataAPI.request(self)
        titles = []
        areas = []

        for i in range(len(house_containers)):
            first = house_containers[i]
            # Fetching Title of properties
            title = str(first.find_all('span')[3].getText())
            title = title.replace('\n', '')
            titles.append(title)

            # Now getting areas
            query = re.compile("in(.*)")
            area = str(query.findall(title))
            if area:
                if len(area) > 2:
                    slice_object = slice(2, -2)
                    areas.append(area[slice_object])
                elif len(area) <= 2:
                    areas.append("Ahmedabad")
            else:
                areas.append("NaN")
        return titles, areas

    def get_SqrFt(self):
        house_containers = DataAPI.request(self)
        sqr_feets = []
        for i in range(len(house_containers)):
            first = house_containers[i]

            ## Fetching area information(Sqft)
            sqr_feet = first.find_all('div', class_="m-srp-card__summary__info")[0]
            q = '\>.*?\<'
            if re.search(q, str(sqr_feet)) is not None:
                sqr_feet_ = str(re.findall(q, str(sqr_feet)))
                sqr_feet_sc = sqr_feet_.replace('\\xa0', ' ')
                slice_object = slice(3, -3)
                sqr_feets.append(sqr_feet_sc[slice_object])
            else:
                sqr_feets.append("NaN")
        return sqr_feets

    def get_Date(self):
        house_containers = DataAPI.request(self)
        dates = []
        for i in range(len(house_containers)):
            first = house_containers[i]

            # Fetching property posting date
            today = datetime.today()
            date = first.find_all('span', itemprop="dateCreated")
            q = '\>.*?\<'
            if re.search(q, str(date)) is not None:
                date_ = str(re.findall(q, str(date)))
                if 'Today' in date_:
                    date_ = date_.replace('Today', today.strftime("%B %d, %Y"))
                    slice_object = slice(3, -3)
                    dates.append(date_[slice_object])
                elif 'Yesterday' in date_:
                    yesterday = today.now() - timedelta(days=1)
                    date_ = date_.replace('Yesterday', yesterday.strftime("%B %d, %Y"))
                    slice_object = slice(3, -3)
                    dates.append(date_[slice_object])
                else:
                    slice_object = slice(3, -3)
                    dates.append(date_[slice_object])
            else:
                dates.append("NaN")
        return dates

    def get_Price(self):
        house_containers = DataAPI.request(self)
        for i in range(len(house_containers)):
            first = house_containers[i]
            prices = []

            ## Fetching prices from MagicBricks.com for Ahmedabad, Gujarata, INDIA.
            price = first.find_all('span')[1].text
            if '.' in price:
                rm_price = price.replace('.', '')
                if ' Lac' in rm_price:
                    p = rm_price.replace(' Lac', '00000')
                    prices.append(p)
                elif ' Cr' in rm_price:
                    p = rm_price.replace(' Cr', '0000000')
                    prices.append(p)
                else:
                    prices.append("NaN")
                    # prices.append(rm_price)
            else:
                if ' Lac' in price:
                    p = price.replace(' Lac', '00000')
                    prices.append(p)
                elif ' Cr' in price:
                    p = price.replace(' Cr', '0000000')
                    prices.append(p)
                else:
                    prices.append("NaN")
                    # prices.append(price)
        return prices

    def get_Per_Sq_Price(self):
        house_containers = DataAPI.request(self)
        sqr_prices = []
        for i in range(len(house_containers)):
            first = house_containers[i]
            per_sqr_price = first.find_all('div', class_="m-srp-card__area")
            q = '\>.*?\<'
            if re.search(q, str(per_sqr_price)) is not None:
                sqr_price_ = str(re.findall(q, str(per_sqr_price)))
                slice_object = slice(11, -3)
                sqr_price = sqr_price_[slice_object]
                sqr_prices.append(sqr_price.replace("<', '>", " "))
            else:
                sqr_prices.append("NaN")
        return sqr_prices


title, area = DataExtractor().get_Title()
sqr_price = DataExtractor().get_Per_Sq_Price()
date = DataExtractor().get_Date()
sqr_ft = DataExtractor().get_SqrFt()
price = DataExtractor().get_Price()

print(len(str(title)))
print(len(str(area)))
print(len(str(sqr_price)))
print(len(str(sqr_ft)))
print(len(str(date)))
print(len(str(price)))

max_length = max(max(len(title), len(area)), len(sqr_price), len(sqr_ft), len(date), len(price))
title += ['X'] * (max_length - len(title))
area += ['X'] * (max_length - len(area))
sqr_price += ['X'] * (max_length - len(sqr_price))
sqr_ft += ['X'] * (max_length - len(sqr_ft))
date += ['X'] * (max_length - len(date))
price += ['X'] * (max_length - len(price))

cols = ['Title', 'Area', 'Price', 'SqrFt', 'Sq.Price', 'Date']

DataFrame = pd.DataFrame({'Title': title,
                        'Area': area,
                        'Price': price,
                        'SqrFt': sqr_ft,
                        'Sq.Price': sqr_price,
                        'Date': date})[cols]

DataFrame.to_csv('Ahmedabad_MagicBricks.csv')