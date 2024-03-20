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

