from importlib.util import find_spec
from pathlib import Path

from PyInstaller.compat import is_darwin, is_unix, is_win


arcade_spec = find_spec('arcade')
if arcade_spec is None or arcade_spec.origin is None:
    raise ImportError('Arcade is not installed. Cannot continue.')

arcade_path = Path(arcade_spec.origin).parent
hiddenimports = ['arcade.gl.backends.opengl.provider', 'arcade.gl.backends.opengl']
datas = [
    (arcade_path / 'resources' / 'system', './arcade/resources/system'),
    (arcade_path / 'VERSION', './arcade'),
]
binaries = []

if is_darwin:
    binaries.append((arcade_path / 'lib', './arcade/lib'))

pymunk_spec = find_spec('pymunk')
if pymunk_spec is not None and pymunk_spec.origin is not None:
    pymunk_path = Path(pymunk_spec.origin).parent
    if is_win:
        binaries.append((pymunk_path / '_chipmunk.pyd', '.'))
    elif is_darwin or is_unix:
        binaries.append((pymunk_path / '_chipmunk.abi3.so', '.'))
