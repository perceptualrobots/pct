# Build and Deploy to PyPI

## 1. Prepare the notebooks

Export notebooks, run tests, and clean:

```
nbdev_prepare
```

Or on Windows use the provided batch file:

```
nb.bat
```

## 2. Build the dist files (optional)

To build the distribution files without uploading:

```
pip install build
python -m build
```

This creates `.tar.gz` and `.whl` files in the `dist/` directory.

## 3. Publish to PyPI

```
nbdev_pypi
```

This builds the package and uploads it to PyPI in one step. You will need a `~/.pypirc` file configured with your PyPI credentials or API token.

## 4. Push changes to git

On Windows:

```
upd.bat
```

On Linux/macOS:

```
./upd.sh
```
