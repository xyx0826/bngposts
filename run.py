import os
import json

from api import Api
from database import Database


def main():
    # Check config file
    if not os.path.isfile("config.json"):
        print(
            "Error: could not find config.json."
            "Make sure you have written your API key and email into "
            "config.json.sample and renamed it to config.json."
        )
        return

    cfg = None
    with open("config.json", "r") as f:
        cfg = json.load(f)

    # Validate config keys
    if "api_key" not in cfg:
        print(
            "Error: config file does not contain API key."
            "Make sure you have your API key under \"api_key\"."
        )
        return

    # Initialize interfaces
    api = Api(cfg["app_id"], cfg["app_name"], cfg["api_key"], cfg["email"])
    db = Database()
    last_news_id = db.get_last_news_id()
    if last_news_id:
        print(f"Last fetched article is {last_news_id}")
    else:
        print("News table is empty, fetching everything")

    for news in api.get_news(last_news_id):
        db.add_news(author_name=news[0], tags=news[1], news_tuple=news[2])
    db.close()


if __name__ == "__main__":
    main()
