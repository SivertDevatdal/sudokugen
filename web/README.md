# Sudoku download page

`index.html` is a single, self-contained page: a calendar where every day
that has a sudoku PDF can be clicked and downloaded. Sundays, Norwegian
public holidays and the days listed in `../no-paper-days.txt` are struck
through. It reads `pdfs/index.json`, which `kukoku.py` rewrites every time it
runs, so the page updates itself when the monthly workflow adds puzzles.

## Putting it on the VPS

The VPS only has to serve two folders from a clone of this repo: `web/`
(the page) and `pdfs/` (the files). No Python or database is needed there.

**1. Clone the repo** (for a private repo, add a
[deploy key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
and use the `git@github.com:` URL instead):

```sh
sudo git clone https://github.com/SivertDevatdal/sudokugen.git /srv/sudokugen
```

**2. Keep it up to date.** The puzzles are generated on GitHub on the 1st
of every month; pulling once an hour is plenty. `sudo crontab -e`, add:

```
0 * * * * cd /srv/sudokugen && git pull -q --ff-only
```

**3. Serve it.** With nginx, inside your website's `server { ... }` block
(this puts the page at `https://yoursite/sudoku/`):

```nginx
location /sudoku/pdfs/ {
    alias /srv/sudokugen/pdfs/;
}
location /sudoku/ {
    alias /srv/sudokugen/web/;
}
```

then `sudo nginx -t && sudo systemctl reload nginx`.

With Caddy instead:

```
handle_path /sudoku/pdfs/* {
    root * /srv/sudokugen/pdfs
    file_server
}
handle_path /sudoku/* {
    root * /srv/sudokugen/web
    file_server
}
```

**4. Link to it** from your website, e.g.
`<a href="/sudoku/">Download sudoku</a>`. You can also show it inside a
page with `<iframe src="/sudoku/" width="460" height="640" style="border:0"></iframe>`.

Everything in `pdfs/`, including future days, can be downloaded by anyone
who has the link, the same as on GitHub if the repo is public. To keep it
private, put the `/sudoku/` locations behind a password (nginx
`auth_basic`, Caddy `basic_auth`).
