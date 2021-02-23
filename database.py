import sqlite3


class Database:
    def _ensure_tables(self) -> None:
        """
        Makes sure the tables are created.
        """
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS "authors" (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS "news" (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                author_id INTEGER NOT NULL REFERENCES authors(id),
                title TEXT NOT NULL,
                subtitle TEXT NOT NULL,
                content TEXT NOT NULL,
                frontpage_banner TEXT,
                article_banner TEXT
            );
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS "tags" (
                id INTEGER PRIMARY KEY,
                name TEXT
            );
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS "news_tags" (
                news_id INTEGER NOT NULL REFERENCES news(id),
                tag_id INTEGER NOT NULL REFERENCES tags(id)
            );
            """
        )

    def _cache_authors(self):
        """
        Caches all author IDs and their names from the database.
        """
        self._authors = {v: k for k, v in self._conn.execute(
            "SELECT * FROM authors;"
        )}

    def _cache_tags(self):
        """
        Caches all tags IDs and their names from the database.
        """
        self._tags = {v: k for k, v in self._conn.execute(
            "SELECT * FROM tags;"
        )}

    def __init__(self) -> None:
        """
        Connects to and sets up the database.
        """
        self._conn = sqlite3.connect("bngposts.db")
        self._conn.execute("PRAGMA foreign_keys = 1;")
        self._ensure_tables()
        self._cache_authors()
        self._cache_tags()

    def _add_author(self, id: int, name: str) -> None:
        """
        Adds an author to the database.

        Args:
            id (int): The membership ID of the author.
            name (str): The name of the author.
        """
        if name not in self._authors:
            self._conn.execute(
                "INSERT INTO authors VALUES(?, ?);", (id, name)
            )
            self._authors[name] = id
            self._conn.commit()

    def _add_tag(self, name: str) -> None:
        """
        Adds a tag to the database.

        Args:
            name (str): The name of the tag.
        """
        if name not in self._tags.values():
            result = self._conn.execute(
                "INSERT INTO tags(name) VALUES (?);", (name,)
            )
            self._tags[name] = result.lastrowid
            self._conn.commit()

    def add_news(
            self, author_name: str, tags: "list[str]",
            news_tuple: tuple) -> None:
        """
        Adds a news article tuple to the database.

        Tuple contents:
            id (int): The content ID.
            created_at (str): The ISO8601 creation date.
            author_id (str): The membership ID of the author.
            # author_name (str): The display name of the author.
            title (str): The title.
            subtitle (str): The subtitle.
            content (str): The content.
            frontpage_banner (str): The relative URL to the frontpage banner.
            article_banner (str): The relative URL to the article banner.
            # tags (list[str]): A list of tags.
        """
        # Ensure author
        if author_name not in self._authors:
            self._add_author(news_tuple[2], author_name)

        news_id = news_tuple[0]
        count = self._conn.execute(
            "SELECT COUNT() FROM news WHERE id = ?;", (news_id,)
        ).fetchone()
        if count[0] > 0:
            print(f"News {news_id} already exists")
            return

        self._conn.execute(
            "INSERT INTO news VALUES(?, ?, ?, ?, ?, ?, ?, ?);",
            news_tuple
        )

        # Add tags
        for tag in tags:
            if tag not in self._tags:
                self._add_tag(tag)
            tag_id = self._tags[tag]
            self._conn.execute(
                "INSERT INTO news_tags VALUES (?, ?);", (news_id, tag_id)
            )

        self._conn.commit()
        print(f"Added news {news_id}")

    def get_last_news_id(self) -> int:
        """
        Gets the latest news ID stored in the database.

        Returns:
            int: The ID for the latest news in the database,
                 or None if the news table is empty.
        """
        last_id = self._conn.execute(
            "SELECT id FROM news ORDER BY id DESC LIMIT 1;"
        ).fetchone()
        if not last_id:
            # News table is empty
            return last_id
        return last_id[0]

    def close(self) -> None:
        """
        Closes the connection to the database.
        """
        self._conn.commit()
        self._conn.close()
