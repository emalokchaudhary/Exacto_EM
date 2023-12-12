#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 17:23:23 2020

@author: tacacs
"""

from .NumberField import NumberField
import re



class EmailField(NumberField):
    
    def __init__(self):
        self.specific_patterns = []
        super(EmailField, self).__init__(self.specific_patterns, start_offset=5, end_offset=15)

    def __str__(self):
        return "mail extractor"
        
    def validation_fun(self, email):
        if "." in email and '@' in email:
            return True
        return False


if __name__=='__main__':
    pass
    



