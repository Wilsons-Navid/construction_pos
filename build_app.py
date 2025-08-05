# build_app.py
import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Build arguments
args = [
    '--name=Construction_POS',
    '--onefile',
    '--windowed',
    '--distpath=./dist',
    '--workpath=./build',
    '--specpath=./build',
    '--add-data=database;database',
    '--add-data=gui;gui', 
    '--add-data=utils;utils',
    '--hidden-import=sqlalchemy.dialects.sqlite',
    '--hidden-import=PIL._tkinter_finder',
    'main.py'
]

# Add icon if exists
if os.path.exists('icon.ico'):
    args.append('--icon=icon.ico')

# Run PyInstaller
PyInstaller.__main__.run(args)

print("Build complete! Check the 'dist' folder for your executable.")