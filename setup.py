from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('C:\\Users\\ddsnowboard\\Documents\\tShirtPicker\\main.pyw', base=base, targetName = 'tShirtPicker')
]

setup(name='T-Shirt Picker',
      version = '2.0',
      description = 'Picks T-Shirts',
      options = dict(build_exe = buildOptions),
      executables = executables)
