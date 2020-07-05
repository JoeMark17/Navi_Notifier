import logging
import psycopg2
import smtplib
import yfinance as yf

import azure.functions as func
from datetime import datetime, timedelta

navihost='{navihost}'
navidb='{navidb}'
naviuser='{naviuser}'
navipwd='{navipwd}'
naviport='{naviport}'
navimail='{navimail}'
navimailpwd='{navimailpwd}'

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.today()
    def stockstest():
        #################################################################################################
        offday = ['07-03-20', '09-07-20', '11-26-20', '12-25-20']

        #Define datetime for today and yesterday (or holidays/weekends) to get change in stock
        today = datetime.today()
        yesterday = datetime.today() - timedelta(1)
        holiday = datetime.today() - timedelta(2)
        friday = datetime.today() - timedelta(3)
        holimonday = datetime.today() - timedelta(4)
        ################################################################################################# 

        stock_dict = {}

        con = psycopg2.connect(
            host = navihost,
            database = navidb,
            user = naviuser,
            password = navipwd,
            port = naviport)
        cur = con.cursor()

        user_call = (
                'SELECT U."id", CONCAT(U."NotifierString",EC."ECString") as "NotifierString", S."Stock", S."StockLow", S."StockHigh" '
                'FROM Public."accounts_stocks" S '
                'LEFT JOIN Public."accounts_users_dj" U ON U."id" = S."User_id" '
                'LEFT JOIN Public."accounts_emailcarrier" EC ON EC."EmailCarrier" = U."EmailCarrier" '
                'WHERE U."ActiveFlag" = \'Y\' ORDER BY U."id" ASC;')

        stock_ticker = ('SELECT DISTINCT S."Stock" FROM Public."accounts_stocks" S;')

        cur.execute(user_call)
        user = cur.fetchall()

        cur.execute(stock_ticker)
        tick = cur.fetchall()
        
        ticker = [row[0] for row in tick]
        stock_live = {i: float(round(yf.download(i,today,today)['Adj Close'].iloc[0],2))for i in ticker}
        
        for column in user:
            if column[0] in stock_dict:
                stock_dict[column[0]][column[1]][column[2]] = (column[3], column[4], float(stock_live.get(column[2])))
            else:
                stock_dict[column[0]] = {column[1]: {column[2]: (column[3], column[4], float(stock_live.get(column[2])))}}

        for key, user in stock_dict.items():
            userid = key
            
            for number, stock_info in user.items():
                usernumber = number
                alerts = []
                
                for ticker, price in stock_info.items():
                    stock = ticker

                    user_low = round(price[0],2)
                    user_high = round(price[1],2)
                    stock_live = round(price[2],2)
                    
                    if stock_live < user_low: 
                        cur = con.cursor()
                        ##Multiply the stock_low by .95 so the database can dynamically change the low threshold when it is met.
                        low_insert_command = 'UPDATE public."accounts_stocks" SET "StockLow" = ("StockLow" * .95) '
                        'WHERE "User_id" ='+ str(userid) +' and "Stock" = \''+ str(stock) + '\';'
                        cur.execute(low_insert_command)
                        con.commit()
                        
                        alert_low_message = '\n\n' + str(stock) + ' - has fallen BELOW your threshold of $' + str(user_low)
                        alerts.append(alert_low_message)
                        
                        final_alert = (', '.join(alerts))
                        cur.close()

                    elif stock_live > user_high:
                        cur = con.cursor()
                        ##Multiply the stock_low by 1.05 so the database can dynamically change the high threshold when it is met.
                        high_insert_command = 'UPDATE public."accounts_stocks" SET "StockHigh" = ("StockHigh" * 1.05) '
                        'WHERE "User_id" ='+ str(userid) +' and "Stock" = \''+ str(stock) + '\';'
                        cur.execute(high_insert_command)
                        con.commit()
                        
                        alert_low_message = '\n\n' + str(stock) + ' - has risen ABOVE your threshold of $' + str(user_high)
                        alerts.append(alert_low_message)

                        final_alert = (', '.join(alerts))
                        cur.close()

                    else:
                        pass

                    final_alert = (', '.join(alerts))

                if(len(final_alert) == 0): 
                    pass
                else:
                    mail = smtplib.SMTP('smtp.gmail.com',587)

                    # Starting the logic for smtplib mail to send the information using my gmail to my phone.
                    mail.ehlo()
                    mail.starttls()
                    mail.login(navimail, navimailpwd)
                    # Below (TO) sender pulls from the SQL statement at the begin of the for loop, and the finalstock is pulled from the inner loop

                    message = 'Hey, Listen! \n\nThere have been stock changes as of (' + today.strftime('%m-%d-%y %X') + ')!\n' + str(final_alert)

                    try:
                        mail.sendmail(navimail, usernumber, str(message))
                    except:
                        pass

                    mail.close()

    stockstest()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Hey, Listen! Python timer trigger function ran at %s', utc_timestamp)
