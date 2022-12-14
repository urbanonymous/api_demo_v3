# api_demo_v3

This repo contains a web app that provides liquidity to Binance trading pairs.

It connects to Binance's API to gather information related to some symbols, and then it creates buy and sell orders in the testnet of Binance based on some parameters.

The web displays the current orders, ticker, balances from an account.
The tickers are updated once those are activated (run button) up to 2 times per second.

The data is updated using websockets, from the website to the internal API.
Only tickers and orders are updated for not. The balances are only updated on a refresh.

The internal API is connected to Binance by websocket to get real-time price information.
It subscribes to some market symbols and then ingests the newest price to an internal liquidity engine.

This liquidity engine basically checks if there are orders in place for a given symbol, if not, it creates a buy and sell order in the testnet of Binance.

It also checks the trading pair price, and compares it to the orders placed, to cancel and create new orders if necessary.

All the pending orders for the trading pairs are cancelled/cleaned once the api is stopped and also on startup.

The web is made with vanilla Javascript, Tailwind CSS and DaisyUI

Internally, the API uses FastAPI, jinja2, websockets and aiohttp.


The app is hardcoded to only use BTC, BUSD and USDT and the pairs BTCBUSD and BTCUSDT.

## TODO

- Update account balances using websocket
- Update orders status using websocket


## Improvements

- Add OCO, Iceberg, Invisible and other order types
- Add logic related to order size and balances
- Allow configuration from the web
- Initialize table of orders in frontend and only send updates instead of full table
- Add a rebalance option for trading pair (mantain close to 50%/50% each asset)
- Add tests...

## Notes related to Binance API

- Some ENUM fields are not populated/documented
- The testnet fails sometimes due to "-1007 timeouts" and 502 Bad Gateway, this seems to be caused by testnet resets/maintenance.


## Requirements

- Linux/osx machine (for the makefiles)
- Docker/Docker compose

## Development

Clone the repo in a linux/osx machine and execute the following commands:

To build the docker image user `make build`

Create a new file inside /docker with the name local.env and add the Binance testnet API keys. Follow the local.env.template.
 
To start the API in development mode use `make develop`

To attach to the running api use `make attach`
When attached:
- To detach use `control+d`
- To stop the API use `control+c`

To just watch the logs without being attached use `make logs`

The URL to view the web is `http://localhost:9001`

You can also check the API openapi docs at `http://localhost:9001/docs/`

To execute the tests use `make unit-test`

To reformat the code use `make reformat`

To check the linting of the code use `make lint`