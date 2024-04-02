from pyuseragents import random as random_ua


def yooldo_headers(content_length=None, yooldo_token=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,en-US;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://app.yooldo.gg",
        "Referer": "https://app.yooldo.gg/",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": random_ua(),
    }
    if content_length is not None:
        headers['Content-Length'] = str(content_length)
    if yooldo_token is not None:
        headers['Authorization'] = f'Bearer {yooldo_token}'
    return headers

def tomo_headers(content_length=None, token=None):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,en-US;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://h5.tomo.inc",
        "Referer": "https://h5.tomo.inc/",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": random_ua(),
    }
    if content_length is not None:
        headers['Content-Length'] = str(content_length)
    if token is not None:
        headers['Authorization'] = f'Bearer {token}'
    return headers
def lineascan_headers():
    return {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://lineascan.build',
        'Referer': 'https://lineascan.build/',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Opera";v="107", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': random_ua(),
    }


def ultipilot_headers_1():
    return {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,en-US;q=0.9",
        "Access-Control-Request-Headers": "content-type,ul-auth-api-key",
        "Access-Control-Request-Method": "POST",
        "Origin": "https://pilot-linea.ultiverse.io",
        "Referer": "https://pilot-linea.ultiverse.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Ul-Auth-Api-Key": "YWktYWdlbnRAZFd4MGFYWmxjbk5s",
        "User-Agent": random_ua()
    }


def ultipilot_headers_2():
    return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en,en-US;q=0.9",
            "Content-Length": "219",
            "Content-Type": "application/json",
            "Origin": "https://pilot-linea.ultiverse.io",
            "Referer": "https://pilot-linea.ultiverse.io/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Ul-Auth-Api-Key": "YWktYWdlbnRAZFd4MGFYWmxjbk5s",
            "User-Agent": random_ua()
    }


def ultipilot_headers_3(address: str, token: str):
    return {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,en-US;q=0.9',
        'Content-Length': '90',
        'Content-Type': 'application/json',
        'Origin': 'https://pilot-linea.ultiverse.io',
        'Referer': 'https://pilot-linea.ultiverse.io/',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Ul-Auth-Address': address,
        'Ul-Auth-Token': token,
        'User-Agent': random_ua()
    }
