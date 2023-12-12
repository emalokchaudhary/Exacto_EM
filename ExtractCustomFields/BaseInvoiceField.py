#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 13:02:08 2020

@author: tacacs
"""


from abc import ABC, abstractmethod
from . import utility as ut
import re,os

class AbstractInvoiceField(ABC):
    
    
    
    @abstractmethod
    def validation_fun(self):
        pass
    
    @abstractmethod
    def get_horizontal_data(self, matched_key=None, current_line=None):
        '''
        define a method which tries to extract data from match string assuming the value is present in horizontal
        '''
        pass
    
    @abstractmethod
    def get_vertical_data(self, lindex=None, Lines=None):
        '''
        define a method which tries to extract data using match string considering the value to be present in vertical.
        '''
        pass
    def vartical_pattern_match(self,pattern,patternpath):
        
        varticall_path = os.path.join(os.getcwd(),'ExtractCustomFields')
        f = open(os.path.join(varticall_path,"vartical_preference.txt"),'r')
        liness = f.readlines()
        #print(liness,'######################')
        
        for lin in liness:
            #print(lin.lower(),'$$$$$$$$')
          #  print(patternpath.lower() + ' ' + pattern.lower() ,'patternnn pathh')
       
            if patternpath.lower() + ' ' + pattern.lower() in lin.lower():
                
                return True
        return False

    def _gen_req_line(self, Lines, patterns,patternpath):
        vartical_flag = False
        for pattern in patterns:
           for lindex, line in enumerate(Lines):
               c_pat = ut.create_compiled_pat(pattern, ignore_case=True)
               #print(c_pat)
               vartical_flag = self.vartical_pattern_match(pattern,patternpath)
               if c_pat.search(line):
                   matched_key = c_pat.search(line).group(0)
                   
                   yield(matched_key, line, lindex,vartical_flag)
        

    def get_data(self, filepath, patternpath):
        '''
        Attempt first to extract data from horizontal, then vertical
        '''
        #print(patternpath,'pattern_path')
        extracted_val = ""
        Lines = ut.read_lines(filepath)
        patterns = ut.get_pattern_list(patternpath)
        
        patterns = patterns[1:]
        try:
            if len(patterns) <=10:           # to accomodate active learning on priority basis only on custom fields done on 17-001-2021
                patterns = patterns[::-1]
            patterns = [p for p in patterns if not p.strip() == '']
        except:
            pass
        for matched_key, line, lindex,vartical_flag in self._gen_req_line(Lines, patterns,patternpath):
           
            if vartical_flag:
                
                extracted_val = self.get_vertical_data(lindex, matched_key, Lines)
                print(extracted_val,'vartical  extraction')
                if not extracted_val:
                    extracted_val = self.get_horizontal_data( matched_key, line)
                if extracted_val:
                    return extracted_val
            else:
                extracted_val = self.get_horizontal_data(matched_key, line)
                print(extracted_val,'horizontal extraction ')

                if not extracted_val:
                    extracted_val = self.get_vertical_data(lindex, matched_key, Lines)
                if extracted_val:
                    return extracted_val

            
        return extracted_val

