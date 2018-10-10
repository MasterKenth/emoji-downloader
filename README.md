# emoji-downloader
Downloads emojis from https://unicode.org/emoji/charts/full-emoji-list.html to PNG files.

Useful for example in combination with [emoji-unicode](https://github.com/nitely/emoji-unicode) to replace emojis in html text with image representations (e.g. like in my case to workaround lack of easy unicode support for custom EPUB files for Kindle).


## Usage
1) Install dependencies
```Shell
pipenv install
```

2) Run
```Shell
pipenv run python emoji-downloader.py [--forcefetch] <variant>
```

| Parameter			| Description																																				|
|:------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `variant`			| Variant of emoji to download. Corresponds to the table header text of the desired column (e.g. _Appl_, _Wind_, _Twtr_, _FB_ etc.). Case-insensitive. 		|
| `forcefetch`	| (Optional flag) If specified, forces (re)downloading of the source html, otherwise use cache if it exists from previous use (default at `emoji/cache.html`). 	|

**Example**: 
```Shell
pipenv run python emoji-downloader.py Appl
```

Output is saved at `emoji/<variant>/` (e.g. `emoji/Appl/`). Files are saved as <unicode_code>.png, without `U+`, joining codes with `_` (e.g. `1f1e6_1f1e8.png`, extract from html so subject to change).


## Possible improvements
* Add option to extract all variants
* Cleaner code by removing asyncio and async dependencies (performance gain from async is untested and probably negligible at best)
* Specify custom output dir
* Specify custom cache file
* Specify different naming format(s)

Disclaimer: only tested on Windows.
