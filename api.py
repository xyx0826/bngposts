import os
import requests

from typing import Generator


HOST = "https://www.bungie.net"
ENDPOINT = "https://www.bungie.net/platform/Content/Site/News/all/en-us"
FPB = "FrontPageBanner"
AB = "ArticleBanner"


class Api:
    def _write_image(
            self, news_id: int,
            is_fpb: bool, url: str) -> None:
        """
        Downloads a FrontPageBanner or ArticleBanner to images folder.

        Args:
            news_id (int): The content ID of the news article.
            is_fpb (bool): Whether the image is a FPB or AB.
            url (str): The absolute Bungie.net URL of the image.
        """
        if not os.path.isdir("images"):
            os.mkdir("images")
        file_name = f"images/{news_id}_" + ("fpb." if is_fpb else "ab.") \
            + url.split(".")[-1]
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(file_name, "wb") as f:
                f.write(resp.content)
                print(f"Written {file_name}")

    def _get_abs_url(self, props: dict, key: str) -> str:
        url = props[key]
        if not url:
            return None
        if url.startswith("http"):
            return url.replace("http://", "https://")
        else:
            return HOST + url

    def __init__(self, api_key: str, email: str, from_page: int = 1) -> None:
        """
        Initializes networking and sets HTTP headers.

        Args:
            api_key (str): The API key to use.
            email (str): The email to use in User-Agent.
            from_page (int): The news page to begin from.
                             Defaults to first page.
        """
        if not api_key or len(api_key) != 32:
            raise ValueError("API key does not have a length of 32.")

        self._sesh = requests.Session()
        self._sesh.headers.update(
            {"X-API-Key": api_key}
        )
        self._sesh.headers.update(
            {"User-Agent": f"Lotus/1.0 AppId/34673 ({email})"}
        )
        self._data = {
            "currentpage": from_page,
            "itemsperpage": 10
        }

    def get_news(self, end_on_id: int) -> Generator[tuple, None, None]:
        """
        Returns a generator that fetches news from Bungie.net and returns
        tuples for inserting into the database. News FPBs and ABs are
        downloaded if provided.

        Args:
            end_on_id (int): A news content ID to stop fetching when seen.
                             the news with this ID itself will not be yielded.


        Yields:
            Generator[tuple, None, None]: A generator that return news tuples.
        """
        end_on_id = str(end_on_id)  # API id field is a string
        more = True
        while more:
            resp = self._sesh.get(ENDPOINT, params=self._data)
            if resp.status_code != 200:
                print("HTTP error.")
                return

            data = resp.json()
            if data["ErrorCode"] != 1:
                print("API error.")
                return

            for news in data["Response"]["results"]:
                # Extract ID, check against stop marker
                id = news["contentId"]
                if (id == str(end_on_id)):
                    print("Reached stop marker")
                    more = False
                    break

                props = news["properties"]
                author = news["author"]

                # Write banner images if needed
                fpb = self._get_abs_url(props, FPB)
                if fpb:
                    self._write_image(id, True, fpb)
                ab = self._get_abs_url(props, AB)
                if ab:
                    self._write_image(id, False, ab)

                # (author_name, tags, news_tuple)
                yield (author["displayName"], news["tags"], (
                    id, news["creationDate"], author["membershipId"],
                    props["Title"], props["Subtitle"], props["Content"],
                    fpb, ab
                ))

            print("Finished page " + str(self._data["currentpage"]))
            more = more and data["Response"]["hasMore"]
            self._data["currentpage"] += 1
