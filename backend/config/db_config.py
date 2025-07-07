import os
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()

MONGO_URI=os.getenv("MONGO_URI")
DB_NAME=os.getenv("DB_NAME")
COLLECTION_NAME=os.getenv("COLLECTION_NAME")
categories_collection=os.getenv("CATEGORY-COLLECTION")
user_collection=os.getenv("user_collection")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
ADMIN_EMAIL=os.getenv("ADMIN_EMAIL")

client = MongoClient(MONGO_URI)
db=client[DB_NAME]
collection=db[COLLECTION_NAME]
collection_2=db[categories_collection]
user_collection=db[user_collection]
ADMIN_PASSWORD=ADMIN_PASSWORD
ADMIN_EMAIL=ADMIN_EMAIL

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    FRONTEND_URL = os.getenv("FRONTEND_URL")  # e.g., http://localhost:3000
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = True