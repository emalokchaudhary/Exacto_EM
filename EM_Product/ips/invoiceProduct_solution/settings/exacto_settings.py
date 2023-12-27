import os, traceback
import pyodbc



class ExactoSettings:

  def __init__(self):
    
    self.ROOT_INPUT_DIR = "/datadrive/EM_Product/eips_data/invoice_data"
    self.ROOT_INPUT_DIR = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_input/Camin"
    self.PATTERNS_PATH = "/datadrive/EM_Product/eips_data/user_active_learning_data"
    self.INVOICE_LOG = "/datadrive/EM_Product/ips/invoiceProduct_solution/logs"
    # self.OUTPUT_DIR = './../output_data/'
    self.OUTPUT_DIR = "./../EM_output"
    
    ####### EM Path ######
    self.INPUT_CGI_CHEM = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/CGI/CHEM-US"
    self.INPUT_CGI_US = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/CGI/US"
    self.INPUT_CAMIN_CHEM = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Camin/CHEM-US"
    self.INPUT_CAMIN_US = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Camin/US"
    self.INPUT_CAMIN_INT = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Camin/INT"
    
    self.INPUT_SAYBOLT_CHEM="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Saybolt/CHEM-US"
    self.INPUT_SAYBOLT_EU="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Saybolt/EU"
    self.INPUT_SAYBOLT_INT="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Saybolt/INT"
    self.INPUT_SAYBOLT_US="/datadrive/EM_Product/ips/invoiceProduct_solution/EM_api_Input/Saybolt/US"
    
    self.PROCESSED_CGI_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/CGI/CHEM-US"
    self.PROCESSED_CGI_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/CGI/US"
    self.PROCESSED_CAMIN_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Camin/CHEM-US"
    self.PROCESSED_CAMIN_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Camin/US"
    self.PROCESSED_CAMIN_INT_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Camin/INT"
    
    self.PROCESSED_SAYBOLT_INT_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Saybolt/INT"
    self.PROCESSED_SAYBOLT_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Saybolt/CHEM-US"
    self.PROCESSED_SAYBOLT_EU_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Saybolt/EU"
    self.PROCESSED_SAYBOLT_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Processed/Saybolt/US"
    
    self.ERROR_CGI_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/CGI/CHEM-US"
    self.ERROR_CGI_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/CGI/US"
    self.ERROR_CAMIN_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Camin/CHEM-US"
    self.ERROR_CAMIN_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Camin/US"
    self.ERROR_CAMIN_INT_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Camin/INT"
    
    self.ERROR_SAYBOLT_INT_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Saybolt/INT"
    self.ERROR_SAYBOLT_CHEM_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Saybolt/CHEM-US"
    self.ERROR_SAYBOLT_EU_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Saybolt/EU"
    self.ERROR_SAYBOLT_US_PATH = "/datadrive/EM_Product/ips/invoiceProduct_solution/EM_Nonprocessed/Saybolt/US"

    
    self.DEFAULT_USER_ID = '123'
    self.DEFAULT_CONFIG_ID = 'c1'
    self.DEFAULT_COMPANY_CODE = 'ccode1'
    self.XML_DIR = os.path.join(self.OUTPUT_DIR, 'XML')
    self.DOC_OUTPUT = os.path.join(self.OUTPUT_DIR, 'doc_output')
    self.OCR_MODEL_PATHS  = { 

                            'checkpoint_path'  :   './data/models/resnet',
                            'checkpointPath'   :   './data/models/orientationClassifier',
                            'checkpointMeta'  :   './data/models/orientationClassifier/orientationHighmark-model.meta',
                            'classModel'      :   './data/models/harrisClassifier/classificationHarris-model.meta',
                            'classModelDir'   :   './data/models/harrisClassifier',
                            'xml_dir'         :    self.XML_DIR

                      }

    self.create_req_dir()

  @staticmethod
  def safely_create_dir(path):
    if not os.path.exists(path):
      os.mkdir(path)
    return

  def create_req_dir(self):
    ExactoSettings.safely_create_dir(self.ROOT_INPUT_DIR)
    ExactoSettings.safely_create_dir(self.OUTPUT_DIR)
    ExactoSettings.safely_create_dir(self.DOC_OUTPUT)
    ExactoSettings.safely_create_dir(self.XML_DIR)
    ExactoSettings.safely_create_dir(self.INVOICE_LOG)
    return













