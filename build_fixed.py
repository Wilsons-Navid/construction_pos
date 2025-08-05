# build_simple_fixed.py
import subprocess
import sys
import os

# Simple build without data files - let Python handle imports
cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    '--name=Construction_POS',
    '--clean',
    '--paths=.',
    '--paths=database',
    '--paths=gui',
    '--paths=utils',
    'main.py'
]

print("Building with simple configuration...")
subprocess.run(cmd)