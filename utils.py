# -*- coding: utf-8 -*-

from __future__ import division

import re
import os
import shutil
import string

COMMON_CHARS = [l for l in string.ascii_letters] + [l for l in string.digits]
SPECIAL_CHARS =    ['^',   #Accent circumflex (caret)
                  '&',   #Ampersand
                  '\'',   #Apostrophe (single quotation mark)
                  '@',   #At sign
                  '{',   #Brace left
                  '}',   #Brace right
                  '[',   #Bracket opening
                  ']',   #Bracket closing
                  ',',   #Comma
                  '$',   #Dollar sign
                  '=',   #Equal sign
                  '!',   #Exclamation point
                  '-',   #Hyphen
                  '#',   #Number sign
                  '(',   #Parenthesis opening
                  ')',   #Parenthesis closing
                  '%',   #Percent
                  '.',   #Period
                  '+',   #Plus
                  '~',   #Tilde
                  '_',   #Underscore
                  ' ',   #Space
                  ]
VALID_CHARS = COMMON_CHARS + SPECIAL_CHARS

PALATS  = {'č':'c','ć':'c','ž':'z','š':'s','đ':'d','Č':'C','Ć':'C','Ž':'Z','Š':'S','Đ':'D'}

def rmpalat(value):
    for (k,v) in PALATS.items():
        value = value.replace(unicode(k,"utf-8"),v)
    return value

def humanize_bytes(bytes, precision=1):
    """Return a humanized string representation of a number of bytes.

    Assumes `from __future__ import division`.

    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 kB'
    >>> humanize_bytes(1024*123)
    '123.0 kB'
    >>> humanize_bytes(1024*12342)
    '12.1 MB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GB'
    """
    abbrevs = (
        (1<<50L, 'PB'),
        (1<<40L, 'TB'),
        (1<<30L, 'GB'),
        (1<<20L, 'MB'),
        (1<<10L, 'kB'),
        (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)

def dir_size(start_path='.'):
    total_size = 0
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
        total_files += len(filenames)
    return (total_size,total_files)

def extension(path):
    m = re.match(r'^.*\.(\w+)$',path)
    return m.group(1) if m else 'none'

def copy(src,dest):
    (_dir,_file) = os.path.split(dest)
    try:
        os.makedirs(_dir)
    except OSError,e:
        pass
    shutil.copy(src,dest)
    
def correct_path(args):
    
    def clean_arg(arg):
        chars = [c if c in VALID_CHARS else '_' for c in rmpalat(arg)]
        if chars[-1] in SPECIAL_CHARS:
            chars[-1] = '_'
        return ''.join(chars)
    
    args = map(clean_arg,args)
    return args