#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 17:23:23 2020

@author: tacacs
"""

from .NumberField import NumberField
import re



class NameField(NumberField):
    
    def __init__(self):
        self.specific_patterns = []
        super(NameField, self).__init__(self.specific_patterns,multiple_val=True)

    def __str__(self):
        return "name extractor"
        
    def validation_fun(self, name):

        if re.search(r'[A-Z][a-z]+', name):
            return True
        return False

if __name__=='__main__':
    pass
    



