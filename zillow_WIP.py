from lxml import html
import requests
import unicodecsv as csv
import argparse
import re
import pandas as pd


def parse(zipcode, filter=None):
    if filter == "newest":
        url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(zipcode)
    elif filter == "cheapest":
        url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(zipcode)
    else:
        url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(
            zipcode)

    for i in range(5):
        # try:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        # print(response.status_code)
        parser = html.fromstring(response.text)
        search_results = parser.xpath("//div[@id='search-results']//article")
        properties_list = []

        for properties in search_results:
            raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
            raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
            raw_state = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
            raw_postal_code = properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
            raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
            raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
            raw_broker_name = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
            url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
            raw_title = properties.xpath(".//h4//text()")

            address = ' '.join(' '.join(raw_address).split()) if raw_address else None
            city = ''.join(raw_city).strip() if raw_city else None
            state = ''.join(raw_state).strip() if raw_state else None
            postal_code = ''.join(raw_postal_code).strip() if raw_postal_code else None
            price = ''.join(raw_price).strip() if raw_price else None
            if price == None:
                continue
            print(price)
            price = ''.join(re.findall(r'\d+', price))

            print(price)

            info = ' '.join(' '.join(raw_info).split()).replace(u"\xb7", ',')
            temp = re.findall(r'\d+', info)
            # print(temp)
            if len(temp) == 3:
                temp.append("")
            elif len(temp) < 3:
                continue
            info_temp = (temp[0] + ',' + temp[1] + ',' + temp[2] + temp[3]).split(',')
            # print(info_temp)
            beds = info_temp[0]
            baths = info_temp[1]
            sqrt = info_temp[2]
            broker = ''.join(raw_broker_name).strip() if raw_broker_name else None
            title = ''.join(raw_title) if raw_title else None
            property_url = "https://www.zillow.com" + url[0] if url else None
            is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')
            properties = {
                'address': address,
                'city': city,
                'state': state,
                'postal_code': postal_code,
                'price': price,
                # 'facts and features': info,
                'beds': beds,
                'baths': baths,
                'sqrt': sqrt,
                'real estate provider': broker,
                'url': property_url,
                'title': title
            }
            if is_forsale:
                properties_list.append(properties)

        print("Parse finished!")
        return properties_list


def write_to_csv(scraped_data):
    # print("Writing data to output file")
    # print(scraped_data)
    current_date = date.today().isoformat().replace("-", "")
    fieldnames = ['title', 'address', 'city', 'state', 'postal_code', 'price', 'beds', 'baths', 'sqrt',
                  'real estate provider', 'url']
    with open("%s_houses.csv" % current_date, 'a+') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in scraped_data:
            try:
                print(row)
                writer.writerow(row)
            except:
                print("error in write, skip")
    print("Write finished!")


def get_zipcodes(county_list):
    mydata = pd.read_csv("F:\\myprojects\\zillow_explore\\geo.csv", header=None)
    mydata.columns = ['City', 'County', 'State', 'zipcode', 'lat', 'lng', 'type', 'Country', 'ETC']
    zipcodes = mydata.query('County == @county_list').zipcode
    return list(zipcodes)


if __name__ == "__main__":
    county_names = ['SANTA CLARA']
    zipcode_list = get_zipcodes(county_names)
    # zipcode = '94536'
    scraped_data = []
    for zipcode in zipcode_list:
        print("Dealing with %s" % zipcode)
        # print(scraped_data[])
        scraped_data.append(parse(zipcode))
    print("Start writing")
    write_to_csv(scraped_data)