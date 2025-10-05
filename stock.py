import os
import datetime as dt
import requests

ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_URL = "https://alphavantage.co/query"

NEWSAPI_API_KEY = os.environ.get("NEWSAPI_API_KEY")
NEWSAPI_URL_EVERYTHING = "https://newsapi.org/v2/everything"

TOP_N_ARTICLES = 3

class Stock:

    def __init__(self, stock, company_name, threshold):
        self.m_stock = stock
        self.m_company_name = company_name
        self.m_threshold = threshold

        # get the current date
        self.m_time_now = dt.datetime.now()

    def get_stock_data_if_big_change(self):
        # get the stock information
        stock_request_params = {"apikey": ALPHAVANTAGE_API_KEY, "function": "TIME_SERIES_DAILY", "symbol": self.m_stock}
        stock_request_response = requests.get(url=ALPHAVANTAGE_URL, params=stock_request_params)
        stock_request_response.raise_for_status()
        stock_data = stock_request_response.json()
        # print(stock_data)

        # get the price for yesterday
        yesterday = self.m_time_now - dt.timedelta(days=1)
        yesterday_data = stock_data['Time Series (Daily)'][yesterday.strftime("%Y-%m-%d")]
        yesterday_close = float(yesterday_data['4. close'])
        # print(yesterday_close)

        # get the price before yesterday
        day_before_yesterday = self.m_time_now - dt.timedelta(days=2)
        day_before_yesterday_data = stock_data['Time Series (Daily)'][day_before_yesterday.strftime("%Y-%m-%d")]
        day_before_yesterday_close = float(day_before_yesterday_data['4. close'])
        # print(day_before_yesterday_close)

        # determine if there was a +/- m_threshold % difference in price between the prior two days
        difference_in_price = yesterday_close - day_before_yesterday_close
        difference_in_percent = difference_in_price / day_before_yesterday_close
        #print (f"difference_in_percent: {difference_in_percent}")
        #print (f"m_threshold: {self.m_threshold}")
        big_price_difference_for_email = abs(difference_in_percent) >= self.m_threshold
        #print(f"big_price_difference_for_email: {big_price_difference_for_email}")
        difference_in_percent_printable = float(int(difference_in_percent * 1000) / 10)

        # get the trending articles for the stock
        newsapi_request_params = {"apiKey": NEWSAPI_API_KEY, "q": self.m_stock,
                                  "from": day_before_yesterday.strftime("%Y-%m-%d"), "language": "en",
                                  "pageSize": TOP_N_ARTICLES, }
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

        # construct a return value consisting of the actual % change and related news articles
        retval = None
        if big_price_difference_for_email:
            #print("there is a big price difference, sending email...")
            #print(f"{difference_in_percent_printable}% in {self.m_company_name} ({self.m_stock}))")
            #print(message_body)
            retval = {
                "actual_percent_diff": difference_in_percent_printable,
                "articles": message_body
            }

        return retval