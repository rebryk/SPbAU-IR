import logging
import json

from pony import orm

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING)
db = orm.Database()

from .document import Document
from .author import Author
from .article import Article
from .query import Query, Like

with open("config/db.json") as f:
    config = json.load(f)
    db.bind(provider="postgres",
            user=config["user"],
            password=config["password"],
            host=config["host"],
            database=config["database"])

    db.generate_mapping(create_tables=True)

__all__ = ("Document", "Article", "Author", "Query", "Like")
