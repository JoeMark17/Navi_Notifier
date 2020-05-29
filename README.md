# Navi_Notifier
"Hey Listen!" Navi is a project centered around stock management. Are you new to investing on your own, do you wish you could be notified each morning on the status of your investments, do you wish an alert was sent to your mobile device if a stock dropped or rose a certain percentage or dollar amount? Well then this application is the one for you. Navi is intended to be used for all notifications related to user specified stocks. Navi is a passion project built from my own frustration with managing stocks. I hope the end product will help you in your investment journey. [In-Progress]

# How it works
I leverage two Azure Functions currently to execute the python scripts. One in the morning, and one in the afternoon on Weekdays. In addition to Azure Functions, I leverage an Azure PostgresDB which contains user information which the python script calls from.
