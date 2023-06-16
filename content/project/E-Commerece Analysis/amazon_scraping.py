# Importing libraries
import time
import csv
import datetime
import requests
import os
from bs4 import BeautifulSoup


# Connecting to the Amazon's product webpage.
def check_price():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    page = requests.get(
        'https://www.amazon.com/Funny-Data-Systems-Business-Analyst/dp/B07FNW9FGJ/ref=sr_1_3?dchild=1&keywords=data%2Banalyst%2Btshirt&qid=1626655184&sr=8-3&customId=B0752XJYNL&th=1',
        headers=headers)  # connecting to amazon

# Parsing and cleaning the scraped data and then stores it in a CSV.

    soup = BeautifulSoup(page.text, "html.parser")  # parsing the HTML result.

    title = soup.find(id='productTitle').get_text().strip()  # fetching the product's name.
    price = soup.find('span', class_="a-offscreen").get_text().strip()  # fetching the product's price.
    price = float(price.replace('$', ''))  # removing the dollar sign.

    today = datetime.date.today().strftime("%d-%m-%Y")  # getting today's date.

    data_itself = [title, price, today]
    col_names = ["Title", "Price", "Date"]

    with open('Amazon_Price_Data.csv', 'a+', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        f.seek(0, os.SEEK_END)  # seek to the end of the file
        if f.tell() == 0:  # write headers if the file is empty
            writer.writerow(col_names)
        writer.writerow(data_itself)

    return price

# The loop executes every 5 seconds and checks if the price dropped below 15 USD.
while True:
    price = check_price()
    if price > 15:
        print("Price has dropped below 15$. This loop will terminate now.")
        break
    time.sleep(5)