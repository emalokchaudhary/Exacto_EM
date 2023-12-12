#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 12:09:49 2020

@author: tacacs
"""
import os


def safely_create_file(fpath):
    if not os.path.exists(fpath):
        f = open(fpath, 'w')
        f.close()

curr_dir = os.path.dirname(os.path.realpath(__file__))
FILE_TYPE_VAR = os.path.join(curr_dir, 'field_type_var')

if not os.path.exists(FILE_TYPE_VAR):
    os.mkdir(FILE_TYPE_VAR)
    
NUM_FIELD = os.path.join(FILE_TYPE_VAR, 'num.txt')
safely_create_file(NUM_FIELD)

DATE_FIELD = os.path.join(FILE_TYPE_VAR, 'date.txt')
safely_create_file(DATE_FIELD)

TELE_FIELD = os.path.join(FILE_TYPE_VAR, 'phone.txt')
safely_create_file(TELE_FIELD)

TEXT_FIELD = os.path.join(FILE_TYPE_VAR, 'text.txt')
safely_create_file(TEXT_FIELD)

EMAIL_FIELD = os.path.join(FILE_TYPE_VAR, 'email.txt')
safely_create_file(EMAIL_FIELD)

NAME_FIELD = os.path.join(FILE_TYPE_VAR, 'name.txt')
safely_create_file(NAME_FIELD)

