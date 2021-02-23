# bngposts

Archives [Bungie.net news posts](https://www.bungie.net/en/News)
to a SQLite database, and downloads their banner images.

## Usage

[Get an API key](https://www.bungie.net/en/Application).

Put your API key and email (for `User-Agent` courtesy) into `config.json.sample`
and rename the file to `config.json`.

Execute `python run.py`.

News posts, tags, and authors are stored in `bngposts.db`, and their
front page banners (FPBs) or article banners (ABs) are stored in `images` folder
when available, in format `/[0-9]+_(ab|fpb).(jpg|png)/`.

Because Bungie.net API returns news articles in most recent order, database update
is **incremental**. The script stops when it gets to an already archived news post.
