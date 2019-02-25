## hget 

Download galleries from e-hentai (downloads the original images
only).

Requires [lxml](https://lxml.de/installation.html) and Python 3.4+.

### Usage

#### Download Galleries:

```
python hget.py URLs...

python hget.py URLs... -o /path/to/directory/
```

#### To download using a textfile of urls:

```
https://e-hentai.org/g/1271534/be3dc157c2/
https://e-hentai.org/g/939026/3594918bd8/
.
.
.
```

```
cat file.txt | xargs python hget.py
```

#### Login and Download:

```
python hget.py  URLs... --username Weeb --password Lord -o /path/to/directory/
```


### License

[Unlicense](LICENSE)
