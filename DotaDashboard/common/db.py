import pymongo
import config
# import pandas as pd

from pymongo import MongoClient

_db_config = None

def init():
  global _db_config
  _db_config = config.MONGODB_DATABASE_URI
  conn = MongoClient(_db_config)
  return conn

def insert_mongo(db, data, collection):
  """ Save dataframe from pandas to MongoDB """

  conn = init()
  db = conn[db]
  records = json.loads(data.T.to_json()).values()
  result = db[collection].insert(records)
  return result

def save_line_by_line(db, data, collection):
  conn = init()
  db = conn[db]
  result = db[collection].save(data)
  return result

def load_mongo(db, collection, query={}):
  conn = init()
  db = conn[db]
  data = db[collection].find(query)
  return data

def load_match(db, collection, projection, query={}):
  conn = init()
  db = conn[db]
  data = db[collection].find(query, projection)
  return data
