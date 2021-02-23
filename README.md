# bngposts

Archives [Bungie.net news posts](https://www.bungie.net/en/News)
to a SQLite database, and downloads their banner images.

## Usage

[Get an API key](https://www.bungie.net/en/Application).

Fill out `config.json.sample`:

| Key        | Value                                                                   |
| ---------- | ----------------------------------------------------------------------- |
| `app_id`   | The ID of your app. Visible in the URL of the details page of your app. |
| `app_name` | The name of your app. Included as a courtesy in `User-Agent`.           |
| `api_key`  | The API key of your app.                                                |
| `email`    | Your email address. Included as a courtesy in `User-Agent`.             |

Then rename `config.json.sample` to `config.json`.

Execute `python run.py`.

News posts, tags, and authors are stored in `bngposts.db`, and their
front page banners (FPBs) or article banners (ABs) are stored in `images` folder
when available, in format `/[0-9]+_(ab|fpb).(jpg|png)/`.

Because Bungie.net API returns news articles in most recent order, database update
is **incremental**. The script stops when it gets to an already archived news post.
