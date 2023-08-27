import json
from forums import Forums


f = Forums(
    base_link="http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion",
    cookie="2kc9mlhkcr12qojdoqviu6bp5g9vjb70jfg12ab1surgg85s"
)
data = f.crawl_forums()

with open("forums.json", mode="w") as file:
    json.dump(data, file)
