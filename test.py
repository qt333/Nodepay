import requests

# proxy = {'http':'47.91.121.127:9080'}
# proxy = {'http':'47.91.109.17:8108'}

# req = requests.get('https://app.nodepay.ai', proxies=proxy)
# print(req.status_code)

# proxy_list = []
# with open('free-proxy.txt', 'r') as file:
#     proxy_list = [proxy.strip() for proxy in file.readlines()]
#     print(proxy_list)

with open('free-proxy.txt', 'r') as file:
    proxy_list = [proxy.strip() for proxy in file.readlines()]
    # print(proxy_list)

def define_proxy(proxy):
    host, port, username, password = proxy.split(':')
    proxy_url = f'socks5://{username}:{password}@{host}:{port}'
    return proxy_url

proxies = [define_proxy(proxy) for proxy in proxy_list]
print(proxies)