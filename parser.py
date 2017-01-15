# -*- coding: utf-8 -*-
import os
import csv
import time
import urllib2
import dryscrape

from selenium import webdriver
from bs4 import BeautifulSoup

#source_link = "https://search.jd.com/Search?keyword=qnap&enc=utf-8&wq=qnap&pvid=yhzxfuxi.4ocx0a00n52av"

# link of source
source_link = "https://search.jd.com/Search?keyword=qnap&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&wq=qnap&ev=exbrand_威联通（QNAP）%40&page={0}&s={1}&click=0"


def bs(url):
    """
    parse page of goods data

    ### url: link of page for parsing
    """
    link = 'https:{}'.format(url)
    page_link = urllib2.urlopen(link).read()
    return page_link


def write_to(data):
    """
    function for writing to csv file

    ### data: data for write to file;
    ###       brand, mpn, url, name, prices, stocks.
    """
    with open("results.csv", "a") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(data)


def browser(url, page, mount):
    """
    browsing page of list products data

    ### url: link of goods page_link
    ### page: number of page_link
    ### mount: mount of products per page
    """
    src_link = url.format(page, mount)

    driver = webdriver.Chrome()
    driver.get(src_link)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # time for loading data on page
    time.sleep(5)

    site = driver.page_source
    driver.quit()

    return site


def main():
    """
    main function for parse

    """

    # numbers of pages
    # step = 2 because default loads 30 goods
    # and further loads by JS extra 30 goods
    pages = range(1, 14, 2)

    # mount goods per page
    mount = 61

    for page in pages:

        site = browser(source_link, page, mount)
        soup = BeautifulSoup(site, "html.parser")

        page_goods = soup.find("div", id="J_goodsList")
        ul_lst = page_goods.find("ul", class_="gl-warp")
        li_lst = ul_lst.findAll("li")

        mount += 60

        gds_link = []
        prices = []
        stocks = []

        for item in li_lst:

            gds_block = item.find("div", class_="p-name")
            gds_link.append(gds_block.find("a")['href'])

            # price
            gds_price = item.find("div", class_="p-price")
            prices.append(gds_price.find("i").text)

            # stock
            gds_stock = item.find("div", class_="p-operate")

            try:
                if gds_stock.find("a", class_="addcart"):
                    stocks.append('1')
                else:
                    stocks.append('0')
            except AttributeError:
                stocks.append('0')

        for item in range(len(gds_link)):

            link = bs(gds_link[item])
            page_soup = BeautifulSoup(link, "html.parser")

            # name
            try:
                nm_block = page_soup.find("div", id="name")
                name = nm_block.find("h1").text
            except AttributeError:
                name = page_soup.find("div", class_="sku-name").text

            # brand
            brn = page_soup.find("ul", id="parameter-brand")
            brand = brn.find("li")["title"]

            # MPN
            ul_mpn = page_soup.findAll("ul", class_="p-parameter-list")
            lst_mpn = ul_mpn[1].findAll("li")
            mpn = lst_mpn[1]["title"]

            url = gds_link[item]

            data = [
                brand.encode("utf-8"),
                mpn,
                url,
                name.encode("utf-8"),
                prices[item],
                stocks[item]
            ]

            write_to(data)


if __name__ == "__main__":
    main()
