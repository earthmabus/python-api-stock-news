import os
import requests
from datetime import timedelta

import email_account
import datetime as dt

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# load in the email account credentials that should be used to send outbound messages
EMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_URL = "https://alphavantage.co/query"

NEWSAPI_API_KEY = os.environ.get("NEWSAPI_API_KEY")
NEWSAPI_URL_EVERYTHING = "https://newsapi.org/v2/everything"
TOP_N_ARTICLES = 3

# When STOCK price increase/decreases by percent_change between yesterday and the day before yesterday then send email
percent_change = .01

# get the current date
time_now = dt.datetime.now()
print(f"{time_now.year}-{time_now.month}-{time_now.day}")

# get the stock information
stock_request_params = {"apikey": ALPHAVANTAGE_API_KEY, "function": "TIME_SERIES_DAILY", "symbol": STOCK }
stock_request_response = requests.get(url=ALPHAVANTAGE_URL, params=stock_request_params)
stock_request_response.raise_for_status()
stock_data = stock_request_response.json()
print(stock_data)

# get the price for yesterday
yesterday = time_now - timedelta(days=1)
yesterday_data = stock_data['Time Series (Daily)'][yesterday.strftime("%Y-%m-%d")]
yesterday_close = float(yesterday_data['4. close'])
print(yesterday_close)

# get the price before yesterday
day_before_yesterday = time_now - timedelta(days=2)
day_before_yesterday_data = stock_data['Time Series (Daily)'][day_before_yesterday.strftime("%Y-%m-%d")]
day_before_yesterday_close = float(day_before_yesterday_data['4. close'])
print(day_before_yesterday_close)

# determine if there was a +/- 5% difference in price between the prior two days
difference_in_price = yesterday_close - day_before_yesterday_close
difference_in_percent = difference_in_price / day_before_yesterday_close
big_price_difference_for_email = abs(difference_in_percent) >= percent_change
difference_in_percent_printable = float(int(difference_in_percent * 1000) / 10)
print(big_price_difference_for_email)
print(difference_in_percent)

# get the trending articles for the stock
newsapi_request_params = { "apiKey": NEWSAPI_API_KEY, "q": STOCK, "from": day_before_yesterday.strftime("%Y-%m-%d"), "language": "en", "pageSize": TOP_N_ARTICLES, }
newsapi_response = requests.get(url=NEWSAPI_URL_EVERYTHING, params=newsapi_request_params)
newsapi_response.raise_for_status()
news_stock = newsapi_response.json()
news_stock_articles = news_stock['articles']
message_body = ""
for article in news_stock_articles:
    title = article['title'].encode('unicode_escape')
    description = article['description'].encode('unicode_escape')
    url = article['url'].encode('unicode_escape')
    message_body += f"Headline: {title}\nBrief:\n{description}\nurl: {url}\n\n"

# send an email with the stock change
if big_price_difference_for_email:
    print("there is a big price difference, sending email...")
    print(f"{difference_in_percent_printable}% in {COMPANY_NAME} ({STOCK}))")
    print(message_body)
    email = email_account.EmailAccount(my_email=EMAIL_ADDRESS, my_password=EMAIL_PASSWORD)
    response = email.send_email(
       to_address="earthmabus@hotmail.com",
       subject=f"{difference_in_percent}% in {COMPANY_NAME} ({STOCK})",
       message=message_body)
    print(response)
