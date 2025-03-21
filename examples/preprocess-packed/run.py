import ultraimport

from packed import packed

tag = ultraimport('__dir__/tag.py', 'tag', preprocessor=packed.translate)


tag()
