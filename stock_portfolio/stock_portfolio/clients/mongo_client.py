import logging
import os

from pymongo import MongoClient

from stock_portfolio.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.environ.get('MONGO_PORT', 27017))

logger.info("Connecting to MongoDB at %s:%d", MONGO_HOST, MONGO_PORT)
mongo_client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
db = mongo_client['stock_portfolio']
sessions_collection = db['sessions']