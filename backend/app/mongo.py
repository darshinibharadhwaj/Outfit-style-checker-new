from .config import settings

if settings.use_mongomock:
    import mongomock

    _client = mongomock.MongoClient()
else:
    from pymongo import MongoClient

    _client = MongoClient(settings.mongo_uri)

mongo_db = _client[settings.mongo_db_name]

# Collections
tips_collection = mongo_db["style_tips"]
analysis_logs_collection = mongo_db["analysis_logs"]
