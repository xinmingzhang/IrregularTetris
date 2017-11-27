# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal, get_deps_all, hookspath, runtime_hooks
from kivy.deps import sdl2, glew, gstreamer

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\TJ\\Desktop\\tetris'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=hookspath(),
             runtime_hooks=runtime_hooks(),
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             **get_deps_all())
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='tetris',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, Tree('C:\\Users\\TJ\\Desktop\\tetris'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)],
               strip=False,
               upx=True,
               name='tetris')