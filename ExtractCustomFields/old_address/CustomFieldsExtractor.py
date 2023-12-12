#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 20:41:15 2020

@author: tacacs
"""
import os
from configs import ExactoSettings
from . import utility as ut
from .NumberField import NumberField
from .DateField import DateField
from .EmailField import EmailField
from .PhoneNumberField import PhoneNumberField
from .NameField import NameField
from .TextField import TextField, TextFieldLong
from .AddressField import AddressField
from . import config as cnf


class CustomFieldsExtractor():

    def __init__(self,exacto_settings=None,user_id=None, config_id=None, folderpath=None):
        if exacto_settings:
            self.exacto_settings = exacto_settings
        else:
            self.exacto_settings=ExactoSettings()
        self.user_id = user_id
        self.config_id = config_id
        self.folderpath = folderpath


        
        

    @property
    def filepaths(self):
        return ut.read_all_files(self.folderpath)

    @property
    def pattern_folderpath(self):
        return os.path.join(self.exacto_settings.PATTERNS_PATH, self.user_id, self.config_id.lower())
    
    @property
    def pattern_files_dict(self):
        pattern_files = {}
        for file in os.listdir(self.pattern_folderpath):
            if file.startswith('SC') and file.endswith('.txt'):
                base_fname = os.path.splitext(file)[0]
                base_fname = base_fname.split('SC-')[1]
                file_path = os.path.join(self.pattern_folderpath, file)
                #print("file: ", file)
                field_name = self._get_field_name(file_path)
                #print("field names: ", field_name)
                pattern_files[base_fname] = [field_name, file_path]
        return pattern_files

    def _get_field_name(self, filepath):
       
        with open(filepath) as f:
            for line in f:
                line = line.strip('\n').strip()
                if line:
                    return line

        
        return "None"
    
     
    @staticmethod
    def get_extractor(field_name):
        extractor_name = field_name        
        if extractor_name in ['number', 'alphanumeric', 'amount', 'count']:
            extractor = NumberField()
        elif 'phone' in extractor_name:
            extractor = PhoneNumberField()
        elif 'email' in extractor_name:
            extractor = EmailField()
        elif 'name' in extractor_name:
            extractor = NameField()
        elif 'date' in extractor_name:
            extractor = DateField()
        elif extractor_name in ['longtext']:
            extractor = TextFieldLong()
        elif 'text' in extractor_name:
            extractor = TextField()
        elif 'address' in extractor_name:
            extractor = AddressField()
        else:
            extractor = NumberField()
        return extractor
            
    
    def _extract_single_custom_field(self, base_fname):
        value = ""
        field_name, patternpath = self.pattern_files_dict.get(base_fname)
        extractor = CustomFieldsExtractor.get_extractor(field_name)
        print(extractor)
        #extractor = NumberField()
        
        for filepath in self.filepaths:
            value = extractor.get_data(filepath, patternpath)
            value = value.strip()
            if value:
                return  value
        return  value
        
    
    def extract_custom_fields(self):
        final_dict = {}
        #print("pattern_files_dict ",self.pattern_files_dict)
        for base_fname in self.pattern_files_dict:
            value = self._extract_single_custom_field(base_fname)
            final_dict[base_fname] = [value, ""]
        return final_dict
                
            
    
    
if __name__=='__main__':
    folderpath = '/home/tacacs/Documents/Rahul/sample/test_sample'
    patterns_folderpath = '/home/tacacs/Documents/Rahul/patterns'
    extractor = CustomFieldsExtractor(folderpath, patterns_folderpath)
    print("pattern dict ", extractor.pattern_files_dict)
    custom_fields_dict = extractor.extract_custom_fields()
    print(custom_fields_dict)
        
        
    
