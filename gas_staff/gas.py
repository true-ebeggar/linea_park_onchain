import time
import requests
from loguru import logger

from linea_park_onchain.config import *
from linea_park_onchain.headers.headers import lineascan_headers


def gas_gate():
    attempt = 0
    while True:
        try:
            response = requests.get('https://glinea.blockscan.com/gasapi.ashx?apikey=key&method=gasoracle',
                                    headers=lineascan_headers())
            gas_data = response.json()
            proposed_gas_price = float(gas_data['result']['ProposeGasPrice'])
            price = float(gas_data['result']['UsdPrice'])
            attempt = 0

            if proposed_gas_price <= MAX_GAS:
                logger.success(f"gas: {proposed_gas_price} < {MAX_GAS} Eth price - {round(price, 2)}")
                break
            else:
                logger.error(f"gas: {proposed_gas_price} > {MAX_GAS} Eth price - {round(price, 2)}")
                time.sleep(40)
        except Exception as e:
            attempt += 1
            if attempt == 10:
                logger.critical(f"error after {attempt} consecutive attempts"
                                f"\n{e}")
            time.sleep(1)


def get_gas():
    while True:
        try:
            response = requests.get('https://glinea.blockscan.com/gasapi.ashx?apikey=key&method=gasoracle',
                                    headers=lineascan_headers())
            gas_data = response.json()
            proposed_gas_price = float(gas_data['result']['ProposeGasPrice'])
            return proposed_gas_price
        except Exception as Error:
            logger.error(Error)
            time.sleep(2)
