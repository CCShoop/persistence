# persistence
JSON file handling library for persistent data storage.

## Adding it to a bot

Add it as a git submodule where the bot imports it from, for example:

```
git submodule add https://github.com/CCShoop/persistence.git libs/persistence
```

```python
from libs.persistence import Persistence
```

Or at the top level, imported with `from persistence import Persistence`:

```
git submodule add https://github.com/CCShoop/persistence.git persistence
```

After cloning or pulling a bot that uses it, fetch the submodule with `git submodule update --init`. To update a bot to the latest version, run `git submodule update --remote` in the bot and commit the change.

## Usage

```python
persist = Persistence("data.json")
data = persist.read()        # None if the file doesn't exist
persist.write({"key": "value"})
```

- `write()` writes to `<file>.tmp` and then swaps it in, so a crash can't leave the file half-written. It skips writing when the data hasn't changed since the last write, so calling it every second is cheap.
- `read()` raises an error if the file isn't valid JSON. Call `quarantine()` to rename the file to `<file>.corrupt-<date and time>`, so the bot can start fresh without overwriting it.
- `pause()` makes `read()` return None and `write()` do nothing until `resume()`, for example while shutting down.
- Reads and writes are serialized with a lock, so they're safe to call from worker threads.

## Running the tests

```
python3 -m pytest
```
