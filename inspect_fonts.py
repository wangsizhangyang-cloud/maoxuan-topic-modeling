import inspect
from qhchina import helpers
print("=== load_font ===")
print(inspect.getsource(helpers.load_font)[:1500])
print("=== load_fonts ===")
print(inspect.getsource(helpers.load_fonts)[:1200])
print("=== get_current_font_name ===")
print(inspect.getsource(helpers.get_current_font_name)[:600])
