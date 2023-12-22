#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 16:07:27 2020

@author: tacacs
"""
import re
from . import utility as ut

class VerticalData():
    
    def __init__(self, validation_func,  specific_patterns=[], start_offset=5, end_offset=5,
                 spaces_to_split=1, multiple_val=False, reverse=False):
        
        self.validation_func = validation_func
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.reverse = reverse
        self.specific_patterns = specific_patterns
        self.spaces_to_split = spaces_to_split
        self.multiple_val=multiple_val
        
        
    def _calculate_offset(self, pattern, line, next_line):
        cmp_pattern = ut.create_compiled_pat(pattern)
        start, end = cmp_pattern.search(line).span()
        #print("end offset from span: ", end)
        start = max(0,start-self.start_offset)
        if self.end_offset==-1:
            end = len(next_line)-1
        else:
            end = min(len(next_line), end + self.end_offset)
            #print("len of next_line ", len(next_line))
            #print("end indexx afterrr adding offset" , end)
        return start, end
        
    def _get_vertical_lines(self, lindex, Lines):
        line1  = ""
        line2 = ""
        vlines = []
        if self.reverse:
            try:
                line1 = Lines[lindex-1]
            except:
                line1 = ""
            try:
                line2 = Lines[lindex-2]
            except:
                line2 = ""
        
        else:
            try:
                line1 = Lines[lindex+1]
            except:
                line1 = ""
            try:
                line2 = Lines[lindex+2]
            except:
                line2 = ""
        if line1:
            vlines.append(line1)
        if line2:
            vlines.append(line2)
        return vlines

    def _get_multiple_val_words(self, vwords_to_look):
        val_words = []
        for vword in vwords_to_look:
            if self.validation_func(vword):
                val_words.append(vword)
        if val_words:
            return " ".join(val_words)
        return ""
    
    def _get_validated_words(self, vline):
        val = ""
        split_pat = " "*self.spaces_to_split
        vwords = vline.split(split_pat)
        vwords = [v for v in vwords if v not in [',', ':', '#']]
        vwords = [vword for vword in vwords if vword]
        #print("vertical words:  ", vwords)
        vlen = len(vwords)
        if self.multiple_val:
            end_index = min(vlen, 3)
            vword_to_look = vwords[:end_index]
            val = self._get_multiple_val_words(vword_to_look)
            if val:
                return val
        if vlen ==3:
            if self.validation_func(vwords[1]):
                val = vwords[1]
                return val
            elif self.validation_func(vwords[0]):
                val = vwords[0]
                return val
            elif self.validation_func(vwords[-1]):
                val = vwords[-1]
                return val
            else:
                return ""
        elif vlen==2:
            if self.validation_func(vwords[-1]):
                val = vwords[-1]
                return val
            elif self.validation_func(vwords[0]):
                val = vwords[0]
                return val
            else:
                return ""
        elif vlen==1:
            if self.validation_func(vwords[0]):
                val = vwords[0]
                return val
            else:
                return ""
        elif vlen > 3:
            if self.validation_func(vwords[0]):
                val = vwords[0]
                return val
            elif self.validation_func(vwords[1]):
                val = vwords[1]
                return val
            else:
                return val
        else:
            return val
        
    def _get_data_from_specific_pattern(self, vlines):
        val = ''
        for pat in self.specific_patterns:
            for vline in vlines:
                if re.search(pat, vline):
                    val = re.search(pat, vline).group(0)
                if val:
                    return val
        return val
        
    def extract(self, lindex, matched_key, Lines):
        val = ""
        vlines = self._get_vertical_lines(lindex, Lines)
        #print("vertical lines found under match: ", vlines)
        if self.specific_patterns:
            val = self._get_data_from_specific_pattern(vlines)
            if val:
                return val
            
        for vline in vlines:
            start, end = self._calculate_offset(matched_key, Lines[lindex], vline)
            vline = vline[start : end]
            #print("len of vlaine  ", len(vline))
            #print("req vlines: ", vline)
            val = self._get_validated_words(vline)
            if val:
                return val
        return val
        
        
                

        
        
    
        
        
        
        
        
    
        
        
    
        