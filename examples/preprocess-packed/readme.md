# Dynamic JSX-Style Processing with Ultraimport

This example demonstrates a powerful feature of ultraimport: dynamically preprocessing code during import. We're using the [packed](https://github.com/michaeljones/packed) library which provides JSX-style syntax in Python, but in a more efficient way than the library's default approach.

## Prerequisites

This example requires the `packed` package to be installed:

```bash
pip install packed
```

## Advantages Over Standard Packed Approach

The standard approach with packed requires manually preprocessing `.pyx` files to generate `.py` files:

```bash
python -m packed .  # Generates .py files for all .pyx files
```

With ultraimport, we get several major advantages:

1. **Dynamic Processing**: No need to manually preprocess files or run a separate step
2. **Instant Feedback**: Changes to JSX syntax are processed on every import
3. **Seamless Integration**: JSX markup can be used directly in regular Python files
4. **Development Friendly**: Edit-run cycle is simpler without compile steps

## How It Works

1. The `tag.py` file contains JSX-like syntax:
   ```python
   def tag(self):
       share = get_share_link()
       return <a href={share}>Share on internet</a>
   ```

2. In `run.py`, we use ultraimport's preprocessor feature to transform the code on-the-fly:
   ```python
   tag = ultraimport('__dir__/tag.py', 'tag', preprocessor=packed.translate)
   ```
   
3. The code is automatically transformed during import without any additional steps.

This approach streamlines development by removing manual preprocessing steps, making it easier to iterate on JSX-style Python code.