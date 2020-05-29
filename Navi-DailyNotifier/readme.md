# Navi-DailyNotifier TimerTrigger -Python

The `Navi-DailyNotifier` Azure Function runs each weekday morning (sans holidays) at 4:00pm (Cental Time) and sends a text message to specified users of stock price and changes which they are interested in. For an example of what the message looks like, see below:

```
Hey, Listen! 
Your interested stock price values for today (05-26-20) are...

MSFT = $185.27 | $-1.39 -0.75% from prev close,
VOO = $276.31 | $3.41 !.25% from prev close
```

## How it works
The `Navi-DailyNotifier` works by using the code within the _init_.py file to query an Azure PostgresDB and obtain user information. The PostgresDB contains users name, phone number, carrier information, and the stocks they are interested in. The python script then uses that information to call yfinance for the stock information. Then based off the day the python script iterates through each user and sends and email with the price of the stock as of $:00pm and also the changes in price and percentage from previous close.

