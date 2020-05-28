#import datetime
import logging
import psycopg2
import smtplib
import yfinance as yf

import azure.functions as func
from datetime import datetime, timedelta
#from datetime import timedelta

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.today()
   # print('Hello')
    def stock():
        #################################################################################################
        # Below is defining stock market holidays and days of the week to get previous stock quotes.
        offday = ['01-01-20', '01-20-20', '02-17-20', '04-10-20', '05-25-20', '07-03-20', '09-07-20', '11-26-20', '12-25-20']

        # Define datetime for today and yesterday (or holidays/weekends) to get change in stock.
        today = datetime.today()
        yesterday = datetime.today() - timedelta(1)
        holiday = datetime.today() - timedelta(2)
        friday = datetime.today() - timedelta(3)
        holimonday = datetime.today() - timedelta(4)
        #################################################################################################
        # Below is establishing connection to Postgres DB and executing select queries.
        stock_dict = {}

        con = psycopg2.connect(
            host='naviserver.postgres.database.azure.com',
            database='Navi',
            user='naviadmin@naviserver',
            password='v!z&jKP4Pxi2llnl',
            port='5432')

        cur = con.cursor()

        user_call = (
            'SELECT CONCAT(U."NotifierString",EC."EC-String") as "NotifierString", S."Stock", S."Stock-Low", S."Stock-High" '
            'FROM Public."Stocks" S '
            'INNER JOIN Public."Users" U ON U."UserID" = S."UserID" '
            'INNER JOIN Public."EmailCarrier" EC ON EC."Email-Carrier" = U."Email-Carrier" '
            ## 'WHERE U."UserID" = 1 ORDER BY U."UserID" ASC;')
            'WHERE U."ActiveFlag" = \'Y\' ORDER BY U."UserID" ASC;')

        stock_ticker = ('SELECT DISTINCT S."Stock" FROM Public."Stocks" S;')

        cur.execute(user_call)
        user = cur.fetchall()
        #print(user)

        cur.execute(stock_ticker)
        tick = cur.fetchall()

        for column in user:
            if column[0] in stock_dict:
                stock_dict[column[0]][column[1]] = (column[2], column[3])
            else:
                stock_dict[column[0]] = {column[1]: (column[2], column[3])}

        # Below creates the stock list from the second select statement.
        ticker = [row[0] for row in tick]
        
        #print(ticker)
    
        # If statements to execute based off what type of day .today() is.
        #if yesterday.strftime('%m-%d-%y') in offday and yesterday.weekday() == 0:
        
        stock_live = {i: float(round(yf.download(i,today,today)['Adj Close'].iloc[0],2))for i in ticker}
        stock_prev = {i: float(round(yf.download(i,yesterday,today)['Adj Close'].iloc[0], 2)) for i in ticker}

        #print(stock_live)
        #print(stock_prev)

        for stock_integer in stock_dict:
            for actual in stock_dict[stock_integer]:
                stock_dict[stock_integer][actual] = (stock_live.get(actual), stock_prev.get(actual))

        for u, s in stock_dict.items():
            usernumber = u
            result = []
            for tick, price in s.items():
                stock = tick  # stock ticker
                stock_cur = price[0]  # todays stock price
                stock_previ = price[1]  # yesterdays stock price

                # Calculating change in stock price from yesterday
                stock_net = float(round((stock_cur - stock_previ), 2))
                stock_change = float((stock_cur - stock_previ) / stock_previ)
                stock_percent = format(stock_change, '.2%')

                # Creating a final message to be displayed in the email regarding each stock listed in the for loop
                stock_message = '\n\n' + stock + ' = $' + str(round(stock_cur, 2)) + ' | $' + str(stock_net) + ' ' + str(stock_percent) + ' from prev close'

                # Added the .append so each iteration of the for loop is included in the 'result' list at the beg of the function.
                result.append(stock_message)

                # Below removes the brackets and quotes that would otherwise be included in returning a list.
                finalstock = (', '.join(result))

            # Defing the mail service I am using. In this case it is gmail.
            mail = smtplib.SMTP('smtp.gmail.com',587)

            # Starting the logic for smtplib mail to send the information using my gmail to my phone.
            mail.ehlo()
            mail.starttls()
            mail.login('navi.notify@gmail.com', 'ed9UklZF#Em4C9KI')
            # Below (TO) sender pulls from the SQL statement at the begin of the for loop, and the finalstock is pulled from the inner loop

            message = 'Hey, Listen! Your interested stock price values for today (' + today.strftime('%m-%d-%y') + ') are...' + str(finalstock)
            mail.sendmail('navi.notify@gmail.com', usernumber, str(message))

            mail.close()

        print(message)
    stock()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Hey, Listen! The Python timer trigger function ran at %s', utc_timestamp)


#stock()