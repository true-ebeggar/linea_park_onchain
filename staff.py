import random
import string
import datetime

import json
from html.parser import HTMLParser
from web3 import Web3, HTTPProvider
from eth_account import Account

from blockchain_data.blockchain_data import linea
from gas_staff.gas import *


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.numbers = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'data-test' and attr[1] == 'token_link':
                    self.capture = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.capture:
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            number = ''.join(filter(str.isdigit, data))
            if len(number) == 6:
                self.numbers.append(int(number))


class LineaTxnManager:
    def __init__(self, key, proxy=None):
        self.private_key = key
        self.session = requests.Session()
        if proxy:
            credentials, ip_port = proxy.split('@')
            self.session.proxies = {
                "http": f"http://{credentials}@{ip_port}",
                "https": f"http://{credentials}@{ip_port}"
            }
        self.w3 = Web3(HTTPProvider(linea.rpc))
        self.w3.provider = HTTPProvider(linea.rpc, session=self.session)
        self.account = Account.from_key(key)
        self.address = self.account.address

    def _submit_and_log_transaction(self, txn):
        try:
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
            txn_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash, timeout=120)
            if receipt['status'] == 1:
                logger.success(f"Txn completed: {linea.scan}{txn_hash.hex()}")
                return 1
            else:
                logger.warning(f"Txn unsuccessful: {linea.scan}{txn_hash.hex()}")
                return 0
        except Exception as e:
            logger.critical(f"Error while making txn for wallet {self.address}: \n{e}")
            return 0

    def _get_memory_card_id(self, max_retry=3):
        retry_count = 0
        while retry_count < max_retry:
            try:
                response = requests.get(url=f'https://explorer.linea.build/address/{self.address}/tokens/'
                                            f'{pictograph_contract}/token-transfers?type=JSON',
                                        proxies=self.session.proxies)
                if response.status_code == 200:
                    data = response.json()
                    html_content = data["items"][0]
                    parser = MyHTMLParser()
                    parser.feed(html_content)
                    if parser.numbers:
                        logger.info(f"Memory card ID: {parser.numbers[0]}")
                        return parser.numbers[0]
                    else:
                        return None
                else:
                    logger.error(f"Unexpected response structure while checking NFT-id."
                                      f"\nResponse: {response.text}")
                    return None
            except Exception as e:
                logger.critical(f"Exception during checking NFT-id."
                                     f"\nException: {e}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying in 10 seconds... (Attempt {retry_count}/{MAX_RETRIES})")
                    time.sleep(10)
                else:
                    logger.critical("Max retries reached. Failed to get memory card ID.")
                    return None

    def _get_txn_data_gamic(self):
        retry_count = 0

        while retry_count < MAX_RETRIES:
            try:
                now = datetime.datetime.now()
                future_time = now + datetime.timedelta(minutes=3)
                future_timestamp = int(time.mktime(future_time.timetuple()))

                token_list = [
                    '0x5471ea8f739dd37E9B81Be9c5c77754D8AA953E4',
                    '0xf5C6825015280CdfD0b56903F9F8B5A2233476F5',
                ]

                token = random.choice(token_list)
                eth = random.uniform(0.00005, 0.00015)
                amount = self.w3.to_wei(eth, 'ether')

                url = ('https://api.dodoex.io/route-service/v2/widget/getdodoroute?chainId=59144'
                       f'&deadLine={future_timestamp}'
                       f'&apikey=f78ebf46796fca2a5c'
                       f'&slippage=2.0'
                       f'&source=dodoV2AndMixWasm'
                       f'&toTokenAddress={token}'
                       f'&fromTokenAddress=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
                       f'&userAddr={self.address}'
                       f'&estimateGas=true'
                       f'&fromAmount={amount}')

                response = requests.get(url=url, proxies=self.session.proxies)
                json_data = response.json()
                data = json_data['data']['data']
                gas_limit = json_data['data']['gasLimit']
                to = json_data['data']['to']
                value = int(json_data['data']['value'])
                d = self.w3.from_wei(value, 'ether')

                if len(data) == 1610:
                    logger.success(f'Receive txn data: swap-to-token {token}, '
                                   f'Amount {d} ETH')
                    return data, gas_limit, value, to
                else:
                    raise ValueError("Data length does not match the desired format.")

            except (KeyError, ValueError) as e:
                retry_count += 1
                logger.warning(f"Retry {retry_count}/{MAX_RETRIES}: {str(e)}")
                time.sleep(3)

        logger.critical(f"Could not retrieve data after {MAX_RETRIES} retries")
        return None, None, None, None

    def bit_avatar_wrap(self):
        if self.mint_bit_avatar() == 1:
            return self.check_in_bit_avatar()
        else:
            return 0

    def read_on_curate(self):
        min_value = 10 ** (19 - 1)
        max_value = (10 ** 19) - 1
        random_number = random.randint(min_value, max_value)

        try:
            contract_address = self.w3.to_checksum_address(read_on_contract)
            with open('ABI/read_on.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(60000, 80000)
            txn = contract.functions.curate(random_number).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def pictograph_wrap(self):
        code = self._get_memory_card_id(max_retry=1)
        if code is not None:
            return self.stake_pictograph_memory_card(code)
        else:
            if self.mint_pictograph_memory_card() == 1:
                return self.stake_pictograph_memory_card(code)
            else:
                return 0

    def mint_pictograph_memory_card(self):
        try:
            contract_address = self.w3.to_checksum_address(pictograph_contract)
            with open('ABI/pictographs.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 340000)
            txn = contract.functions.mintNFT().build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def stake_pictograph_memory_card(self, card_id=None):
        if card_id is None:
            logger.info("Waiting a bit, for txn to index...")
            time.sleep(30)
            logger.info("Attempt to find memory card ID")
            card_id = self._get_memory_card_id()
        try:
            contract_address = self.w3.to_checksum_address(pictograph_contract)
            with open('ABI/pictographs.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 340000)
            txn = contract.functions.stake(card_id).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_genesis_proof(self):
        try:
            contract_address = self.w3.to_checksum_address(genesis_proof_contract)
            with open('ABI/genesis_proof.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(50000, 80000)
            txn = contract.functions.signGenesisProof().build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_tanuki_nft(self):
        eth = 0.0001
        wei = self.w3.to_wei(eth, 'ether')
        gas = random.randint(350000, 400000)
        data = '0xefef39a10000000000000000000000000000000000000000000000000000000000000001'
        gasPrice = 1
        try:
            txn = {
                'to': self.w3.to_checksum_address(tanuki_linea_park_contract),
                'value': wei,
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gasPrice, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint2048(self):
        function_selector = "0x36ab86c4"
        example = "09867bc044d0cb8657a0e60be15868d905f6a5c35edc810cef5facd58327a62c"
        symbols = set(example)
        generated_string = ''.join(random.choice(list(symbols)) for _ in range(len(example)))
        argument2 = '0000000000000000000000000000000000000000000000000000000000000001'
        data = function_selector + generated_string + argument2

        gas = random.randint(300000, 350000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(game_2048_contract),
                'value': 0,
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_bit_avatar(self):
        code = ''.join(random.choice(string.hexdigits) for _ in range(24))
        url = f"https://api.bitavatar.io/v1/avatar/{code}"
        encoded_url = url.encode('utf-8').hex()

        padding_length = (32 - len(encoded_url)) % 32
        encoded_url += '0' * padding_length

        encoded_data = '0xd85d3d27'
        encoded_data += '0000000000000000000000000000000000000000000000000000000000000020'
        encoded_data += f'{len(url):064x}'
        encoded_data += encoded_url
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(bit_avatar_contract),
                'value': 0,
                'gas': 500000,
                'data': encoded_data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def check_in_yooldo(self):
        data = "0xfb89f3b1"
        gas = random.randint(35000, 50000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(check_in_yooldo_contract),
                'value': int(self.w3.to_wei(0.000002, 'ether')),
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def yooldo_wallpaper_A(self):
        part1 = "0xa20a3252"
        part3 = "000000000000000000000000000000000000000000000000000000000000"
        value = format(random.randint(0, 0xFFFF), '04x')
        data = part1 + value + part3

        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address('0xf5b709c209c3ba5e837d517bb2719e3d2da76629'),
                'value': 0,
                'gas': random.randint(300000, 350000),
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def check_in_bit_avatar(self):
        data = '0x183ff085'
        gas = random.randint(35000, 50000)

        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(bit_avatar_contract),
                'value': 0,
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def send_dmail_message(self):
        variable = ''.join(random.choices('0123456789abcdef', k=64))
        try:
            contract_address = self.w3.to_checksum_address(dmail_contract)
            with open('ABI/dmail.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(50000, 80000)
            txn = contract.functions.send_mail(variable, variable).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def swap_on_gamic_dex(self):
        data, gas_limit, value, to = self._get_txn_data_gamic()

        if data is None or gas_limit is None or value is None or to is None:
            logger.error("Some data is not received from gamic api, no txn will be made")
            return 0

        gas_price = get_gas()

        try:
            txn = {
                'to': to,
                'value': int(value),
                'gas': gas_limit,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            logger.info('Txn data are send to blockchain')
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_emerald_enchanted_key(self):
        try:
            contract_address = self.w3.to_checksum_address(EE_key_contract)
            with open('ABI/EE_key.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 400000)
            txn = contract.functions.purchase(1).build_transaction({
                'value': int(self.w3.to_wei(0.0001, 'ether')),
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def adopt_cat_call(self):
        try:
            contract_address = self.w3.to_checksum_address(adopt_cat)
            with open('ABI/lottery_master.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(150000, 200000)
            txn = contract.functions.adoptCat().build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_token_abyss_world(self):
        try:
            contract_address = self.w3.to_checksum_address(abuse_world_contract)
            with open('ABI/abyss_world.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 340000)
            txn = contract.functions.purchase(1).build_transaction({
                'value': int(self.w3.to_wei(0.0001, 'ether')),
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_satoshi_universe_battle_pass(self):
        try:
            contract_address = self.w3.to_checksum_address(satoshi_universe_contract)
            with open('ABI/satoshi_universe_battle_pass.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(250000, 350000)
            txn = contract.functions.mint((
                self.w3.to_checksum_address(self.address),
                self.w3.to_checksum_address('0x0dE240B2A3634fCD72919eB591A7207bDdef03cd'),
                1,
                [],
                1,
                b''
            )).build_transaction({
                'value': self.w3.to_wei(0.00015, 'ether'),
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def fire_moneygun_sending_me(self):
        data = ('0xf02bc6d500000000000000000000000000000000000000000000000000005af3107a'
                '4000000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        gas = random.randint(35000, 50000)

        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(sending_me_money_gun_contract),
                'value': int(self.w3.to_wei(0.0001, 'ether')),
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0


if __name__ == "__main__":
    key = ''
    proxy = ''
    m = LineaTxnManager(key, proxy)
