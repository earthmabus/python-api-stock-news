import os
from stock import Stock
import email_account

# load in the email account credentials that should be used to send outbound messages
EMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

# construct a list of stocks that we're interested in
Stocks = [
    Stock("TSLA", "Telsa Inc", .03),
    Stock("INTC", "Intel", .001)
]

# construct a subject that contains all     the stocks over
# construct a message body with news articles for each stock over
complete_subject = ""
complete_message = ""
for stock in Stocks:
    # is the stock over our reporting threshold?
    over_threshold = stock.get_stock_data_if_big_change()
    if over_threshold is not None:
        # yes, the stock is over the reporting threshold

        # append the stock name and % change to the complete_subject
        if complete_subject != "":
            complete_subject += ", "
        complete_subject += f"{stock.m_stock} ({over_threshold['actual_percent_diff']}%)"

        # append a "header" and news articles to complete_message
        if complete_message != "":
            complete_message += "\n\n"
        complete_message += f"{stock.m_company_name} ({stock.m_stock}) changed by {over_threshold['actual_percent_diff']}%\n\n{over_threshold['articles']}"

# if there was at least one stock crossed its threshold, then send out an email
if complete_message != "":
    email = email_account.EmailAccount(my_email=EMAIL_ADDRESS, my_password=EMAIL_PASSWORD)
    response = email.send_email(
        to_address="earthmabus@hotmail.com",
        subject=complete_subject,
        message=complete_message)
    print(f"successfully sent email with subject {complete_subject}")
