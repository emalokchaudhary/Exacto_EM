import os


xml='Download (20).xml'
fileName='Download (20)'
pgnum=3
fw=open('DD.txt','w')
for i in range(1,pgnum+1):
	print i
	text= fileName+'-'+str(i)+'_1.txt'
	if os.path.isfile(text):
		f = open(text)
		lines= f.read()
		fw.write(lines)
	fw.write('\n\n')
fw.close()
