# ICFP Competition 2024

## Links
* [Official Site](https://icfpcontest2024.github.io/)
* [Competition Discord](https://discord.com/invite/HtXttgvCeP)
* [Shared Drive Folder](https://drive.google.com/drive/folders/1YIHAz6ulwzU6LVsBSBNl7XGtgAmxC6cJ)

## Misc

* The bearer token for submitting is in `misc/SUBMISSION_HEADER.txt`

## Tooling
* Run project iPython: `bazel run //tools:icfp_ipython`

This drops you into an ipython shell.  Import `icfp_lang` to get access to modules in that folder.

Example importing strings.py and using it:
```
from icfp_lang.strings import example, decode

result = decode(example)

print(result)
```