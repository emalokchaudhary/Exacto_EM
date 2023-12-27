# coding: utf-8

##################### Training configuration ##########################

train_dir="training_data2"
train_image_type="*.png"
train_txt_type=".txt"
line_shape = (48, 500)
line_shape_t = (500,48)
decay_factor = 0.9
eta_initial = 1.0
decay_step = 2000
dropout = 1.0
momentum = 0.9
validation_step = 1000
batch_size = 32
training_batch = 10
total_epochs = 1000
hidden_neurons = 128
num_hidden_layers = 2
total_classes = 150
num_training_images = 10000000000

##################### Testing configuration ########################

test_dir="testing_data"
test_image_type="*.bin.png"
test_txt_type=".txt"
test_batch_size = 32
testing_batch = 10
num_testing_images = 100000

##################### OCR configuration ##########################

numbers = r"0123456789"
alphabets = r"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

english = r""".wz;{j»79B<@®:84v!-&ﬂ(d0_oéIqc>|O#AL5”"‘gkEN$l3~§}\Sf°n,RM’Dp©mU][?y'VPu%bK/16xﬁhJ)i“H*+¥£F€s—aW«T2GeQXCrZ=¢Yt"""
danish =   r"""PKW«irDSLpotE-MalTsbeﬁndÖfchzw#2uüg&CmvA©3Nk15„Iéj[G]9H—|.,JOYURx‚‘;06XF’"Ä4y/{}VB€()ä:!>q*£7°8”\Z$+?_Ü<%®öQ'ﬂ=@“ß»"""
finnish =  r"""detailsovVun+358MÖKITmprkPz.äjg1924—6|0,Schy>()[]=fö€£$CY-q"Jé<A7%;DFEURHb:'šXLQ&NGOw?”/!W*xBZ»Ä"""
norwegian = r"""NOKsåkule9.R$(0)1LBnQdpFot:avribygh!YHETm2UIjD5MWAéS;',c°7qz3-føPCJ*—6»æÅ|«[X]GV/"”&€84£öxw<=>%+?ØZä"""
polish =    r"""IXmającolign="eftsbZukóry<h1NOWŚCwDLAdłz:ęSp.27,©08PF5|R3[]TMV-U_#B€)ż4EGĄśź+v»>/6&K*£$x~(9ŁÓH—JćQ!%YŻ;›?„”ń'Ęq@«"""
swedish =   r"""Show”DetsinfödÖK'xmpl204åbr8vaukjg"J.ä6PÅy,HW5%c-FZ1N/L_€£$R:I9=3CéÄA[Ez©?»#T(X)UYGQ;O&B+]7Mq!V>—*|"""
german =     r"""PKW«irDSLpotE-MalTsbeﬁndÖfchzw#2uüg&CmvA©3Nk15„Iéj[G]9H—|.,JOYURx‚‘;06XF’"Ä4y/{}VB€()ä:!>q*£7°8”\Z$+?_Ü<%®öQ'ﬂ=@“ß»"""


symbols = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
charset1 = numbers+alphabets+symbols+danish+finnish+norwegian+polish+swedish+german+english
ascii_labels = [""," ","~"] + [chr(x) for x in range(33,126)]
charset = sorted(list(set(list(ascii_labels) + list(charset1) )))

# print(len(charset))
# print(charset)
