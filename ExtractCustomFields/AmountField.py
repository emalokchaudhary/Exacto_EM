__author__ = 'boddu.prabh'


from .NumberField import NumberField
import re

class AmountField(NumberField):
    def __init__(self):
        self.specific_patterns = []
        super(AmountField, self).__init__(specific_patterns=[],
                 v_spaces_to_split=2, h_spaces_to_split=2,
                 multiple_val=False)
    def __str__(self):
        return "name extractor"

if __name__=='__main__':
    pass

