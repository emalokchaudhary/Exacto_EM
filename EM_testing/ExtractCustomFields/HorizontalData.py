
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 13:44:01 2020

@author: tacacs
"""
import re
from . import utility as ut

class HorizontalData():
    
    def __init__(self,  validation_func, specific_patterns=[], max_words_to_look=3, spaces_to_split=1, multiple_val = True,data_seperator=[':', '#']):
        
        self.validation_func = validation_func
        self.spaces_to_split = spaces_to_split
        self.multiple_val = multiple_val
        self.max_word_to_look = max_words_to_look
        self.data_seperator = data_seperator
        self.specific_patterns = specific_patterns
        
    def _get_matchstring(self, key, line):
        
        matched_keyword = key
        
        cmp_key = ut.create_compiled_pat(key)
        if cmp_key.search(line):
            matched_keyword = cmp_key.search(line).group(0)
            matched_keyword = matched_keyword.strip()
            #print( 'matched keyword  ********  ', matched_keyword)
            match_string_pattern = matched_keyword + r'.*'
            matchstring = re.search(match_string_pattern, line).group(0)
            #print("matrchstring befor strip ***:   ", matchstring)
            matchstring = matchstring.replace(matched_keyword, "")
            matchstring = matchstring.strip()
            #print("**matchstring**  : ", matchstring)
            return matchstring
        return line
        
    
    def _get_validated_words(self, matchstring):
        matchwords = matchstring.split(" "*self.spaces_to_split)
        matchwords = [w for w in matchwords if w]
        validated_words = []
        end_index = min(len(matchwords), self.max_word_to_look)
        matchwords = matchwords[:end_index]
        matchwords = [w.strip(':') for w in matchwords]
        for word in matchwords:
            if self.validation_func(word):
                validated_words.append(word)
        
        if validated_words and self.spaces_to_split>1:
            return validated_words[0]
            
        
        if validated_words and self.multiple_val:
            return " ".join(validated_words)
        if len(validated_words)==0:
            return ''
        return validated_words[0]
        
        
          
    
    def _field_data_seperator(self, matchstring):
        for sep in self.data_seperator:
            if sep in matchstring:
                splitted_words = matchstring.split(sep)
                if len(splitted_words) > 1:
                    return splitted_words[1]
        return ""
        
    def _get_data_from_specific_pattern(self, matchstring):
        val = ''
        for pat in self.specific_patterns:
            if re.search(pat, matchstring):
                val = re.search(pat, matchstring).group(0)
            if val:
                return val
        return val
                
    
    def extract(self, keyword, line, data_seperator=False):
        
        matchstring = self._get_matchstring(keyword, line)
        
        value = ''
        if self.specific_patterns:
            value = self._get_data_from_specific_pattern(matchstring)
            if value:
                return value
        
        if data_seperator:
            value = self.field_data_seperator(matchstring)
      
        if not value:
            value = self._get_validated_words(matchstring) 
        
        return value
            
            
    
