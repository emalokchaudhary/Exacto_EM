from .BaseInvoiceField import AbstractInvoiceField
from . import utility as ut
import re



class AddressField(AbstractInvoiceField):
    def __init__(self):
        self.specific_patterns = []
        super(AddressField, self).__init__()

    def __str__(self):
        return "Address field extractor"
    def get_horizontal_data(self, matched_key=None, current_line=None):
        '''
        define a method which tries to extract data from match string assuming the value is present in horizontal
        '''
        pass

    def get_vertical_data(self, lindex=None,matched_key = None,Lines=None):
        address_string = ''
        try:
            [a,b] = re.search(matched_key,Lines[lindex],re.IGNORECASE).span()

            for i in range(lindex+1,lindex+5):
                # print(Lines[i].strip(),'lines')
                starting_index = max(0,a-1)
                ending_index = min(len(Lines[i]),b+15)
                address_info = Lines[i][starting_index:ending_index].strip()
                # print(address_info,'address information')
                t_address_string = address_info.split(3*' ')[0]
                if t_address_string:
                    address_string = address_string + ' '+ t_address_string
            address_string = address_string.strip()
        except:
            address_string = ''
        print(address_string,'final ')
        return address_string
    def validation_fun(self, number):

        return True