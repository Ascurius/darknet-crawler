import json
from forums import Forums

f = Forums(
    base_link="http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion",
    cookie="d7lns6g5j16kv7aaihbd127mqpti9m5trhn5s7d61il3h1cq"
)
data = f.crawl_forums()

with open("forums.json", mode="w") as file:
    json.dump(data, file)
