# MongoDB

MongoDB implementation for Nautica 3.1.x

## Usage

To use MongoDB, you'll need to get the plugin from the service registry, you can do it like this:

```py
# file: src/lib/Mongo.py
from nautica import Services
from plugins.mongodb import MongoDB

Mongo: MongoDB = Services.get("MongoDB")
```

Now that you have the MongoDB plugin, you can access any `Collection` in said database:

```py
from src.lib.Mongo import Mongo

Mongo("users") # -> pymongo.collection.Collection
# You can use this, as you would with pymongo:

Mongo("users").find_one({"_id": ...})
Mongo("posts").find({"author_id": ...}, {"_id": 0})
Mongo("posts").insert_one({...})
```