
# Coursera Notebooks Fetcher
> Fetch notebooks (including .ipynb, images, datasets...) of courses on www.coursera.com

## Usage

1. First, make sure you have registered on [coursera](https://www.coursera.org) .
2. Open the course you want, find a notebook, click into it.
Now you see a notebook (on https://hub.coursera-notebooks.org).
3. Copy headers.Cookie you have on this site.
4. Paster the Cookie into main() of /fetcher/main.py
5. In the webpage you just opened, Click the "coursera" icon at the top-left corner.
Now You see many a page with many files.
The address look like "https://hub.coursera-notebooks.org/user/jzpvoopfcbteoxgjrpwsyv/tree"
6. Copy the address, paste into main() of /fetcher/main.py
7. Run /fetcher/main.py

## dependencies
+ gevent
+ requests

