import requests

session = requests.session()
session.proxies = {"http": "socks5://127.0.0.1:9150",
                   "https": "socks5://127.0.0.1:9150"}

result = session.get("germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion").text

print(result)