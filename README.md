# api_demo_v3

Demo API + webapp, that provides liquidity to a Binance trading pair.

It connects to Binance's API to gather information related to a trading pair.

Then it creates buy and sell orders in the testnet of Binance to provide liquidity to the market.

The portal displays the current orders, ticker, balances from an account.

The data is updated by websocket from the website to the internal API.
The internal API is connected to Binance by websocket to get realtime price information.

The web is made with Tailwind CSS and daisyUI

Internally, the API uses FastAPI, jinja2, websockets and aiohttp.

When the API starts, it executes a cleanup, closing all the open orders in the testnet.

The app is hardcoded to only use BTC, BUSD and USDT.

## TODO

- Account balances updated by websocket
- Orders status updated by websocket

## Requirements

- Linux/osx machine (for the makefiles)
- Docker/Docker compose

## Development

Clone the repo in a linux/osx machine and execute the following commands:

To build the docker image user `make build`

To start the api in development mode use `make develop`

To attach to the running api use `make attach`
When attached:
- To detach use `control+d`
- To stop the api use `control+c`

To just watch the logs without being attached use `make logs`

To execute the tests use `make unit-test`

To reformat the code use `make reformat`

To check linting of the code use `make lint`
