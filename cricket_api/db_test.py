import pymongo
import dns # required for connecting with SRV
client = pymongo.MongoClient("mongodb+srv://manthan:manthan_1234@cluster0.q1fx6jn.mongodb.net/?retryWrites=true&w=majority")
db = client["mydatabase"]

print(db)