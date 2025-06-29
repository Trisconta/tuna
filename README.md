# Tuna

**Tuna** is a lightweight Python tool that extracts, structures, and formats metadata from the iTunes/Music library database on macOS. Whether you want to analyze your listening habits, clean up your library, or feed your own playlist generator -- Tuna's got your back.

## Features

- Parses `.xml` iTunes/Music library files (not `.itl`)
- Converts track metadata into clean JSON output
- Supports podcasts, streams, and locally stored tracks
- Maps internal rating values to user-friendly star ratings
- Handles non-ASCII characters and malformed metadata gracefully

## Installation

```bash
git clone https://github.com/trisconta/tuna.git
cd tuna
pip install -r requirements.txt
```
