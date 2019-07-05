# -*- coding: utf-8 -*-
from ybmex_websocket import ybmexWebsocket
import logging
import time


# Basic use of websocket.
def run():
    logger = setup_logger()

    # Instantiating the WS will make it connect. Be sure to add your api_key/api_secret.
    # API Key and API Secret modified by chaiyu
    ws = ybmexWebsocket(endpoint="wss://www.ybmex.com/realtime", symbol="XBTUSD",
                         api_key="u_api_key", api_secret="u_api_secret")
    logger.info("Instrument data: %s" % ws.get_instrument())

    # Run forever
    while (ws.ws.sock.connected):
        # logger.info("Ticker: %s" % ws.get_ticker())
        # if ws.api_key:
        #     logger.info("Funds: %s" % ws.funds())
        logger.info("Market Depth: %s" % ws.market_depth())
        logger.info("Recent Trades: %s\n\n" % ws.recent_trades())
        time.sleep(2)

def setup_logger():
    # Prints logger info to terminal
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

if __name__ == "__main__":
    run()
