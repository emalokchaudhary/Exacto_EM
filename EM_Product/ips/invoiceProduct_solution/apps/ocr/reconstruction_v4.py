#import os
#path=r"D:\Users\51689383\Desktop\raushan\v8"
#lis=os.listdir(path)

f = open(r"./ocr/data_.txt", 'r')
words_set = set()
for x in f.readlines():
    words_set.add(x.strip())

def min_dist(a, b):
    n = len(a)
    m = len(b)
    lis = [[0 for x in range(m + 1)] for y in range(n + 1)]
    for i in range(n + 1):
        for j in range(m + 1):
            if i is 0:
                lis[0][j] = j
            elif j is 0:
                lis[i][0] = i
            elif a[i - 1] is b[j - 1]:
                lis[i][j] = lis[i - 1][j - 1]
            else:
                lis[i][j] = 1 + min(lis[i - 1][j - 1], lis[i][j - 1], lis[i - 1][j])
    return lis[n][m]

def getCorrected(word):

    if word in words_set:
        return word
    final_word = word
    final_score = len(word)
    for words in words_set:
        if min(len(word), len(words)) >= 3:

            if abs(len(word) - len(words)) <= 2:

                if min_dist(words, word) <= 2:
                    score = min_dist(words, word)

                    if score < final_score:
                        final_score = score
                        final_word = words
    return final_word


#for l in lis:
#    if l.endswith('_info.txt'):
#        path1=os.path.join(path,l)
#        p=r"D:\Users\51689383\Desktop\v8_data"
#        path2=os.path.join(p,l.replace('_info.txt','.txt'))

def reconstruct(path1):
    path2=path1.replace('_info.txt','.txt')
    f=open(path1,'r')
    file1=open(path2,'w')

    text = []
    line =[]
    left=[]
    top=[]
    description=[]
    for x in f.readlines():
        line.append(x)
    #lll=line
    description=[]
    top=[]
    left=[]
    for x in line:
        x=x.split('\t')
        a=[]
        a.extend([x[0]])
        a.extend(x[1].split())
        a.extend([x[2]])
        x=a
        if(len(x)==6):
            x=x[1:6]
            for i in range(0,4):
                x[i]=int(x[i])
            top.append(x[1])
            left.append(x[0])
            description.append(x)
    #print(description)
    description.sort(key=lambda z: z[1])

    if len(description)>0:
        font_size=sum(int(l[3]) for l in description)/float(len(description))
    else:
        font_size=21

    prev=description[0][1]

    Line_text=[]
    line=[]
    for des in description:
        if des[1]-prev<10:
            line.append(des)
            prev=des[1]
        else:
            Line_text.append(line)
            line=[]
            line.append(des)
            prev=des[1]
    Line_text.append(line)

    def todo_nhi_jodo(x):
        prev=-100
        prev_text=""
        new=[]
        z=[]
        z_new=[]
        for y in x:
            if(y[0]-prev <=5 and (len(y[4]) in [1,2] or len(prev_text) in[1,2])):
                prev=y[0]+y[2]
                prev_text=prev_text+y[4]

            elif(5<y[0]-prev <=30):
                prev=y[0]+y[2]
                prev_text=prev_text+" "+y[4]

            else:
                z=y[0:4]
                new.append(prev_text)
                z_new.append(z)
                prev_text=""
                prev=y[0]+y[2]
                prev_text=prev_text+y[4]

        new.append(prev_text)
        if len(new[0])==0:
            new=new[1:len(new)]

        text_detail=[]
        for i in range(0,len(new)):
            z_new[i].extend([new[i]])
            text_detail.append(z_new[i])

        return text_detail

    r_text=[]
    for line in Line_text:
        line.sort(key=lambda z: z[0])
        l=todo_nhi_jodo(line)
        r_text.append(l)

    def Find_text_index(l):
    #X-normalization
        x=l[0]
        scale_factor=float(font_size)/21
        sigma1=1573-166
        sigma1=sigma1*scale_factor
        mu1=(1573+166)/2
        mu1=mu1*scale_factor

        sigma2=133*scale_factor
        #sigma2=133*0.8
        mu2=sigma2/2
        indx=int(round(mu2+sigma2*(x-mu1)/float(sigma1)))
        return indx

    text=[]
    i=0
    for line in r_text:
        text_line=[]
        #line.sort(key=lambda z: z[0])
        for l in line:
            text_line.append((l[4],i,Find_text_index(l)))

        i+=1
        text.append(text_line)

    Line_by_line_text=text

    #All_text=[]

    for line in Line_by_line_text:
        text=""
        for tt in line:
            len1=len(text)
            white_spaces=tt[2]-len1
            """*****************************"""
            pp=tt[0].split()
            #print(pp,"******")
            w=""
            for p in pp:
                if len(p)>=4:
                    #print(p,'******')
                    w=w+" "+getCorrected(p)
                else:
                    w=w+" "+p
            #print(w,"##########")
            """*****************************"""

            text=text+" "+" "*white_spaces+w

        file1.write(text)
        file1.write('\n')
        #print(text)
        #print("\n")
    #print(file1)


        #All_text.append(text)
# path=r"D:\Users\51689383\Desktop\raushan\v8\300_11250008_139_107808__1712040900_1_info.txt"
# reconstruct(path)
