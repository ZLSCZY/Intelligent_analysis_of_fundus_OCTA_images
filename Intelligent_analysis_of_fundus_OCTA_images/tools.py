import os
import shutil
import zipfile
from os.path import join, getsize
from django.shortcuts import render


def unzip_file(zip_src, dst_dir):
    fz = zipfile.ZipFile(zip_src, 'r')
    for file in fz.namelist():
        fz.extract(file, dst_dir)
