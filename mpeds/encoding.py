# Fixes UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 269: ordinal not in range(128)
# Adapted from https://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte/35444608

import os

os.chdir('/usr/lib64/python2.7/site-packages')
file = open('sitecustomize.py', 'w') 
file.write('import sys\n')
file.write("sys.setdefaultencoding('utf8')")
file.close()
