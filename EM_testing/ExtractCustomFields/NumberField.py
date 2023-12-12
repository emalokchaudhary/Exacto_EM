#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:25:44 2020

@author: tacacs
"""
import re
from . import utility as ut
from .BaseInvoiceField import AbstractInvoiceField
from .HorizontalData import HorizontalData
from .VerticalData import VerticalData

class NumberField(AbstractInvoiceField):
    
    
    def __init__(self, specific_patterns=[],
                 v_spaces_to_split=1, h_spaces_to_split=1,
                 start_offset=5, end_offset=5,
                 multiple_val=False):
        self.horizontal_extractor = HorizontalData(self.validation_fun, specific_patterns=specific_patterns,multiple_val = multiple_val,
                                                   spaces_to_split=h_spaces_to_split)
        self.vertical_extractor = VerticalData(self.validation_fun, specific_patterns=specific_patterns,
                                               start_offset=start_offset, end_offset=end_offset,
                                               spaces_to_split= v_spaces_to_split, multiple_val=multiple_val)
        
    def __str__(self):
        return "number extractor"
        
        
    def validation_fun(self, number):
    
         char_prop, digit_prop = ut.char_digit_prop(number)
         if not re.search(r'\d',number):
            return False
         
         if number.isdigit() and len(number)==1:
             return True
         if len(number) < 3:
             return False
         if len(number) <=3 and char_prop > 0.9:
             return False
         if len(number) > 3 and char_prop >= 0.8:
             return False
         n_slash=ut.cal_char_occurence(number, '/')
         if n_slash >= 2:
             return False
         
         return True
     
    def get_horizontal_data(self, matched_key, current_line):
        data = self.horizontal_extractor.extract(matched_key, current_line)
       
        return data
    
    def get_vertical_data(self, lindex, matched_key, Lines):
        data = self.vertical_extractor.extract(lindex, matched_key, Lines)
        return data
        
    

        

if __name__=='__main__':
    patternpath = '/home/tacacs/Documents/Rahul/patterns/SC_due_date.txt'
    filepath = '/home/tacacs/Documents/Rahul/sample/test_sample/200712612912040-1_infoN.txt'
    order_number = NumberField() 
    data = order_number.get_data(filepath, patternpath)      
    print("order number: ", data)
        
         
         
