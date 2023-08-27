import json
from forums import Forums
from database import MongoDBConnector


f = Forums(
    verbose=1,
    db_host="172.30.0.2:27017",
    base_link="http://germania7zs27fu3gi76wlr5rd64cc2yjexyzvrbm4jufk7pibrpizad.onion",
    cookie="m8ofuu62clk9be79vooi7k20e0469kkbhg7bf9u90amtji7f"
)
data = f.crawl_forums(auto_push_db=True, bulk_push_db=True)
#f.clear_collection("forums")

# with open("forums.json", mode="w") as file:
#     json.dump(data, file)

# db = MongoDBConnector("172.30.0.2:27017")

# forums = []
# with open("forums.json", mode="r") as file:
#     forums = json.load(file)

# inserted_documents = db.push_data_forums(forums)

# print("Inserted document IDs:", inserted_documents.inserted_ids)

f.client.close()