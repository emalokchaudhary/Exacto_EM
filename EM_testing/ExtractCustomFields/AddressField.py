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
            count = 0
            try:
                address_string = address_string + Lines[lindex][b:min(len(Lines[lindex]),b+10)]
            except:
                address_string = ''
            for i in range(lindex+1,lindex+8):
                # print(Lines[i].strip(),'lines')
                if len(Lines[i]) < b + 15:
                    Lines[i] = Lines[i][:] + (b + 15 - len(Lines[i])) * ' '

                starting_index = max(0, a - 1)
                ending_index = min(len(Lines[i]), b + 15)
                space_check = Lines[i][starting_index:ending_index]
                space_check_1 = Lines[i+1][starting_index:ending_index]
                space_check_2 = Lines[i+2][starting_index:ending_index]
                space_final_check = space_check + space_check_1 + space_check_2
                if len(space_final_check.strip()) == 0:
                    print(space_check_2,'More than 2 spaces')
                    break
                if(count < 5):
                    address_info = Lines[i][starting_index:ending_index].strip()
                   # print(address_info,'address information')
                    t_address_string = address_info.split(4*' ')[0]
                    if t_address_string:
                        count = count + 1
                        address_string = address_string + ' '+ t_address_string
            address_string = address_string.strip()
        except:
            address_string = ''
       # print(address_string,'final ')
        return address_string.replace('/n','').replace(':','').strip()
    def validation_fun(self, number):

        return True
