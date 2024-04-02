import random
import string
import datetime

import json
from datetime import datetime

import requests
from html.parser import HTMLParser
from eth_account.messages import encode_defunct
from web3 import HTTPProvider
from eth_account import Account


from blockchain_data.blockchain_data import linea
from gas_staff.gas import *
from headers.headers import *
from contracts import *


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
        self.yooldo_token = None

    def _signIn_ulti_pilot(self):
        try:
            message = self._get_signature_u_p()
            if message is None:
                logger.error("message not arrive")
                return None

            signature = self.account.sign_message(encode_defunct(text=message))
            payload = {
                "address": str(self.address),
                "signature": str(signature.signature.hex()),
                "chainId": 59144
            }
            headers = ultipilot_headers_2()
            response = requests.post(url='https://account-api.ultiverse.io/api/wallets/signin',
                                     proxies=self.session.proxies, json=payload, headers=headers)

            if response.status_code == 201:
                data = response.json()
                if data['success']:
                    access_token = data['data']['access_token']
                    self.ultipilot_token = access_token
                    logger.success('got ulti-pilot signIn token')
                    return access_token
            else:
                logger.error(f"wrong status code - {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"error while signIn [ulti-pilot]: {e}")
            return None

    def _get_signature_u_p(self):
        try:
            headers = ultipilot_headers_1()
            payload = {
                "address": str(self.address),
                "feature": "assets-wallet-login",
                "chainId": 59144}

            response = requests.post(url='https://account-api.ultiverse.io/api/user/signature',
                                     proxies=self.session.proxies, json=payload, headers=headers)

            if response.status_code == 201:
                message = response.json()['data']["message"]
                return message
        except Exception as e:
            logger.error("error while getting message [ulti-pilot]"
                         f"\nError: {e}")
        return None

    def _register_ultipilot(self):
        try:
            token = self.ultipilot_token
            payload = {"referralCode": "Linea", "chainId": '59144'}
            response = requests.post(url='https://pml.ultiverse.io/api/register/sign', proxies=self.session.proxies,
                                     headers=ultipilot_headers_3(address=self.address, token=token), json=payload)
            # print(json.dumps(response.json(), indent=4))
            if response.json()['success'] is False and 'Wallet already registered' in response.json()['err']:
                logger.warning("wallet is already register on ulti-pilots, wich is good...")
                return True
            elif response.json()['success'] is True:
                return True
            else:
                logger.error("unknown response format")
                return False
        except Exception as e:
            logger.error('error while wallet registration [ulti-pilots]'
                         f'error: {e}')
            return False

    def _get_txn_data_ultipilot(self):
        try:
            self._signIn_ulti_pilot()
            if self.ultipilot_token is None:
                return
            reg = self._register_ultipilot()
            if not reg:
                return

            silhouette_traits = [
                ["Optimistic", "Introverted", "Adventurous"],
                ["Sensitive", "Confident", "Curious"],
                ["Practical", "Social Butterfly", "Independent"],
                ["Responsible", "Open-minded", "Humorous"],
                ["Grounded", "Skeptical", "Altruistic"]
            ]
            chosen_traits = [random.choice(traits) for traits in silhouette_traits]
            payload = {
                "meta": chosen_traits,
                "chainId": 59144
            }
            token = self.ultipilot_token
            response = requests.post(url='https://pml.ultiverse.io/api/register/mint', proxies=self.session.proxies,
                                     headers=ultipilot_headers_3(address=self.address, token=token), json=payload)

            data = response.json().get('data', {})
            deadline = data.get('deadline')
            attributeHash = data.get('attributeHash')
            signature = data.get('signature')
            return deadline, attributeHash, signature
        except Exception as e:
            logger.error('error while getting txn data for ulti-pilots mint'
                         f'\nerror: {e}')
            return None

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

    def _yooldo_registration(self):
        try:
            payload = {"walletAddress": self.address}
            response = requests.post('https://yooldo.be.by-catze.xyz/nonce',
                                     headers=yooldo_headers(content_length=62),
                                     json=payload, proxies=self.session.proxies)

            message = response.json()["nonce"]
            signature = self.account.sign_message(encode_defunct(text=message))
            simbols = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            payload = {
                "chainId": 59144,
                "signature": signature.signature.hex(),
                "email": f"{simbols}@gmail.com",
                "walletAddress": str(self.address.lower()),
            }

            response = requests.post('https://yooldo.be.by-catze.xyz/auth/registerWithWallet',
                                     headers=yooldo_headers(content_length=252), json=payload,
                                     proxies=self.session.proxies)

            if response.status_code == 201:
                if "id" in response.json():
                    logger.success(f"yooldo account registered, it ID: {response.json()['id']}")
                    return 0
            elif response.status_code == 409:
                logger.warning(f"account already exist... which is good")
                return 0
        except Exception as e:
            logger.error("error while account creation."
                         f"\nError: {e}")
            return 1

    def _get_token_yooldo(self):
        try:
            payload = {"walletAddress": self.address}
            response = requests.post('https://yooldo.be.by-catze.xyz/nonce',
                                     headers=yooldo_headers(content_length=62),
                                     json=payload, proxies=self.session.proxies)

            message = response.json()["nonce"]
            signature = self.account.sign_message(encode_defunct(text=message))

            payload = {
                "chainId": 59144,
                "signature": signature.signature.hex(),
                "walletAddress": str(self.address.lower()),
            }

            response = requests.post('https://yooldo.be.by-catze.xyz/auth/loginWithWallet',
                                     headers=yooldo_headers(content_length=252), json=payload,
                                     proxies=self.session.proxies)

            if response.status_code == 201:
                token = response.json()["accessToken"]
                self.yooldo_token = token
                logger.success(f"yooldo token obtained...")
                return 0
        except Exception as e:
            logger.error("error while obtaining yooldo token"
                         f"\nError: {e}")
            return 1

    def _get_txn_data_yooldo(self):
        with open("data\\yooldo_codes.txt", 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]
        if not lines:
            logger.critical("yooldo codes has ended!")
            return 0

        code = random.choice(lines)

        url = f"https://yooldo.be.by-catze.xyz/linea-park/rpd/validateUID?uid={code}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            'Authorization': f'Bearer {self.yooldo_token}'
        }

        response = requests.options(url, headers=headers, proxies=self.session.proxies)

        headers = {
            "User-Agent": random_ua(),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            'Authorization': f'Bearer {self.yooldo_token}'
        }
        response = requests.get(url, headers=headers, proxies=self.session.proxies)
        print(response.status_code)
        print(response.headers)
        print(response.content)

    def yooldo_random_defence_wrap(self):
        if self._yooldo_registration() == 0:
            if self._get_token_yooldo() == 0:
                self._get_txn_data_yooldo()
        else:
            logger.critical("yooldo account registration failed, exiting...")
            return 1

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
                'gas': int(gas_limit),
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

    def mint_NFTbadge(self):
        try:
            contract_address = self.w3.to_checksum_address(NFTbadge_contract)
            with open('ABI/NFTBadge.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 340000)
            txn = contract.functions.mint().build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_battlemon(self):
        try:
            contract_address = self.w3.to_checksum_address(battlemon_contract)
            with open('ABI/battlemon.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(200000, 250000)
            txn = contract.functions.safeMint().build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_expedition_legacy(self):
        data = "0x1249c58b"
        gas = 81555
        gas_price = get_gas()
        try:
            txn = {
                'to': self.w3.to_checksum_address(expedition_legacy_contract),
                'value': int(self.w3.to_wei(0.0003, 'ether')),
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }

            if self._submit_and_log_transaction(txn):
                logger.info("going to send second second txn for bonus-task")
                data = "0x1249c58b"
                gas = 81555
                gas_price = get_gas()
                txn = {
                    'to': self.w3.to_checksum_address(expedition_legacy_contract_2),
                    'value': int(self.w3.to_wei(0.00015, 'ether')),
                    'gas': gas,
                    'data': data,
                    'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                    'nonce': self.w3.eth.get_transaction_count(self.address),
                }
                return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_micro3(self):
        try:
            contract_address = self.w3.to_checksum_address(micro_nft_contract)
            with open('ABI/MicroNFTV2.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            txn = contract.functions.purchase(1).build_transaction({
                'value': int(self.w3.to_wei(0.00006, 'ether')),
                'gas': 275426,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })

            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_nft_nft(self):
        random_metadata = ''.join(random.choices(string.ascii_letters + string.digits, k=59))
        metadata_url = f"https://ipfs.io/ipfs/{random_metadata}/metadata.json"

        try:
            contract_address = self.w3.to_checksum_address(nft_contract)
            with open('ABI/NFT.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(300000, 400000)
            txn = contract.functions.mint(metadata_url).build_transaction({
                'value': int(self.w3.to_wei(0.0001, 'ether')),
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_alien_nft(self):
        data = '0xefef39a10000000000000000000000000000000000000000000000000000000000000001'
        gas = random.randint(300000, 400000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(alien_swap_nft_contract),
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

    def mint_arena_nft(self):
        v = self.address.replace('0x', '')
        padded_address = v.rjust(64, '0')
        padded_data = '0x40d097c3' + padded_address
        gas = random.randint(100000, 150000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(arena_nft_contract),
                'value': 0,
                'gas': gas,
                'data': padded_data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def zace_main(self):
        data = '0xbaeb0718'
        gas = random.randint(300000, 400000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(zace_contract),
                'value': int(self.w3.to_wei(0.00005, 'ether')),
                'gas': gas,
                'data': data,
                'gasPrice': int(self.w3.to_wei(gas_price, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            }
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_agg_genesis_something(self):
        data = '0x1249c58b'
        gas = random.randint(200000, 250000)
        gas_price = get_gas()

        try:
            txn = {
                'to': self.w3.to_checksum_address(agg_world_contract),
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

    def mint_ultipilots(self):
        deadline, attributeHash, signature = self._get_txn_data_ultipilot()
        if deadline is None or attributeHash is None or signature is None:
            logger.warning("txn data is not received, dropping mint")
            return 0
        try:
            contract_address = self.w3.to_checksum_address(ultipilot_contract)
            with open('ABI/SBTGenesis.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(250000, 350000)
            txn = contract.functions.mintSBT(deadline, attributeHash, signature).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })
            logger.info("txn data send to blockchain")
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def comic_book_wrap(self):
        if not self.mint_comic_book():
            logger.warning('failed to mint comic book')
        logger.info(f"address {self.address} going to execute second txn for a bonus task")
        return self.claim_comic_book()

    def claim_comic_book(self):
        with open('ABI/DropERC1155.json', 'r') as abi:
            contract_abi = json.load(abi)
        contract_address = self.w3.to_checksum_address(comic_book_claim_contract)
        contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)
        gas = random.randint(200000, 250000)

        txn = contract.functions.claim(
            str(self.address),
            6,
            1,
            self.w3.to_checksum_address("0x21d624c846725ABe1e1e7d662E9fB274999009Aa"),
            0,
            (
                [
                    "0x0000000000000000000000000000000000000000000000000000000000000000"
                ],
                1,
                0,
                self.w3.to_checksum_address("0x21d624c846725ABe1e1e7d662E9fB274999009Aa"),
            ),
            "0x"
        ).build_transaction({
            'value': 0,
            'gas': gas,
            'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
            'nonce': self.w3.eth.get_transaction_count(self.address),
        })
        return self._submit_and_log_transaction(txn)

    def mint_comic_book(self):
        try:
            contract_address = self.w3.to_checksum_address(comic_book_contract)
            with open('ABI/DropERC1155.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(250000, 350000)
            txn = contract.functions.claim(
                self.address,
                1,
                1,
                "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                100000000000000,
                (
                    [
                        "0x0000000000000000000000000000000000000000000000000000000000000000"
                    ],
                    1,
                    100000000000000,
                    "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                ),
                "0x"
            ).build_transaction({
                'value': int(self.w3.to_wei(0.0001, 'ether')),
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0

    def mint_nounce(self):
        try:
            contract_address = self.w3.to_checksum_address(nounce_contract)
            with open('ABI/DropERC1155.json', 'r') as abi:
                contract_abi = json.load(abi)
            contract = self.w3.eth.contract(address=contract_address, abi=contract_abi)

            gas = random.randint(250000, 350000)
            txn = contract.functions.claim(
                self.address,
                0,
                1,
                "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                0,
                (
                    [
                        "0x0000000000000000000000000000000000000000000000000000000000000000"
                    ],
                    115792089237316195423570985008687907853269984665640564039457584007913129639935,

                    0,
                    "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
                ),
                "0x"
            ).build_transaction({
                'value': 0,
                'gas': gas,
                'maxFeePerGas': int(self.w3.to_wei(MAX_GAS, 'gwei')),
                'nonce': self.w3.eth.get_transaction_count(self.address),
            })
            return self._submit_and_log_transaction(txn)
        except Exception as e:
            logger.critical(e)
            return 0


if __name__ == "__main__":
    key = ''
    proxy = ''
    m = LineaTxnManager(key, proxy)
    f = m.w3
