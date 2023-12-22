from collections import OrderedDict


def result_dict(final_dict,output):
    st_dict = {}
    print("final_dict : ",final_dict)
    print("output :",output)
    for sl in output['standard_list']:
        st_dict[sl['fields_name']] = final_dict['static'][sl['field_key']]
    stc_dict= {}
    for scl in output['standard_custom_list']:
        stc_dict[scl['fields_name']] = final_dict['static'][scl['mapped_field']]
    line_header = final_dict['dynamic'][0]
    for tcl in output['table_custom_list']:
        line_header = list(map(lambda x: x.replace(tcl['mapped_field'] , tcl['fields_name']), line_header)) 
    final_dict['dynamic'][0]=line_header
    final_static = st_dict.copy()
    final_static.update(stc_dict)
    result = {"static":final_static, "dynamic": final_dict['dynamic'] }
    return result


final_dict =  {"static": {"invoice_number": ["4313", "90.0"], "invoice_date": ["26/02/2021", "36.3"], "tax_amount": [" \u00a3300.00", "72.67"],
 "total_amount": [" 6,732.00", "58.39"], "company_name": ["Hanlon Computer Systems Ltd.", "53.19"], "shipping_amount": ["", "55.96"], "po_number":
 ["3101176793", "55.96"], "currency": ["\u00a3", "87.89"], 
"invoice_address": [": Old Oak & Park Royal DC Accounts Payable P.O. Box 45276", "94.93"], 
"delivery_address": [": Old Oak & Park Royal DC Accounts Payable P.O. Box 45276", "94.93"], "account_number": ["32840812", "90.37"],

 "net_amount": [" 6,732.00", "58.39"], "s_2": ["", ""], "s_3": ["Number", ""], "s_1": ["", ""], "invoice_type": ["PDF_File", "", ""], 
"bar_code": ["", "", ""], "qr_code": ["", "", ""], "file_name": ["90kjoikg35g.PDF", "", ""]},
 "dynamic": [["line_no", "order_number", "quantity", "unit", "description", "unit_price", "amount", "total_amount", "t_2", "t_1"], [["1", "", "0.20 system", "", "System sales, Hanlon Client (SR)", "", "\u00a3158.00", "", "", ""], ["2", "", "2.00 user", "user", "Licences, Hanlon Client (SR) user licence", "", "\u00a394.00", "", "", ""], ["3", "", "0.20", "", "Support, Hanlon Client (SR) software support", "", "\u00a374.00", "", "", ""], ["4", "", "2.00 page", "page", "Support, Hanlon Portal (Web Pages Hosting)", "", "\u00a3160.00", "", "", ""], ["5", "", "2.00 user", "user", "Support, Hanlon Client (SR) user support", "", "\u00a360.00", "", "", ""], ["6", "", "0.60 day", "day", "Consultancy, System implementation, including workshops", "", "\u00a378.00", "", "", ""], ["7", "", "1.00 day", "day", "Consultancy, Web site development", "", "\u00a3150.00", "", "", ""], ["8", "", "0.60 day", "day", "Training, Hanlon Client (SR) training", "", "\u00a378.00", "", "", ""], ["9", "", "0.20 module", "", "Modules, Hanlon Client (SR) - Skills & Vacancies module", "", "\u00a390.00", "", "", ""], ["10", "", "0.20 module", "", "Modules, Hanlon Client (SR) - Enterprise module", "", "\u00a3110.00", "", "", ""], ["11", "", "0.20 module", "", "Modules, Hanlon Client (SR) - Web reports module", "", "\u00a320.00", "", "", ""], ["12", "", "0.20 module", "", "Modules, Hanlon Client (SR) - Event Management module", "", "\u00a350.00", "", "", ""]]], "config_uuid": "xerox_po"}


output = {'standard_list'
: [OrderedDict([('fields_name', 'file name'), ('field_key', 'file_name'), ('field_type', 'S'), ('field_sequence', 1), ('mapped_field', 'file_name')]), OrderedDict([('fields_name', 'invoice number'), ('field_key', 'invoice_number'), ('field_type', 'S'), ('field_sequence', 2), ('mapped_field', 'invoice_number')]), OrderedDict([('fields_name', 'account number'), ('field_key', 'account_number'), ('field_type', 'S'), ('field_sequence', 3), ('mapped_field', 'account_number')]), OrderedDict([('fields_name', 'invoice date'), ('field_key', 'invoice_date'), ('field_type', 'S'), ('field_sequence', 4), ('mapped_field', 'invoice_date')]), OrderedDict([('fields_name', 'invoice type'), ('field_key', 'invoice_type'), ('field_type', 'S'), ('field_sequence', 5), ('mapped_field', 'invoice_type')])], 

'standard_custom_list': [OrderedDict([('fields_name', 'invoice amount'), ('field_key', 'invoice_amount'), ('field_type', 'SC'), ('field_sequence', 1), ('mapped_field', 's_1')]), OrderedDict([('fields_name', 'invoice name'), ('field_key', 'invoice_name'), ('field_type', 'SC'), ('field_sequence', 2), ('mapped_field', 's_2')]), OrderedDict([('fields_name', 'invoice'), ('field_key', 'invoice'), ('field_type', 'SC'), ('field_sequence', 3), ('mapped_field', 's_3')])], 

'table_list': [OrderedDict([('fields_name', 'line no'), ('field_key', 'line_no'), ('field_type', 'T'), ('field_sequence', 1), ('mapped_field', 'line_no')]), OrderedDict([('fields_name', 'order number'), ('field_key', 'order_number'), ('field_type', 'T'), ('field_sequence', 2), ('mapped_field', 'order_number')]), OrderedDict([('fields_name', 'description'), ('field_key', 'description'), ('field_type', 'T'), ('field_sequence', 3), ('mapped_field', 'description')]), OrderedDict([('fields_name', 'unit price'), ('field_key', 'unit_price'), ('field_type', 'T'), ('field_sequence', 4), ('mapped_field', 'unit_price')]), OrderedDict([('fields_name', 'amount'), ('field_key', 'amount'), ('field_type', 'T'), ('field_sequence', 5), ('mapped_field', 'amount')]), OrderedDict([('fields_name', 'unit'), ('field_key', 'unit'), ('field_type', 'T'), ('field_sequence', 6), ('mapped_field', 'unit')]), OrderedDict([('fields_name', 'quantity'), ('field_key', 'quantity'), ('field_type', 'T'), ('field_sequence', 7), ('mapped_field', 'quantity')]), OrderedDict([('fields_name', 'total amount'), ('field_key', 'total_amount'), ('field_type', 'T'), ('field_sequence', 8), ('mapped_field', 'total_amount')])], 

'table_custom_list': [OrderedDict([('fields_name', 'net unit'), ('field_key', 'net_unit'), ('field_type', 'TC'), ('field_sequence', 1), ('mapped_field', 't_1')]), OrderedDict([('fields_name', 'net cost'), ('field_key', 'net_cost'), ('field_type', 'TC'), ('field_sequence', 2), ('mapped_field', 't_2')])]}
filtered_static_dict = {}
filtered_static_dict = result_dict(final_dict,output)
print("filtered_static_dictfiltered_static_dict", filtered_static_dict)


line_header = ['no_data']

#line_header = final_dict['dynamic'][0]

table_header_list = []
for tln in output['table_list']:
    print("tln",tln)
    table_header_list.append(tln['field_key'])

for tcn in output['table_custom_list']:
    table_header_list.append(tcn['field_key'])

if 'no_data' in line_header:
    line_header = table_header_list


print(table_header_list)


