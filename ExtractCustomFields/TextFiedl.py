from .NumberField import NumberField
from . import utility as ut
import re



class TextField(NumberField):
    
    def __init__(self):

        self.specific_patterns = []
        super(TextField, self).__init__(self.specific_patterns, v_spaces_to_split=2, h_spaces_to_split=2)

    def __str__(self):
        return "Text field extractor"

    def validation_fun(self, number):
        char_prop, digit_prop = ut.char_digit_prop(number)
        if char_prop < 0.8:
            return False
        if len(number) < 3:
            return False
        return True