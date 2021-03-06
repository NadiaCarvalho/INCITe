# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
spec_root = os.path.realpath(SPECPATH)
icon_path = os.sep.join(['', 'data', 'images', 'logo.ico'])
file_path = os.sep.join(['code', 'cli.py'])

options = []
# options = [('v', None, 'OPTION')]

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
music21_hidden_imports = (collect_submodules('music21') + collect_submodules('music21.converter'))
music21_datas = collect_data_files('music21', subdir=None, include_py_files=True)

a = Analysis([file_path],
             pathex=[spec_root],
             binaries=[],
             datas= music21_datas,
             hiddenimports= music21_hidden_imports + ['sklearn', 'sklearn.neighbors._typedefs', 'sklearn.utils._cython_blas', 'sklearn.neighbors._quad_tree', 'sklearn.tree', 'sklearn.tree._utils', 'pkg_resources.py2_warn', 'scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('logo.ico', spec_root + icon_path, 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          # exclude_binaries=True,
          name='MyMusicalSuggester',
          debug=False,
          strip=False,
          upx=True,
          icon=spec_root + icon_path,
          bootloader_ignore_signals=False,
          runtime_tmpdir=None,
          console=False)

if os.name == 'posix':
    app = BUNDLE(exe,
         name='MyMusicalSuggester.app',
         icon=spec_root + icon_path[:-1] + 'ns',
         bundle_identifier=None)