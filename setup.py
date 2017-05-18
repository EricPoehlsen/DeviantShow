# coding=utf 8
"""
This setup.py is used to compile a standalone windows version of the program
to call it execute: python setup.py py2exe
"""

from distutils.core import setup
import py2exe
import os


#building data_files lists ... 
data_files = []

"""
dirs = ['images','img','data','fonts','templates','chars']
for dir in dirs:
    files = os.listdir(dir)
    file_list = []
    for file in files:
        if os.path.isfile(dir+"/"+file): file_list.append(dir+"/"+file)
    data_files.append((dir,file_list))
"""
data_files.append(("downloads",[]))
data_files.append(("fonts", ["hh_samuel.ttf"]))
data_files.append(("", ["README.md, cacert.pem"]))
    
setup(console=['main.py'], data_files=data_files)