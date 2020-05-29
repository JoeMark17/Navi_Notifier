# Navi-Alerts TimerTrigger -Python

The `Navi-Alerts` Azure Function runs every 15 minutes between the hours of 9:30am and 4:00pm (Central Time) during the weekdays (sans holidays) and sends a text message to specified user if their interested stocks have risen ABOVE or fallen BELOW their predefined thresholds. For an example of what the message looks like, see below:

```
Hey, Listen! 
There have been stock changes as of (05-29-20 16:06:45)!

MSFT - has fallen BELOW your threshold of $190,

VOO - has risen ABOVE your threshold of $150
```

## How it works
The `Navi-Alerts` works by using the code within the _init_.py file to query an Azure PostgresDB and obtain user information. The PostgresDB contains users name, phone number, carrier information, stocks they are interested in, and a high/low threshold for each stock. The python script then uses that information to call yfinance for the stock information. Then based off the day the python script iterates through each user and sends and email if the stock has risen or fallen from their predefined thresholds. In addition, the script is set to update the PostgresDB if the stock price changes. See below for the changes when the stock goes ABOVE and BELOW the threshold:

```
ABOVE = (SET "Stock-High" = ("Stock-High" * 1.10) )
BELOW = (SET "Stock-Low" = ("Stock-Low" * .90) )
```
