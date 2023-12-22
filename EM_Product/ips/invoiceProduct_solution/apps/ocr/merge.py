import os,shutil
import numpy as np
from shapely.geometry import Polygon
from platform import python_version

def intersection(g, p):
    g = Polygon(g[:8].reshape((4, 2)))
    p = Polygon(p[:8].reshape((4, 2)))
    if not g.is_valid or not p.is_valid:
        return 0
    inter = Polygon(g).intersection(Polygon(p)).area
    union = g.area + p.area - inter
    if union == 0:
        return 0
    else:
        return inter/union

def weighted_merge(g, p):
    g[:8] = (g[8] * g[:8] + p[8] * p[:8])/(g[8] + p[8])
    g[8] = (g[8] + p[8])
    return g

def merge1(S, thres):
    order = np.argsort(S[:, 8])[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        ovr = np.array([intersection(S[i], S[t]) for t in order[1:]])
        inds = np.where(ovr <= thres)[0]
        order = order[inds+1]
    return S[keep]

def merge_main_win(polys, thres=0.3, precision=10000):
    S = []
    p = None
    for g in polys:
        if p is not None and intersection(g, p) > thres:
            p = weighted_merge(g, p)
        else:
            if p is not None:
                S.append(p)
            p = g
    if p is not None:
        S.append(p)
    if len(S) == 0:
        return np.array([])
    return merge1(np.array(S), thres)

    # from .adaptor import merge_quadrangle_n9 as nms_impl
    # if len(polys) == 0:
    #     return np.array([], dtype='float32')
    # p = polys.copy()
    # p[:, :8] *= precision
    # ret = np.array(nms_impl(p, thres), dtype='float32')
    # ret[:, :8] /= precision
    # return ret
	
	
def merge_main_linux(polys, thres=0.3, precision=10000):
    ver = python_version()
    # if os.path.isfile(os.path.join("ocr","adaptor.so")):
    #     os.remove(os.path.join("ocr","adaptor.so"))
    #
    # if ver[0] == "2":
    #     s = os.path.join("ocr","adaptor2.so")#"adaptor2.so"
    # else:
    #     s = os.path.join("ocr","adaptor3.so")#"adaptor3.so"
    #
    # d = os.path.join("ocr","adaptor.so")#"adaptor.so"
    # shutil.copy2(s, d)
    from ocr.adaptor import merge_quadrangle_n9 as nms_impl
    if len(polys) == 0:
        return np.array([], dtype='float32')
    p = polys.copy()
    p[:,:8] *= precision
    ret = np.array(nms_impl(p, thres), dtype='float32')
    ret[:,:8] /= precision
    return ret
