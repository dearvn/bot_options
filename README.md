# bot_options
The bot is ideal for traders looking to reduce the amount of time spent on researching and analyzing the markets, as it can quickly scan for and identify the most profitable trades. 

My account less than $25K so I can't buy sell many time in a day, I use this way that I can trade many times on Tradovate


Everyday, can entry 2 orders and gain profit at leat 40%.

Cost to set up an options bot: a vps

My logic is simple and easy to auto trading on TDA.

```
Buy to Open Call Strike $404 Expiration 3/7   ...... + $500

to lock

Sell to Open Call Strike $405 Expiration 3/7


==============================================================

Buy to Open Put Strike $400 Expiration 3/7 ..... $300

to Lock

Sell to Open Put Strike $399 Expiration 3/7


==============================================================

Buy to Open Put Strike $402 Expiration 3/8 (Market) @ 1.00
Set Stop Loss 0.80

Lock when Option $ = 1.80

Sell to Open Put Strike $401 Expiration 3/8 (Market)

```

## Install
# Backend

1. Get refresh token from TD Ameritrade ref https://www.youtube.com/watch?v=aT1nB-vMqdE
2. Update params in env.env file:
   ```bash
  TDAMERITRADE_ACCOUNT_ID=
  
  TDAMERITRADE_CLIENT_ID=
  
  TDAMERITRADE_REFRESH_TOKEN=
   ```
4. Update refresh_token in /app/worker/token.pickle too:

```bash
{"creation_timestamp": 1684423154, "token": {"access_token": "xxxxx", "refresh_token": "", "scope": "PlaceTrades AccountAccess MoveMoney", "expires_in": 1800, "refresh_token_expires_in": 7776000, "token_type": "Bearer", "expires_at": 1684424954}}
```

5. Go to backend folder run docker

```bash

docker-compose build

docker-compose up -d

docker exec -i -t stock_app_1  /bin/bash

nohup python manage.py runserver 0.0.0.0:8000

```  


*Frontend

Currently, I am using Laravel to host Frontend UI to connect with backend.


![Alt text](https://github.com/dearvn/bot_options/raw/main/SPY-20230413.png?raw=true "SPY")

Setting logic

![Alt text](https://github.com/dearvn/bot_options/raw/main/Settings.png?raw=true "Setting")

Orders

![Alt text](https://github.com/dearvn/bot_options/raw/main/Orders.png?raw=true "Order")

