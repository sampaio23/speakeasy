# Speakeasy 🎷

Create score books from a database of Musescore files.

## Quick Start

You need Python and Musescore installed. After that, clone the repository and run:

```sh
python main.py
```

You can find the final PDF in `build/score_book.pdf`.

You can customize the `examples/speakeasy.conf` file to select which files to add to the book. The repository contains a collection of Jazz standards, as well as songs that I like.

## TODO List

- [ ] Pass 'configuration' file as command line argument
- [ ] Incremental build
- [ ] Create a Python package
- [ ] Transpose to any key when creating the book
