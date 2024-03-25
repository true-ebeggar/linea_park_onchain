import time
from web3 import Web3
from loguru import logger
from linea_park_onchain.config import *
from linea_park_onchain.blockchain_data import blockchain_data


def gas_gate():
    while True:
        try:
            w3 = Web3(Web3.HTTPProvider(blockchain_data.linea.rpc))
            gas_price = w3.eth.gas_price
            proposed_gas_price = gas_price / 1e9
            if proposed_gas_price <= MAX_GAS:
                logger.success(f"gas: {proposed_gas_price} < {MAX_GAS}")
                return proposed_gas_price
            else:
                logger.error(f"gas: {proposed_gas_price} > {MAX_GAS}, sleep...")
        except Exception:
            time.sleep(1)
            pass
        time.sleep(30)


def get_gas():
    start_time = time.time()
    while True:
        try:
            w3 = Web3(Web3.HTTPProvider(blockchain_data.linea.rpc))
            gas_price = w3.eth.gas_price
            proposed_gas_price = gas_price / 1e9
            return proposed_gas_price
        except Exception:
            time.sleep(1)
            pass
        elapsed_time = time.time() - start_time
        if elapsed_time >= 60:
            logger.warning("unable to get gas after 60-sec.")
            return None
        time.sleep(1)
