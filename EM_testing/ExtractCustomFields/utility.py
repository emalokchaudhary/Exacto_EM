#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 14:03:59 2020

@author: tacacs
"""

import re
import os, glob


    
    

def extract_num(filename):
    key = re.search(r'[-]\d+[_]infoN',filename).group(0)
    key = re.search(r'\d+',key).group(0)
    key = int(key)
    return key

def sortfilename(base_filenames):
   
    sorted_files = sorted(base_filenames, key = extract_num )
    return sorted_files

def read_all_files(path):
    all_files = []
    filepath = path + '/*_infoN.txt' 
    basefile_names = [filename.split('/')[-1] for filename in glob.glob(filepath)]
    basefile_names = [basefile_name for basefile_name in basefile_names if not basefile_name.startswith('Trng')]
    basefile_names = sortfilename(basefile_names)
    for filename in basefile_names:
        filepath = os.path.join(path,filename)
        all_files.append(filepath)
    return all_files

    
def read_lines(filepath):
    with open(filepath,'r',encoding='utf-8') as f:
        Lines = f.readlines()
        #Lines = [line.strip('\n') for line in Lines if line.strip('\n').strip()]
        Lines = [line.replace('(','') for line in Lines]
        Lines = [line.replace(')','') for line in Lines]
    return Lines



def order_uniquify(seq, idfun=None): 
    
    ######## Functions to return the unique elements of the list while preserving the order   #########
    
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def get_pattern_list(filepath, sort_by_len=False):
    patterns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip('\n').strip()
            if line:
                patterns.append(line)
    first_pattern = patterns[0]
    patterns = patterns[1:]    
    patterns = [p for p in patterns if len(p) >1]
    patterns = [p for p in patterns if p not in ['', ',', '/', '.', '(', ')']]
    patterns = order_uniquify(patterns)
    if sort_by_len:
        patterns = sorted(patterns, key=lambda x: len(x), reverse=True)
    patterns = [pattern.replace('(', '') for pattern in patterns]
    patterns = [pattern.replace(')', '') for pattern in patterns]
    patterns = [first_pattern] + patterns
    return patterns

def clean_pattern(pattern_list):
    cleaned_pattern_list = []
    for pattern in pattern_list:
        pattern = pattern.replace('(','')
        pattern = pattern.replace(')','')
        pattern = pattern.replace('[','')
        pattern = pattern.replace(']','')
        pattern = pattern.replace('{','')
        pattern = pattern.replace('}','')
        cleaned_pattern_list.append(pattern)
    return cleaned_pattern_list


def create_compiled_pat(pattern, ignore_case=False):
    
    all_splits = pattern.split()
    if len(all_splits) == 5:
        if ignore_case:
            c_pattern = re.compile(r'{}\s*{}\s*{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2],all_splits[3],all_splits[4]),re.IGNORECASE)
        else:
            c_pattern = re.compile(r'{}\s*{}\s*{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2],all_splits[3],all_splits[4]))
            
    elif len(all_splits) == 4:
        if ignore_case:
            c_pattern = re.compile(r'{}\s*{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2],all_splits[3]),re.IGNORECASE)
        else:
            c_pattern = re.compile(r'{}\s*{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2],all_splits[3]))
    elif len(all_splits) == 3:
        if ignore_case:
            c_pattern = re.compile(r'{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2]),re.IGNORECASE)
        else:
            c_pattern = re.compile(r'{}\s*{}\s*{}'.format(all_splits[0],all_splits[1],all_splits[2]))
    elif len(all_splits) == 2:
        if ignore_case:
            c_pattern = re.compile(r'{}\s*{}'.format(all_splits[0], all_splits[1]), re.IGNORECASE)
        else:
            c_pattern = re.compile(r'{}\s*{}'.format(all_splits[0], all_splits[1]),re.IGNORECASE)
    else:
        if ignore_case:
            c_pattern = re.compile(r'{}'.format(pattern), re.IGNORECASE)
            if len(pattern) == 2:
                c_pattern = re.compile(r'\b{}\b'.format(pattern), re.IGNORECASE)
                
        else:
            c_pattern = re.compile(r'{}'.format(pattern))
            if len(pattern) == 2:
                c_pattern = re.compile(r'\b{}\b'.format(pattern), re.IGNORECASE)

    return c_pattern

def cal_char_occurence(sent, char):
    count = 0
    for s in sent:
        if s==char.strip():
            count += 1
    return count

def char_digit_prop(sent):
    char_count = 0
    digit_count = 0
    for char in sent:
        if re.search(r'[A-Za-z]', char):
            char_count += 1
        if re.search(r'\d', char):
            digit_count += 1
    try:
        char_prop = char_count/float(len(sent))
    except:
        char_prop = 0.0
    try:
        digit_prop = digit_count/float(len(sent))
    except:
        digit_prop = 0.0
    return char_prop, digit_prop
    
    
            
    




