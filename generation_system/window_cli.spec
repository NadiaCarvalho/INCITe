# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
spec_root = os.path.realpath(SPECPATH)

options = []
# options = [('v', None, 'OPTION')]

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
tf_hidden_imports = collect_submodules('music21')
tf_datas = collect_data_files('music21', subdir=None, include_py_files=True)

a = Analysis(['code\\cli.py'],
             pathex=['D:\\FEUP_1920\\DISS\\Dissertation\\generation_system'],
             binaries=[],
             datas= tf_datas,
             hiddenimports= tf_hidden_imports + ['sklearn', 'sklearn.neighbors._typedefs', 'sklearn.utils._cython_blas', 'sklearn.neighbors._quad_tree', 'sklearn.tree', 'sklearn.tree._utils'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('logo.ico','D:\\FEUP_1920\\DISS\\Dissertation\\generation_system\\data\\images\\logo.ico','DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          # exclude_binaries=True,
          name='MyMusicalSuggestor',
          debug=False,
          strip=False,
          upx=True,
          icon='D:\\FEUP_1920\\DISS\\Dissertation\\generation_system\\data\\images\\logo.ico',
          bootloader_ignore_signals=False,
          runtime_tmpdir=None,
          console=False)

