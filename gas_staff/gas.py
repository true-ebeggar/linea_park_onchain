import time
import requests
from loguru import logger

from linea_park_onchain.config import *
from linea_park_onchain.headers.headers import lineascan_headers


def gas_gate():
    start_time = time.time()
    while True:
        try:
            response = requests.get('https://glinea.blockscan.com/gasapi.ashx?apikey=key&method=gasoracle',
                                    headers=lineascan_headers())
            gas_data = response.json()
            proposed_gas_price = float(gas_data['result']['ProposeGasPrice'])
            price = float(gas_data['result']['UsdPrice'])
            if proposed_gas_price <= MAX_GAS:
                logger.success(f"gas: {proposed_gas_price} < {MAX_GAS} Eth price - {round(price, 2)}")
                return proposed_gas_price
            else:
                logger.error(f"gas: {proposed_gas_price} > {MAX_GAS} Eth price - {round(price, 2)}")
        except Exception:
            pass

        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            logger.warning("unable to get gas after 1 minute.")
            return None

        time.sleep(1)


def get_gas():
    start_time = time.time()
    while True:
        try:
            response = requests.get('https://glinea.blockscan.com/gasapi.ashx?apikey=key&method=gasoracle',
                                    headers=lineascan_headers())
            gas_data = response.json()
            proposed_gas_price = float(gas_data['result']['ProposeGasPrice'])
            return proposed_gas_price
        except Exception:
            pass

        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            logger.warning("unable to get gas after 1 minute.")
            return None

        time.sleep(1)
