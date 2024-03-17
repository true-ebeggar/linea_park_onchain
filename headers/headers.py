from pyuseragents import random as random_ua

def sending_me_headers(content_length=None, ua=None):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en,en-US;q=0.9',
        'content-length': '324',
        'content-type': 'application/json',
        'origin': 'https://chat.sending.me',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }
    if content_length is not None:
        headers['Content-Length'] = str(content_length)
    if ua is not None:
        headers['User-Agent'] = ua
    else:
        headers['User-Agent'] = random_ua()
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

