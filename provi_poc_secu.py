# coding=utf-8
################################################
# Rodolphe ALT
# 0.1
# goal : create,enable,disable,allow roles
#################################################
import sys
import pyhdb
import datetime
import time
import os
import csv
import smtplib
#from StringIO import StringIO  # Python2
from io import StringIO # Python3
from email.mime.text import MIMEText
from hurry.filesize import size
from hurry.filesize import si
from bitmath import *
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf-8')

# timestamp
ts = time.time()
#st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
mydate4hana = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d')
mytime4hana = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')


# file source
SAPHANA_SID = 'SID'
SAPHANA_HOSTNAME = 'sap_hana_hostname'
SAPHANA_SCHEMA = 'POC_SECU'
SAPHANA_SQLPORT = '30059'   # adapt this entry according to the tenant
SAPHANA_ADMIN_LOGIN = 'TECH_POC_SECU'
SAPHANA_ADMIN_PWD = 'UltraComplexPassword2020!'

# Hana remote connexion
connection = pyhdb.connect(SAPHANA_HOSTNAME, SAPHANA_SQLPORT, SAPHANA_ADMIN_LOGIN, SAPHANA_ADMIN_PWD)
cur = connection.cursor()

# SQL generic requests
query_create_user="CREATE RESTRICTED USER %s WITH IDENTITY  FOR SAP LOGON TICKET"
query_grant_user="grant %s to %s"
query_disable_user="alter user %s deactivate user now"
query_user_exist="select count(*) from SYS.USERS where user_name='%s'"
query_role_exist="select count(*) from SYS.ROLES where ROLE_NAME='%s'"
query_enable_user="alter user %s activate user now"
query_upd_state="update %s.APPRO_USER_MNGT set %s,LAST_CHANGE_DATE='%s',LAST_CHANGE_TIME='%s' where USERID='%s'"
query_insert_his="insert into %s.APPRO_USER_HISTORY values('%s','%s','%s','%s','%s','%s')"
query_delete_user="DROP USER %s"
query_delete_state="delete from %s.APPRO_USER_MNGT where USERID='%s'"

query_list = "select * from %s.APPRO_USER_MNGT"
try:
        cur.execute(query_list % SAPHANA_SCHEMA)
except:
       print("HANA settings occured a problem")
resultat = cur.fetchall()
for row in resultat:
        APPRO_USERID=str(row[0])
        APPRO_ENABLED=int(row[1])
        APPRO_ROLES=str(row[2])
        APPRO_ROLES_ALL = APPRO_ROLES.split(",")
        APPRO_TO_UPDATE=int(row[3])
        APPRO_TO_DISABLE=int(row[4])
        APPRO_TO_ENABLE=int(row[5])
        APPRO_TO_DELETE=int(row[6])
        APPRO_LAST_DATE=str(row[7])
        APPRO_LAST_TIME=str(row[8])
        print("USERID=%s;ROLES=%s" % (APPRO_USERID,APPRO_ROLES))
        print("ENABLED=%s;TO_UPDATE=%s;TO_DISABLE=%s;TO_ENABLE=%s;TO_DELETE=%s;LAST_DATE=%s;LAST_TIME=%s" % (APPRO_ENABLED,APPRO_TO_UPDATE,APPRO_TO_DISABLE,APPRO_TO_ENABLE,APPRO_TO_DELETE,APPRO_LAST_DATE,APPRO_LAST_TIME))

        if APPRO_ENABLED > 0:                   # Account seems enabled in HANA
                if APPRO_TO_UPDATE > 0:
                        print("THE ACCOUNT MUST BE UPDATE")
                        try:
                                cur.execute(query_user_exist % APPRO_USERID)
                                user_exist = cur.fetchone()[0]
                                if user_exist > 0:
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'UPDATE',APPRO_ROLES,'THE ACCOUNT MUST BE UPDATE'))
                                for current_word in APPRO_ROLES_ALL:
                                        cur.execute(query_role_exist % current_word)            # if many roles
                                        role_exist = cur.fetchone()[0]
                                        if (user_exist > 0 and role_exist >0):
                                                print("grant %s to %s" % (current_word,APPRO_USERID))
                                                cur.execute(query_grant_user % (current_word,APPRO_USERID))
                                        cur.execute(query_upd_state % (SAPHANA_SCHEMA,'TO_UPDATE=0',mydate4hana,mytime4hana,APPRO_USERID))
                                if (user_exist == 0):
                                        print("THE USER IS NOT CREATED, please ask to update TO_ENABLE=1")
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'UPDATE',APPRO_ROLES,'THE USER IS NOT CREATED, please ask to update TO_ENABLE=1'))
                        except:
                                print("AN ERROR HAS BEEN OCCURED DURING UPDATE")
                                cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'UPDATE',APPRO_ROLES,'AN ERROR HAS BEEN OCCURED DURING UPDATE'))
                if APPRO_TO_DISABLE > 0:
                        print("ACCOUNT MUST BE DISABLED : %s" % APPRO_USERID)
                        try:
                                cur.execute(query_user_exist % APPRO_USERID)
                                user_exist = cur.fetchone()[0]
                                if user_exist > 0:
                                        cur.execute(query_disable_user % APPRO_USERID)
                                        cur.execute(query_upd_state % (SAPHANA_SCHEMA,'TO_DISABLE=0,ENABLED=0',mydate4hana,mytime4hana,APPRO_USERID))
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'DISABLE','','HAS BEEN DEACTIVATED'))
                                        print("%s HAS BEEN DEACTIVATED" % APPRO_USERID)
                                else:
                                        print("%s IS NOT CREATED IN HANA" % APPRO_USERID)
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'DISABLE','','FAILED : THIS USER IS NOT CREATED IN HANA'))
                        except:
                                print("AN ERROR HAS BEEN OCCURED DURING DELETION")
                                cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'DISABLE','','FAILED : AN ERROR HAS BEEN OCCURED DURING DELETION'))
        else:                                   # Account must be created in HANA
                if APPRO_TO_ENABLE > 0:
                        try:
                                cur.execute(query_user_exist % APPRO_USERID)
                                user_exist = cur.fetchone()[0]
                                if user_exist > 0:
                                        print("user exist, just re-enable it")
                                        cur.execute(query_enable_user % APPRO_USERID)
                                        cur.execute(query_upd_state % (SAPHANA_SCHEMA,'TO_ENABLE=0,ENABLED=1',mydate4hana,mytime4hana,APPRO_USERID))
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'CREATE','','user exist, just re-enable it'))
                                else:
                                        print("not find in DB, user %s created" % APPRO_USERID)
                                        cur.execute(query_create_user % APPRO_USERID)
                                        cur.execute(query_upd_state % (SAPHANA_SCHEMA,'TO_ENABLE=0,ENABLED=1',mydate4hana,mytime4hana,APPRO_USERID))
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'ENABLE','','not find in DB, user must be created'))
                                        print("add role(s) to user %s :" % APPRO_USERID)
                                        print("APPRO_ROLES_ALL=%s" % APPRO_ROLES_ALL)
                                        for current_word in APPRO_ROLES_ALL:
                                                cur.execute(query_role_exist % current_word)            # if many role
                                                role_exist = cur.fetchone()[0]
                                                if (role_exist >0):
                                                        print("grant %s to %s" % (current_word,APPRO_USERID))
                                                        cur.execute(query_grant_user % (current_word,APPRO_USERID))
                                                else:
                                                        print("the role %s is not available" % current_word)
                                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'GRANT',APPRO_ROLES,'add roles to user'))
                        except:
                                print("AN ERROR HAS BEEN OCCURED DURING USER CHECK")
                                cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'ENABLE',APPRO_ROLES,'FAILED : AN ERROR HAS BEEN OCCURED DURING USER CHECK'))
        if APPRO_TO_DELETE > 0:
                print("THE USER WILL BE DELETED")
                cur.execute(query_user_exist % APPRO_USERID)
                user_exist = cur.fetchone()[0]
                if user_exist > 0:
                        print("user exist, delete it")
                        cur.execute(query_delete_user % APPRO_USERID)
                        cur.execute(query_delete_state % (SAPHANA_SCHEMA,APPRO_USERID))
                        cur.execute(query_insert_his % (SAPHANA_SCHEMA,mydate4hana,mytime4hana,APPRO_USERID,'DELETE','','USER HAS BEEN DELETED FROM HANA'))
        print("------------ END OF THIS LOOP ------------")



connection.commit()
connection.close()
