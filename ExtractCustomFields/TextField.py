from .NumberField import NumberField
from . import utility as ut
import re



class TextField(NumberField):
    
    def __init__(self):

        self.specific_patterns = []
        super(TextField, self).__init__(self.specific_patterns, v_spaces_to_split=2, h_spaces_to_split=2)

    def __str__(self):
        return "Text field extractor"

    def validation_fun(self, word):
        char_prop, digit_prop = ut.char_digit_prop(word)

        if len(word)>6 and len(word) <=10:
            if char_prop <= 0.6:
                return False
        if len(word) <= 6 and len(word)>3:
            if char_prop <= 0.5:
                return False
        if len(word) < 3:
            return False
        return True
    
    
    
class TextFieldLong(NumberField):
    
    def __init__(self):

        self.specific_patterns = []
        super(TextFieldLong, self).__init__(self.specific_patterns, v_spaces_to_split=2, h_spaces_to_split=2,  end_offset=-1)

    def __str__(self):
        return "Text field Long extractor"

    def validation_fun(self, word):
        word = word.strip(':').strip()
        char_prop, digit_prop = ut.char_digit_prop(word)
        print(char_prop,'----',word)
        if len(word) < 10:
            return False
        if char_prop < 0.75:
            return False
        
        return True
    
    
    
    
