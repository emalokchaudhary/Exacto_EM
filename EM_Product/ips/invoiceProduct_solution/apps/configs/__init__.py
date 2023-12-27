import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
super_parentdir = os.path.dirname(parentdir)
#print("parent dir  ", super_parentdir)
sys.path.insert(0,super_parentdir) 
#from settings import connection as db_connect
from settings.exacto_settings import ExactoSettings

