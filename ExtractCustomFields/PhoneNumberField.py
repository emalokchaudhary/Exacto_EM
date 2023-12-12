#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 17:23:23 2020

@author: tacacs
"""

from .NumberField import NumberField
from . import utility as ut
import re



class PhoneNumberField(NumberField):
    
    def __init__(self):

        self.specific_patterns = []
        super(PhoneNumberField, self).__init__(self.specific_patterns, v_spaces_to_split=2, h_spaces_to_split=2)

    def __str__(self):
        return "phone number extractor"

    def validation_fun(self, number):
        char_prop, digit_prop = ut.char_digit_prop(number)
        if digit_prop < 0.6:
            return False
        if len(number) < 10:
            return False
        if '/' in number:
            return False
        return True

        



if __name__=='__main__':
    pass
    



