import datetime

from pony import orm

from . import db


class Article(db.Entity):
    document = orm.Required("Document")

    title = orm.Required(str)
    abstract_path = orm.Required(str)
    processed_abstract_path = orm.Required(str)
    words_count = orm.Required(int)
    link_to_pdf = orm.Optional(str)
    authors = orm.Set("Author")
    date = orm.Required(datetime.datetime)
