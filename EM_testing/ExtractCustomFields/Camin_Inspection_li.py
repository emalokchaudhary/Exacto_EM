import re
file=open(r'/datadrive/EM_Product/ips/invoiceProduct_solution/output_data/1234/539888EXXM00-12rp0jpa6220-38-08-0538.text','r',encoding='windows-1258')
read=file.read()
lines=read.split('\n')
for n,line in enumerate(lines):
    a = re.search('Sample\s*NÂ°\s*[:]',line)
    if a:
        for i in range(n+3,len(lines)):
            b = re.search('The results apply to the samples as received and specifically to the items listed on this certificate.',lines[i])
            if b:
                break
            else:
                print(lines[i])
                continue




