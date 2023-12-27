from ocr.reconstruction_v4 import reconstruct
class point:
    global padding
    padding = 10

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def __lt__(self, other):
        if abs(self.y - other.y) <= padding:
            return self.x <= other.x
        return self.y <= other.y
def getText(list_txt_co, seg_cordinates, seg_names, filename):
        #print(list_txt_co)
        dict1 = {}
        for x,y in zip(seg_names, seg_cordinates):
            #print(x,y)
            dict1[x] = y
        x=[]
        y=[]
        w=[]
        h=[]
        n=[]
        text=[]
        for a,b,c in list_txt_co:
            #print(a,b)
            text.append(a)
            #print(c)
            x.append(dict1[c[0]][0])
            y.append(dict1[c[0]][1])
            w.append(dict1[c[0]][2])
            h.append(dict1[c[0]][3])
            n.append(c[0])

        with open(filename, "w") as stream:
            for nn,xx,yy,ww,hh,nn,tt in zip(n,x,y,w,h,n,text):
                stream.write(str(nn)+"\t"+str(xx)+" "+str(yy)+" "+str(ww)+" "+str(hh)+"\t"+str(tt))
                stream.write('\n')
        reconstruct(filename)
        # txt=main_function(x,y,text)
        # for l in txt:
        #     print l
        # return txt
def main_function(X, Y, Text):
        l = []
        for i in range(len(X)):
            l.append(point(int(X[i]), int(Y[i]), Text[i]))
        l.sort()

        if len(l) is 0:
            return l
        Lines = {}
        line_num = 0
        min_x = l[0].x
        max_x = l[0].x
        Lines[0] = []
        Lines[0].append((l[0].x, l[0].text))

        for i in range(1, len(l)):
            if abs(l[i].y - l[i - 1].y) <= padding:
                Lines[line_num].append((l[i].x, l[i].text))
                min_x = min(min_x, l[i].x)
                max_x = max(max_x, l[i].x)
            else:
                line_num += 1
                Lines[line_num] = []
                Lines[line_num].append((l[i].x, l[i].text))
                min_x = min(min_x, l[i].x)
                max_x = max(max_x, l[i].x)
        diff = max_x - min_x
        Text = []
        for i in range(line_num + 1):
            line = ""
            for x, t in Lines[i]:
                normalize = int((x - min_x) * 100 // diff)
                if len(line) == 0:
                    line = " " * normalize + t
                else:
                    #print(len(line), normalize)
                    if (len(line)>= 400):
                        break
                    line += " " * abs(normalize - len(line)) + t

            Text.append(line)
            # print(line)
        return Text
