-- bundle version 20201020
-- as DB admin (USER ADMIN ROLE) on tenant
-- sample entries to test the application
CREATE ROLE ZMODELING;
CREATE ROLE ZREADALLTABLES;
CREATE ROLE ZADMINSELFSERVICETOOLS;
insert into "POC_SECU"."APPRO_USER_MNGT" VALUES ('TESTRA','0','ZMODELING',0,0,1,0,'20181203','15:00:01');
insert into "POC_SECU"."APPRO_USER_MNGT" VALUES ('TESTRA2','0','ZMODELING,ZREADALLTABLES,ZADMINSELFSERVICETOOLS',0,0,1,0,'','');
insert into "POC_SECU"."APPRO_USER_MNGT" VALUES ('TESTRA3','0','ZMODELING',0,0,1,0,'','');
insert into "POC_SECU"."APPRO_USER_MNGT" VALUES ('TESTRA5','0','ZMODELING',0,0,0,0,'','');
insert into "POC_SECU"."APPRO_USER_MNGT" VALUES ('RA','0','ZMODELING',0,0,0,0,'','');
-- check the table
select * from "POC_SECU"."APPRO_USER_MNGT";
select * from "POC_SECU"."APPRO_USER_HISTORY";
-- start the python from command line
-- read the return of this program and control these tables
select * from "POC_SECU"."APPRO_USER_MNGT";
select * from "POC_SECU"."APPRO_USER_HISTORY";
-- 	again some inputs to see how the program python will done the update
update "POC_SECU"."APPRO_USER_MNGT" set "TO_UPDATE"=1 where USERID='TESTRA2';
update "POC_SECU"."APPRO_USER_MNGT" set "TO_DELETE"=1 where USERID='TESTRA2';
update "POC_SECU"."APPRO_USER_MNGT" set "ENABLED"=1,"TO_DELETE"=1 where USERID='TESTRA';
update "POC_SECU"."APPRO_USER_MNGT" set "TO_ENABLE"=1,"ENABLED"=0 where USERID='TESTRA2';
update "POC_SECU"."APPRO_USER_MNGT" set "TO_DELETE"=1 where USERID='TESTRA3';
delete from "POC_SECU"."APPRO_USER_MNGT" where USERID='TESTRA2';
select count(*) from SYS.ROLES where ROLE_NAME='ZChangePwd';
-- empty tables, restart from beginning the game or start the real life
delete from "POC_SECU"."APPRO_USER_MNGT";
delete from "POC_SECU"."APPRO_USER_HISTORY";
drop user TESTRA;
drop user TESTRA2;
drop user TESTRA3;
drop user TESTRA5;
drop user RA;
