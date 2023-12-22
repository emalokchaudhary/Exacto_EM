from shapely.geometry import Polygon
import numpy as np
import cv2
import os
import traceback
import ocr.postLocalization as pl
from matplotlib import pyplot as plt

def intersection_of_textboxes(g, p,THRESHOLD_BTW_LINES):
    if abs(g[1] - p[1]) > THRESHOLD_BTW_LINES + 5:
        return -1

    g = Polygon(g.reshape((4, 2)))
    p = Polygon(p.reshape((4, 2)))
    if not g.is_valid or not p.is_valid:
        return 0
    inter = Polygon(g).intersection(Polygon(p)).area
    return inter


def merge_textboxes(g, p):
    x1 = p[0]
    if g[0] < x1:
        x1 = g[0]

    y1 = p[1]
    if g[1] < y1:
        y1 = g[1]

    x2 = g[4]
    if p[4] > x2:
        x2 = p[4]

    y2 = g[5]
    if p[5] > y2:
        y2 = p[5]

    g = np.array([x1, y1, x2, y1, x2, y2, x1, y2], dtype=np.float32)
    return g


def merge_overlapping_textboxes(polys,THRESHOLD_BTW_LINES):
    S = []
    p = None
    for g in polys:
        if p is not None and intersection_of_textboxes(g, p,THRESHOLD_BTW_LINES) > 0:
            p = merge_textboxes(g, p)
        else:
            if p is not None:
                S.append(p)
            p = g
    if p is not None:
        S.append(p)

    if len(S) == 0:
        return np.array([])

    polys_merged = np.array(S)

    cord_list = []
    for i,poly in enumerate(polys_merged):
        x = int(poly[0])
        y = int(poly[1])
        x1 = int(poly[4])
        y1 = int(poly[5])

        if x < 0:
            x = 0

        if y < 0:
            y = 0

        if x1 < 0:
            x1 = 0

        if y1 < 0:
            y1 = 0

        cord_list.append([i+1, x, y, x1 - x, y1 - y])
        # print([i+1, x, y, x1 - x, y1 - y])

    return cord_list


def find_bound_x_dir(img, bound, direction, y_start, y_end, width, thres):
    try:
        ht, wd = img.shape[:2]

        # 1 for forward
        # -1 for back
        i = direction

        empty_space = 0
        max_traversal_allowed = width
        box_height = y_end - y_start
        while True:
            if 0 <= bound + i < wd:
                black_pixels = (np.where(img[y_start:y_end, bound + i] < 128)[0]).size
                if black_pixels >= int(0.9*box_height):
                    try:
                        top_black = img[y_start-4, bound + i]
                        if top_black<128:
                            i = i - direction * empty_space
                            break
                    except:
                        pass
                        print("exception")
                        i = i - direction*empty_space
                        break

                if black_pixels <= int(0.1*box_height):
                    empty_space += 1
                    if empty_space > thres:
                        i = i - direction*(empty_space - 2)
                        break
                else:
                    if empty_space > 0:
                        empty_space = 0

                i = i + direction
            else:
                i = i - direction
                break

        if width < 4 * thres:
            max_traversal_allowed = 4 * thres

        if abs(i) > max_traversal_allowed:
            i = int(max_traversal_allowed)
            i = i * direction

        bound += i
        return bound
    except:
        return bound


def find_bound_y_dir(img, bound, direction, x_start, x_end, height_limit):
    try:
        ht, wd = img.shape[:2]

        # 1 for down
        # -1 for up
        i = direction
        box_width = x_end - x_start
        while True:
            if 0 <= bound + i < ht:
                black_pixels = (np.where(img[bound + i, x_start:x_end] < 128)[0]).size

                if black_pixels >= box_width:
                    break

                if black_pixels <= 0:#int(0.07*box_width):
                    break

                i = i + direction
            else:
                i = i - direction
                break

        if abs(i) > height_limit:
            i = height_limit
            i = i * direction

        bound += i
    except:
        pass

    return bound


def dist_btw_words(g,p,moving_center):
    if len(moving_center)==0:
        p1 = p[2] + int(p[4] / 2)
    else:
        p1 = moving_center[0]

    p2 = g[2] + int(g[4] / 2)


    del moving_center[:]
    moving_center.append((p1+p2)/2)

    return abs(p1 - p2)


def draw_illu(illu, rst):
    img = illu.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for t in rst['text_lines']:
        d = np.array([t['x0'], t['y0'], t['x1'], t['y1'], t['x2'],
                      t['y2'], t['x3'], t['y3']], dtype='int32')
        d = d.reshape(-1, 2)
        cv2.polylines(illu, [d], isClosed=True, color=(0, 255, 0), thickness=2)

        (x, y, w, h) = cv2.boundingRect(d)
        img[y:y + h, x:x + w] = 255
        # cv2.putText(illu, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        # cv2.rectangle(illu, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return illu, img


def create_line_groups(update_list,THRESHOLD_BTW_LINES):
    lines_group = []
    line = []
    p = None
    moving_center = []
    for g in update_list:
        if p is not None and dist_btw_words(g, p, moving_center) < THRESHOLD_BTW_LINES:
            line.append(g[0])
        else:
            if p is not None:
                lines_group.append(line)
                line = []
                del moving_center[:]
                # moving_center.clear()
            p = g
            line.append(p[0])
    if len(line) != 0:
        lines_group.append(line)

    return lines_group


def merge_near_contours(fin_blobs,thres):
    fin_blobs = sorted(fin_blobs, key=lambda x: (x[1], x[2]))

    fin_blobs_merged = []

    try:
        prev = fin_blobs[0]
        for i in range(1, len(fin_blobs)):
            [num1, x1, y1, w1, h1] = prev
            [num2, x2, y2, w2, h2] = fin_blobs[i]


            upper = y1 + h1
            lower = y2

            if y2 < y1 :
                upper = y2 + h2
                lower = y1


            if (x2 - (x1 + w1)) < thres and upper - lower > 0:
                # px1 = 0
                # px2 = 0
                # py1 = 0
                # py2 = 0

                px1 = x1
                if x2 < x1:
                    px1 = x2

                px2 = x2 + w2
                if px2 < x1 + w1:
                    px2 = x1 + w1

                py1 = y1
                if y2 < py1:
                    py1 = y2

                py2 = y2 + h2
                if py2 < y1 + h1:
                    py2 = y1 + h1

                prev = [num1, px1, py1, px2 - px1, py2 - py1]

                # merge
                pass
            else:
                fin_blobs_merged.append([num1, x1, y1, w1, h1])
                prev = [num2, x2, y2, w2, h2]

        fin_blobs_merged.append(prev)
    except:
        pass

    return fin_blobs_merged


def post_nms(img, rst):
    THRESHOLD_WOB = 0.5  #Threshold for detecting white words on black background

    img_ht, img_wd = img.shape[:2]

    cord_list = []
    height = []
    blanked = img.copy()
    for t in rst['text_lines']:
        d = np.array([t['x0'], t['y0'], t['x1'], t['y1'], t['x2'],
                      t['y2'], t['x3'], t['y3']], dtype='int32')
        d = d.reshape(-1, 2)

        (x, y, w, h) = cv2.boundingRect(d)
        if h > int(w*1.5):
            continue
        cord_list.append([x, y, w, h])
        height.append(h)

    if len(cord_list) == 0:
        print("No text boxes found")
        return []

    cord_list = sorted(cord_list, key=lambda x: (x[1], x[0]))
    height.sort()
    height = np.array(height)
    height = np.unique(height)
    ht = height[int(height.size / 2)]

    THRESHOLD_BTW_LINES = int(0.4 * ht)
    HORIZONTAL_WORD_TOLERANCE = ht
    VERTICAL_WORD_TOLERANCE = int(0.2*ht)
    VERTICAL_WORD_TOLERANCE_up = int(0.06*ht)

    # print(height)
    #print("THRESHOLD_BTW_LINES Value : ",THRESHOLD_BTW_LINES) ##keep this parameter small, if you increase this parameter you risk merging two lines
    #print("HORIZONTAL_WORD_TOLERANCE Value : ",HORIZONTAL_WORD_TOLERANCE)
    #print("VERTICAL_WORD_TOLERANCE Value : ",VERTICAL_WORD_TOLERANCE)

    update_list = []
    cord_dict = {}
    num = 1
    for [x, y, w, h] in cord_list:
        update_list.append([num, x, y, w, h])
        cord_dict[num] = [x, y, w, h]
        cv2.rectangle(blanked, (x, y), (x + w, y + h), (255, 255, 255), -1)
        num += 1

    lines_group = create_line_groups(update_list,THRESHOLD_BTW_LINES)

    # fully_updated = []
    fin_num = 1
    polys = []
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blanked = cv2.cvtColor(blanked,cv2.COLOR_BGR2GRAY)

    for line in lines_group:
        # print(line)
        line_sub = []
        for num in line:
            line_sub.append(cord_dict[num])
        line_sub = sorted(line_sub, key=lambda x: (x[0]))

        for [x, y, w, h] in line_sub:
            minX = x
            maxX = x + w
            minY = y
            maxY = y + h

            try:
                margin = 5
                black = np.where(img[y - margin:y + h + margin, x - margin:x + w + margin] < 128)[0]
                black_density = float(black.size) / ((w + 2 * margin) * (h + 2 * margin))
            except:
                black = np.where(img[y:y + h, x:x + w] < 128)[0]
                black_density = float(black.size) / (w * h)


            if black_density <= THRESHOLD_WOB:
                temp_maxX = find_bound_x_dir(blanked, x + w,  1, y, y + h, w, HORIZONTAL_WORD_TOLERANCE)
                temp_minX = find_bound_x_dir(blanked, x    , -1, y, y + h, w, HORIZONTAL_WORD_TOLERANCE)

                if 0 <= temp_maxX < img_wd:
                    maxX = temp_maxX
                if 0 <= temp_minX < img_wd:
                    minX = temp_minX

                temp_maxY = find_bound_y_dir(img, maxY,  1, x, x + w, VERTICAL_WORD_TOLERANCE)
                temp_minY = find_bound_y_dir(img, minY, -1, x, x + w, VERTICAL_WORD_TOLERANCE_up)

                if 0 <= temp_maxY < img_ht:
                    maxY = temp_maxY
                if 0 <= temp_minY < img_ht:
                    minY = temp_minY
            else:
                #print("image num :", fin_num, "black density : ",float("{0:.2f}".format(black_density)))
                # img1 = cv2.bitwise_not(img[minY:maxY, minX:maxX])
                # img[minY:maxY, minX:maxX] = img1
                pass

            x = minX
            y = minY
            w = maxX - x
            h = maxY - y

            polys.append([x, y, x + w, y, x + w, y + h, x, y + h])

            # fully_updated.append([fin_num, x, y, w, h])
            fin_num += 1

    polys_merged = merge_overlapping_textboxes(np.array(polys, dtype=np.float32),THRESHOLD_BTW_LINES)

    cord_dict_temp = {}
    for [num, x, y, w, h] in polys_merged:
        cord_dict_temp[num] = [x, y, w, h]

    lines_group = create_line_groups(polys_merged, int(0.1 * ht))

    fin_cords = []
    fin_num = 0
    for line in lines_group:
        line_sub = []
        for num in line:
            [x, y, w, h] = cord_dict_temp[num]
            line_sub.append([num, x, y, w, h])
        line_sub = sorted(line_sub, key=lambda x: (x[0]))
        line_sub = merge_near_contours(line_sub, int(0.1*ht))

        for [num, x, y, w, h] in line_sub:
            fin_cords.append([fin_num, x, y, w, h])
            fin_num += 1

    return fin_cords


def crop_textboxes(output_path, img, cord_list, flnm):
    illu = img.copy()
    illu2 = img.copy()
    illu3 = img.copy()


    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blank = img.copy()
    orig = img.copy()

    try:
        nnum = 0
        height = []
        for [num, x, y, w, h] in cord_list:
            # cv2.putText(illu, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.rectangle(illu, (x, y), (x+w, y+h), (0, 255, 0), 2)
            blank[y:y + h, x:x + w] = 255
            height.append(h)
            nnum = max(nnum,num)

        # TODO: can be improved based on uniqueness and also the max no of same height entries
        if len(height) == 0:
            return []
        height.sort()
        ht = height[int((len(height) - 1) / 2)]

        # cv2.imwrite(os.path.join(output_path, 'east_detected.jpg'), illu)
        # cv2.imwrite(os.path.join(output_path, 'blank.jpg'), blank)

        blanked = blank.copy()

        blank = pl.detect_salt_and_pepper_noise(blank,3)
        pcord = pl.lineSmorph(blank, nnum+1,illu2,height,output_path,0)

        for [num, x, y, w, h] in pcord:
            cv2.putText(illu, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.rectangle(illu, (x, y), (x+w, y+h), (255, 0, 0), 2)
            blanked[y:y + h, x:x + w] = 255

        cv2.imwrite(os.path.join(output_path, 'detected.jpg'), illu)
        cv2.imwrite(os.path.join(output_path, 'blanked.jpg'), blanked)

        poly_fin = merge_stages(cord_list, pcord,int(0.4*ht))
        illu4 = illu3.copy()
        for [num, x, y, w, h] in poly_fin:
            cv2.putText(illu4, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.rectangle(illu4, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imwrite(os.path.join(output_path, 'merged_fin.jpg'), illu4)

        npredRes,ninfo = postBreak(img,poly_fin)
        ocr_inputs = saveResult(npredRes, ninfo, illu3.copy(), output_path,ht,flnm)
        return ocr_inputs,blanked
    except:
        print('Error in crop_textboxes', traceback.print_exc())


def merge_stages(cord_first,cord_second,THRESHOLD_BTW_LINES):
    cord_list = cord_first + cord_second
    cord_list = sorted(cord_list, key=lambda x: (x[2], x[1]))

    update_list = []
    cord_dict = {}
    num2 = 1
    for [num,x, y, w, h] in cord_list:
        update_list.append([num2, x, y, w, h])
        cord_dict[num2] = [x, y, w, h]
        num2 += 1

    lines_group = create_line_groups(update_list, THRESHOLD_BTW_LINES)
    fin_num = 1
    polys = []
    for line in lines_group:
        # print(line)
        line_sub = []
        for num in line:
            line_sub.append(cord_dict[num])
        line_sub = sorted(line_sub, key=lambda x: (x[0]))

        for [x, y, w, h] in line_sub:
            polys.append([x, y, x + w, y, x + w, y + h, x, y + h])
            fin_num += 1

    polys_merged = merge_overlapping_textboxes(np.array(polys, dtype=np.float32), THRESHOLD_BTW_LINES)

    return polys_merged


def postBreak(img,resList):
    nimgsDict = {}
    npred = []
    for [num, x, y, w, h] in resList:
        num = str(num)
        imgC = img[y:y + h, x:x + w]

        try:
            margin = 5
            black = np.where(img[y - margin:y + h + margin, x - margin:x + w + margin] < 128)[0]
            black_density = float(black.size) / ((w + 2 * margin) * (h + 2 * margin))
        except:
            black = np.where(img[y:y + h, x:x + w] < 128)[0]
            black_density = float(black.size) / (w * h)

        if black_density > 0.5:
            #print("image num :", num, "black density : ", float("{0:.2f}".format(black_density)))
            imgC = cv2.bitwise_not(img[y:y + h, x:x + w])

        thresh = cv2.threshold(imgC, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


        h,w = thresh.shape[:2]
        som = list(thresh.sum(axis=0) / 255)
        soh = list(thresh.sum(axis=1) / 255)

        i1=0;h1=h
        while i1<h and soh[i1]==w:
            h1-=1
            i1+=1
        i1=h-1
        while i1>=0 and soh[i1]>=w-6:
            h1-=1
            i1-=1

        if h1<=0:
            h1=h

        extra_margin = 0

        if h1<20:
            gap=8 + extra_margin
        elif h1>=20 and h1<=24:
            gap=9 + extra_margin
        elif h1>24 and h1<=26:#27-32
            gap=12 + extra_margin
        elif h1>26 and h1<=36:
            gap=14 + extra_margin
        elif h1>36 and h1<=40:
            gap=15 + extra_margin
        elif h1>40 and h1<=44:
            gap=17 + extra_margin
        elif h1>44 and h1<=48:
            gap=18 + extra_margin
        elif h1>48 and h1<=50:
            gap=22 + extra_margin
        else:
            gap=24 + extra_margin
	#print("num : ",num," gap : ",gap)
        subNum=0
        ct=0
        pre=0
        i=0
        while i<w:
            if som[i]==h and ct==0:
                post=i
                while i<w and som[i]==h:
                    ct+=1
                    i+=1
                if ct>=gap and pre!=post:
                    newNum=num+'_'+str(subNum)
                    newImg=thresh[:,pre:post]
                    hn,wn=newImg.shape[:2]
                    i1=0
                    while i1<wn and som[pre+i1]==hn:
                       i1+=1
                    i2 = 0
                    while i2 < wn and som[post - i2] == hn:
                       i2 += 1
                    if wn<=15:
                        dt=som[pre:post]

                        dtL=[1 for v in dt if hn-v<=12]
                        dL=len(dtL)
                        if dL>=wn-3:
                            for s in range(0,subNum):
                                delNm=num+'_'+str(s)
                                del nimgsDict[delNm]
                                last=npred[-1]
                                if last[0].startswith(num+'_'):
                                    del npred[-1]
                            pre=0;subNum=0
                            break
                    nimgsDict[newNum]=newImg
                    npred.append([newNum,x+pre+i1,y,post-pre-i1-i2,h])
                    pre=i-1
                    subNum+=1
                    i-=1
                ct=0
            i+=1

        if pre<w-1:
            newNum=num+'_'+str(subNum)
            newImg=thresh[:,pre:w]
            hn, wn = newImg.shape[:2]
            i1 = 0
            while i1 < wn and som[pre + i1] == hn:
                i1 += 1
            i2 = 0
            while i2 < wn and som[w-1 - i2] == hn:
                i2 += 1
            nimgsDict[newNum]=newImg
            npred.append([newNum,x+pre+i1,y,w-pre-i1-i2,h])

    return npred,nimgsDict


def saveResult(result, imgs_dict, img, output_path,avgHt,fnm):
    cord_path = os.path.join(output_path, 'file.txt')
    wfile = open(cord_path, 'w')
    wfile.write('Num\tx\ty\tw\th\n')
    ty_name = []
    ty_imgs = []
    ty_cord = []

    tyPath = os.path.join(output_path, 'typed')
    for [num, x, y, w, h] in result:
        thresh = imgs_dict[num]
        h, w = thresh.shape[:2]

        if h>8 and w>8:
            wfile.write(str(num) + '\t' + str(int(x)) + '\t' + str(int(y)) + '\t' + str(int(w)) + '\t' + str(int(h)) + '\n')
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.imwrite(os.path.join(tyPath, str(num) + '.png'), thresh)
            ty_name.append(str(num) + '.png')
            ty_imgs.append(thresh)
            ty_cord.append([x, y, w, h])
            #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.putText(img, str(num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
    cv2.imwrite(os.path.join(output_path,'final.png'),img)
    return [ty_name, ty_imgs, ty_cord, [], [], []]

