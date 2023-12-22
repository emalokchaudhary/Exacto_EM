#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 17:23:23 2020

@author: tacacs
"""

from .NumberField import NumberField
import re



class DateField(NumberField):
    
    def __init__(self):
        self.specific_patterns = ["[A-Za-z]+\s{1,2}\d{1,2}[,]?\s{1,2}\d{4}"]
        super(DateField, self).__init__(self.specific_patterns, v_spaces_to_split=2, h_spaces_to_split=2)

    def __str__(self):
        return "date extractor"
        
    def validation_fun(self, date):
        decimal_len = 0
        for i in date:
            if re.search('\d',i):
                decimal_len +=  1
    
        if decimal_len > 8:
            return False
    
        if len(date) <= 3 or re.search('[A-Z]{4,}', date) or (decimal_len <= 1):
            return False
        date_indicator = ['/','-']
        ifc = 0
        indicator_flag = False
        for i in date:
            if i in date_indicator:
                indicator_flag = True
                ifc += 1
    
        if re.search(r'^\d{3,}', date) and not indicator_flag:
            return False
        p1 = r'\d{1,2}[.][A-Z][a-z]+[.]\d{2,4}'
        p2 = r'\d{2}[.-]\d{2}[.-]\d{2}'
        p3 = r'\d{1,2}[-\./ ]{1,2}[A-Za-z]{3,9}[-\./ ]{1,2}\d{4}'
        dpat = [p1,p2,p3]
 
        if ifc >=3:
            return False
        if ifc == 2 and decimal_len >= 4:
            return True
        if indicator_flag and (len(date) > 5) and decimal_len >= 4:
            return True
        for pat in dpat:
            if re.search(pat,date):
                return True
        return False


if __name__=='__main__':
    pass
    



