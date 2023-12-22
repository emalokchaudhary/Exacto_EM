import logging,re
import datetime
import os
import shutil
DESTINATION_FOLDER=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Exception_log_old_file"
LOG_PATH=r"/datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Exception_log"
# /datadrive/EM_Product/ips/invoiceProduct_solution/EM_output/Exception_log
time_now =str(datetime.datetime.now())
day=time_now[:10]+"_"
date_dec=None

def purging(path, days):
    
    today = datetime.datetime.today()
    # print(today)
    global date_dec
    if date_dec is not None:
        date_dec = str(date_dec)[:10]
    today_date = str(today)[:10]
    #print(date_dec , today_date)
    if date_dec!= today_date:
    #  print("purging run")
        dir_list = os.listdir(path)
        print(dir_list)
        for dir in dir_list:
            dir_date = "".join(re.findall(r"\d+",dir))
            if len(dir_date)>4: #find date consisting file
                dir_date = datetime.datetime.strptime(dir_date, "%Y%m%d")
            file_dur = today - dir_date
            if (file_dur.days) > days:
                # os.remove(os.path.join(path,dir) )
                shutil.move(os.path.join(path,dir),DESTINATION_FOLDER )
        date_dec = str(today)



path=os.path.join(LOG_PATH,"Exception_file_"+day+".log")

logger = logging.getLogger(__name__) 
logger.setLevel(logging.INFO) 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
# formatter = logging.basicConfig('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
file_handler = logging.FileHandler(path) 
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter) 
logger.addHandler(file_handler)
file_handler.flush()
logger.info("-----------------------------------------------------------------------------------------------------------------------------------------")
purging(path=LOG_PATH,days=1)## CHANGE  DATES ACC. TO NEED

# print(os.getcwd())