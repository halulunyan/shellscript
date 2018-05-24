#!/usr/bin/env python

##################################################################################################################################
#
#
# lssecfixes_report.py
#
# Author: Steve McKay - smckay@us.ibm.com
# Version: 1.1
# 8.24.2011
#
# The purpose of this program is to generate an html based report based on one or multiple lssecfix output files. 
# It parses the lssecfixes files and places the data in a local sqlite db.
#
# From that data, it can then generate the html report for one or multiple advisories, for one or multiple systems as needed. 
#
# 1.2 - 9.14.2011 - Added csv report output and --missing switch to generate report showing only missing
# 1.1 - 8.24.2011 - Added column in APARs table showing a synopsis of the LSSECFIXES results, also fixed issue with logging output
# 1.0 - 7.29.2011 - Initial release


global VERSION
VERSION="1.2"

global Last_Updated
Last_Updated="09/14/2011"

import sys
import os.path

import logging
import optparse
import re
import string 
import csv
from datetime import datetime
from sqlite3 import *

global OutputWriter

#http://stackoverflow.com/questions/2700859/how-to-replace-unicode-characters-by-ascii-characters-in-python-perl-script-give
import unicodedata

import pprint
pp = pprint.PrettyPrinter(indent=4)

TRUE = (1==1)
FALSE = not TRUE

#defaults
output_file="lssecfixes_report.csv"
input_file="infile.txt"
	
#http://aymanh.com/python-debugging-techniques
progname=sys.argv[0]

#http://blog.tplus1.com/index.php/2007/09/28/the-python-logging-module-is-much-better-than-print-statements/
import logging #used for debugging
# Log everything, and send it to stderr.

#http://aymanh.com/python-debugging-techniques
#Setting the logging level to a value enables log messages for this level and all levels above it. So if you set the level to logging.warning, you will get WARNING, ERROR and CRITICAL messages. This allows you to have different levels of log verbosity.

LOGGING_LEVELS = {'critical': logging.CRITICAL,
                  'error': logging.ERROR,
                  'warning': logging.WARNING,
                  'info': logging.INFO,
                  'debug': logging.DEBUG}

def dictionary_2_lists(item):
	
	keys=[]
	values=[]
	
	for key,value in item.iteritems():
		keys.append("'"+key+"'")
		values.append(value)
		
	
	return keys,values

def insert_data(cursor,table,item):
	question_marks=None
	#print item
	
	for count in range(0,len(item)):
		if question_marks==None:
			question_marks="?"
		else: 
			question_marks+=",?"
		
	question_marks+=",datetime('now'),datetime('now')"
	
	(keys,values)=dictionary_2_lists(item)
	#insert_string="INSERT INTO %s ("+','.join(keys)+",inserted,last_updated) VALUES (%s)), "+','.join(values)+")"%(table,question_marks)
	#print insert_string
	#print item
	#sys.exit()
	
	try:
		#cursor.execute('INSERT INTO lssecfixes (agency,fqdn,hostname,report_date,due_date,due,sev,advisory,description) VALUES (?,?,?,?,?,?,?,?,?)', (agency,fqdn,hostname,report_date,due_date,due,sev,advisory,description))
		logging.debug("INSERT INTO %s (%s,inserted,last_updated) VALUES (%s)"%(str(table),str(",".join(keys)),str(question_marks)) +","+str(",".join(values)))
		cursor.execute("INSERT INTO %s (%s,inserted,last_updated) VALUES (%s)"%(table,",".join(keys),question_marks), values)
	except IntegrityError, m:
		logging.error(IntegrityError, m)
		
def output_html_heading(hostname):
	
	hostname_string=""
	if hostname!=None and hostname!="":
		hostname_string=" for %s"%(hostname)
	
	#print hostname_string
	
	heading_string="""	
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
	<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>

  <meta name="Description" content="" />

  <meta name="Keywords" content="" />

  <meta name="Owner" content="Internet e-mail_address" />

  <meta name="Feedback" content="Internet e-mail_address" />

  <meta name="Robots" content="noindex,nofollow" />

  <meta name="Security" content="IBM internal use only" />

  <meta name="Source" content="v8 Template Generator" />

  <meta name="IBM.Country" content="US" />

  <meta name="DC.Date" scheme="iso8601" content="2004-02-19" />

  <meta name="DC.Language" scheme="rfc1766" content="en-US" />

  <meta name="DC.Rights" content="Copyright (c) 2001,2006 by IBM Corporation" />

  <meta name="DC.Type" scheme="IBM_ContentClassTaxonomy" content="ZZ999" />

  <meta name="DC.Subject" scheme="IBM_SubjectTaxonomy" content="" />

  <meta name="DC.Publisher" content="IBM Corporation" />

  <meta name="IBM.Effective" scheme="W3CDTF" content="" />

  <meta name="IBM.Industry" scheme="IBM_IndustryTaxonomy" content="ZZ" />
  <title>LSSECFIXES Report %s</title>




  <script language="JavaScript" type="text/javaScript" src="http://w3.ibm.com/ui/v8/scripts/scripts.js"></script>
  <style type="text/css" media="all">
 <!--
 @import url("http://w3.ibm.com/ui/v8/css/screen.css");
 @import url("http://w3.ibm.com/ui/v8/css/interior.css");
 @import url("http://w3.ibm.com/ui/v8/css/popup-window.css");
 @import url("http://w3.ibm.com/ui/v8/css/icons.css");
 -->
 </style>
 <!--
  <script language="JavaScript">
 function testResults (form) {
 var Qr = form.inputbox.value;
 location.href='https://portal.mss.iss.net/mss/ticket/securityTicketUpdate.mss?ticketId='+escape(Qr)
 }
  </script>
 -->

 </head>


 <body style="direction: ltr;" id="w3-ibm-com">

	<!-- start popup masthead //////////////////////////////////////////// -->
	<div id="popup-masthead"> <img id="popup-w3-sitemark" src="http://w3.ibm.com/ui/v8/images/id-w3-sitemark-small.gif" alt="" height="26" width="182" /></div>

	<!-- stop popup masthead //////////////////////////////////////////// -->
	<!-- start content //////////////////////////////////////////// -->
	<div id="content"><!-- start main content -->
	<div id="content-main">
	<div id="fourth-level">
	<h1>LSSECFIXES Report %s</h1>

	</div>

	<h2>Purpose</h2>
	<p>The purpose of this page is to provide a report for multiple lssecfixes files. This is mainly useful in areas where Fusion can not be run in an environment </p>
	<br />
	<br />
	"""%(hostname_string,hostname_string)
	
	print heading_string
	
def parse_n_load_lssecfixes(dbconn,file):
						
	cursor = dbconn.cursor()
	table="lssecfixes"
	
	#lssec_DHR-FSAPP.dhr.state.ga.us_03152011.txt
	filename_regex1=re.compile("lssec(?:-out)*_(?P<fqdn>.*)_(?P<report_date>\d+\.\d+\.\d+)\.txt", re.IGNORECASE)
	
	#lssec-bldxsogapp04-05.24.11.txt
	filename_regex2=re.compile("lssec-(.*)-(.*).txt", re.IGNORECASE)
	

	agency=""
	item={}
	fqdn=hostname=report_date=""
	
	#HERE
	parts=file.rpartition("/")
	tmp_filename=parts[2]
	#print tmp_filename
	

	
	#parse the filename
	#tmp_filename=file
	
	#remove file extension .txt
	tmp_filename=tmp_filename.replace(".txt","")
	
	#if the filename has lssecfixes in it, remove
	tmp_filename=tmp_filename.replace("lssecfixes","")
	tmp_filename=tmp_filename.replace("lssecfix","")
	tmp_filename=tmp_filename.replace("lssec","")
	#print "After lssecfixes removal: "+tmp_filename
	
	#date - find and remove
	if re.search("(?P<date>\d+\.\d+\.\d+)",tmp_filename):
		m=re.search("(?P<date>\d+\.\d+\.\d+)",tmp_filename)
		item['report_date']=m.group('date')
		tmp_filename=tmp_filename.replace(item['report_date'],'')
		#print item['report_date']
	elif re.search("[\s\_\.]+(?P<date>\d{4,8})",tmp_filename):
		m=re.search("[\s\_\.]+(?P<date>\d{4,8})",tmp_filename)
		item['report_date']=m.group('date')
		tmp_filename=tmp_filename.replace(item['report_date'],'')
		#print item['report_date']
		
	#print "After date removal: "+tmp_filename
	
	#hostname - remove leacing or trailing - or _
	if (re.search("^_",tmp_filename) or re.search("^-",tmp_filename)):
		tmp_str=tmp_filename[1:]
		tmp_filename=tmp_str

	if (re.search("-$",tmp_filename) or re.search("_$",tmp_filename)):
		tmp_str=tmp_filename[:-1]
		tmp_filename=tmp_str
	
	#print "After - or _ removal: "+tmp_filename
	#print "****"
	#whatever is left over, consider the machine name
	item['hostname']=tmp_filename
	
	
	try:
		infile_handle=open(file,"r")
	except IOError:
		#print >> sys.stderr,"Can't open file %s because: %s"%(input_directory+"/"+file,IOError)
		logging.error("Can't open file %s because: %s"%(input_directory+"/"+file,IOError))
		#print IOError
		parser.print_help()
		sys.exit(1)
	
	#heading_printed=False

	
	date_regex=re.compile("^([0-9]{2}/[0-9]{2}/[0-9]{4})\s+",re.IGNORECASE)
	
	#DUE DATE    DUE  SEV  ADVISORY     DESCRIPTION
	#05/14/2007  I    H    2007:0369.1  RHSA-2007:0097-02: firefox security update
	
	#02/19/2005  I    H    2004:2060.1  IY64312: Buffer overflow vulnerability in paginit command
	#02/19/2005  I    H    2004:2061.1  IY64277: Untrusted path vulnerability in the diag script
	#06/09/2006  NA   H    2006:0586.3  A race condition in sendmail may allow a remote attacker to execute arbitrary code
	#07/21/2006  I    H    2006:0586.4  IY82994: A race condition in sendmail may allow a remote attacker to execute arbitrary code

	#row_regex=re.compile("^(?P<due_date>[0-9]{2}/[0-9]{2}/[0-9]{4})\s+(?P<due>[\w\+\=\*]*)\s+(?P<sev>\w+)\s+(?P<advisory>[0-9]+\:[0-9]+\.[0-9]+)\s+(?P<description>.*)\s*$",re.IGNORECASE)
	row_regex=re.compile("^(?P<due_date>[0-9]{2}/[0-9]{2}/[0-9]{4})\s+(?P<due>(.{3}))\s+(?P<sev>(.{3}))\s+(?P<advisory>(.{13}))\s+(?P<description>(.*$))")
	
	
	#lssecfixes_version=1.9.2
	lssecfixes_version_regex=re.compile("^#\s*lssecfixes_version\s*=\s*(?P<lssecfixes_version>\d+\.\d+\.\d+)")
	# fixDB = /usr/bin/../etc/secfixdb.aix53, 139179, Fri Jun 24 22:57:12 2011
	fixdb_regex=re.compile("^#\s*fixDB\s*=\s*(.*)secfixdb\.(?P<fixdb>.*)\,\s*\d+")
	
	#clean results for system before loading
	#print "DELETE from %s where hostname='%s'"%(table,item['hostname'])
	#cursor.execute("DELETE from %s where hostname='%s'"%(table,item['hostname']) )
	#dbconn.commit()
	#sys.exit()
	
	#TODO - delete entries for hostname in case they already exist
	#print "DELETE from %s where hostname='%s'"%(table,item['hostname'])
	cursor.execute("DELETE from %s where hostname='%s'"%(table,item['hostname']) )
	logging.debug("commit")
	dbconn.commit()
	
	print "Inserting data for %s "%item['hostname']
	
	for line in infile_handle:
		#print line
				
		if len(line)>0:						
			if lssecfixes_version_regex.search(line):
				m=lssecfixes_version_regex.search(line)
				item['lssecfixes_version']=m.group('lssecfixes_version')
				continue
			elif fixdb_regex.search(line):
				m=fixdb_regex.search(line)
				item['fixdb']=m.group('fixdb')
				continue
			elif row_regex.search(line):
				m=row_regex.search(line)
				
				if m is None:
					logging.debug("Error getting parsing line: %s"%(line))
				else:
					item['DUE_DATE']=m.group('due_date')
					item['DUE']=m.group('due')
					item['SEV']=m.group('sev')
					item['ADVISORY']=m.group('advisory')
					item['DESCRIPTION']=m.group('description')
				
					#print item
					
					#clean up the data, epecially for description
					for (name, value) in item.iteritems():
				
						item[name] = value.strip() 
						# Clean up any non-ascii unicode characters
						#make sure we have a unicode string
						item[name] = unicode(item[name], "iso-8859-1")
						#http://stackoverflow.com/questions/2700859/how-to-replace-unicode-characters-by-ascii-characters-in-python-perl-script-give
						item[name]=unicodedata.normalize('NFKD',item[name]).encode('ascii','ignore')
						#business_rules(options.type,value)
						#print "name: %s, value: %s"%(name,item[name])
	
					
					insert_data(cursor,table,item)
					
					#remove old data so it can't accidentally be used for the next row
					del item['DUE_DATE']
					del item['DUE']
					del item['SEV']
					del item['ADVISORY']
					del item['DESCRIPTION']
					
			elif line.startswith("#") or re.search("perl:",line) or re.search("\s+LC_ALL",line) or re.search("\s+LC__FASTMSG",line) or re.search("\s+LANG",line) or re.search("\s+are supported",line):
				#perl : warning: Please check that your locale settings:
				#LC_ALL = (unset),
				#LC__FASTMSG = "true",
				#LANG = "EN_US"
				#are supported and installed on your system.
				logging.debug("comment, skipping line: "+line.strip())
				continue
			elif not re.search("^DUE DATE\s+",line) and not re.search("[-]{10}\s+",line):
				#print re.search("^DUE DATE",line)
				#print >> sys.stderr,"couldn't parse line: "+line.strip()+", in file "+file
				logging.error("couldn't parse line: "+line.strip()+", in file "+file)
				parser.print_help()
				sys.exit(1)
				#print line

	logging.debug("commit")
	dbconn.commit()	

def print_advisories_table(advisory_arr,due_arr):
	#print advisory_arr
	#sys.exit()
	
	#print >> sys.stderr,advisory_arr,due_arr
	
	due_string=[]
	due_string.append("Lssecfixes reports the following for those systems who reported on this advisory:")
	bgcolor=None
	
	if ("*" in due_arr or "+" in due_arr):
		if (bgcolor is None):
			bgcolor="RED"
	elif ("-" in due_arr or "" in due_arr):
		if (bgcolor is None):
			bgcolor="YELLOW"
	else:
		if (bgcolor is None):
			bgcolor="GREEN"
	
	#due_string.append("Security fix is applicable and overdue - lssecfixes reports the following:")
	#'*' = Security fix is overdue.
	if ("*" in due_arr):
		due_string.append("'*' = Security fix is overdue.")
	#`'+' = Security fix is overdue and has a revision level higher than the current system. (e.g. 4.3.2.x -> 4.3.3.x)
	if ("+" in due_arr):
		due_string.append("'+' = Security fix is overdue and has a revision level higher than the current system. (e.g. 4.3.2.x -> 4.3.3.x)")


	#due_string.append("Security fix is applicable, but not yet due - lssecfixes reports the following:")
	#'-' = Security fix is not yet due, but has a higher revision level than the current system.
	if ("-" in due_arr):
		due_string.append("'-' = Security fix is not yet due, but has a higher revision level than the current system.")
	#' ' = Security fix is not yet due.
	if ("" in due_arr):
		due_string.append("' ' = Security fix is not yet due.")
		

	#due_string.append("Lssecfixes - reports the following:")
	#'I' = Security fix has already been installed.
	if ("I" in due_arr):
		due_string.append("'I' = Security fix has already been installed.")
	#'E' = Equivalent e-fix has been applied.
	if ("E" in due_arr):
		due_string.append("'E' = Equivalent e-fix has been applied.")
	#'W' = Workaround has been implemented or affected service not running.
	if ("W" in due_arr):
		due_string.append("'W' = Workaround has been implemented or affected service not running.")
	#'NA' = Security fix does not apply.
	if ("NA" in due_arr):
		due_string.append("'NA' = Security fix does not apply.")
	#'F' = Security fix has not been released (future).
	if ("F" in due_arr):
		due_string.append("'F' = Security fix has not been released (future).")
	#'A' = Security fix has been released, but not formally announced.
	if ("A" in due_arr):
		due_string.append("'A' = Security fix has been released, but not formally announced.")
	
		
	if len(advisory_arr)==1:
		print """<tr><td><a href="#%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td bgcolor="%s">%s</td></tr>"""%(advisory_arr[0]["link"],advisory_arr[0]["ADVISORY"],advisory_arr[0]["SEV"],advisory_arr[0]["DUE_DATE"],advisory_arr[0]["DESCRIPTION"],bgcolor,"<br/>".join(due_string))
	elif len(advisory_arr) > 1:
		print """<tr><td><a href="#%s">%s</a></td><td>%s</td><td>%s</td><td><ul>"""%(advisory_arr[0]["link"],advisory_arr[0]["ADVISORY"],advisory_arr[0]["SEV"],advisory_arr[0]["DUE_DATE"])
		for advisory in advisory_arr:	
			print "<li>%s</li>"%(advisory["DESCRIPTION"])
					
		print """</ul></td><td bgcolor="%s">%s</td></tr>"""%(bgcolor,"<br/>".join(due_string))
	else:
		#print >> sys.stderr,"Issue with advisory",advisory_arr
		logging.error("Issue with advisory",advisory_arr)
		
		
def print_advisories(advisory_arr):
	
	#print """<ul><li><a name="%s" id="%s"><strong>%s</strong></a>
	
	#print "Anchor: %s"%(advisory_arr[0]['anchor'])
	
	print """
		<p>&nbsp;</p>
	<p>&nbsp;</p>
	<table>
  <tr>
    <td colspan="2"><a id="%s"><strong>%s</strong></a></td>
    </tr>
  <tr>
    <td width="8">&nbsp;</td>
    <td><ul>
      <li>Sev: %s</li>
      </ul></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td><ul>
      <li>Due Date: %s</li>
    </ul></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td><table border="1">
      <tr>
        <td>Hostname</td>
        <td>Due</td>
        <td>Description</td>
      </tr>    
 """%(advisory_arr[0]['anchor'],advisory_arr[0]['ADVISORY'],advisory_arr[0]['SEV'],advisory_arr[0]['DUE_DATE'])
	
	for advisory in advisory_arr:
		bgcolor=""
		if (advisory['DUE']=="*" or advisory['DUE']=="+"):
			bgcolor="RED"
		elif (advisory['DUE']=="-" or advisory['DUE']==""):
			bgcolor="YELLOW"
		else:
			bgcolor="GREEN"
			
		print """
 <tr>
        <td><span class="note">%s</span></td>
        <td bgcolor="%s">%s</td>
        <td >%s</td>
      </tr>	
 """%(advisory['hostname'],bgcolor,advisory['DUE'],advisory['DESCRIPTION'])
	
	print """</table></td>
  </tr>
  <tr>
    <td>&nbsp;</td>
    <td><a href="#APAR_List">Back to APAR list</a></td>
  </tr>
 </table>"""
	
def list_servers_in_db():
	cursor = dbconn.cursor()
	table="lssecfixes"
	fileobj=None
	filename=""
	
	#select distinct(ADVISORY) from lssecfixes order by ADVISORY desc;
	#select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes order by ADVISORY desc, hostname desc;
	
	#get all the APARs represented
	logging.debug("SELECT distinct(hostname) from lssecfixes")
	cursor.execute("SELECT distinct(hostname) from lssecfixes")
	allentries=cursor.fetchall()
	
	for hostname in allentries:
		print hostname[0]
		
def list_advisories_in_db():
	cursor = dbconn.cursor()
	table="lssecfixes"
	fileobj=None
	filename=""
	
	#select distinct(ADVISORY) from lssecfixes order by ADVISORY desc;
	#select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes order by ADVISORY desc, hostname desc;
	
	#get all the APARs represented
	logging.debug("SELECT distinct(ADVISORY) from lssecfixes")
	cursor.execute("SELECT distinct(ADVISORY) from lssecfixes")
	allentries=cursor.fetchall()
	
	for advisory in allentries:
		print advisory[0]
		
		
def gen_where_clause(hostname_string,advisory_string,missing):	
	where_clause=None
	
	#import pdb; pdb.set_trace()

	
	if hostname_string!=None:
		#if hostname has a ,
		if re.search(",",hostname_string):
			hostname_arr=[]
			#split on the , to get the hostnames
			for hostname in hostname_string.split(","):
				#trim the hostnames in case there are spaces
				hostname=hostname.strip()
				#add ' around each hostname
				hostname_arr.append("'%s'"%(hostname))
				
			#join the hostnames	
			hostname_string=",".join(hostname_arr)		
			if where_clause==None:
				where_clause="where hostname in (%s)"%(hostname_string)
			else:
				where_clause=" and hostname in (%s)"%(hostname_string)
		else:
			if where_clause==None:
				where_clause="where hostname ='%s'"%(hostname_string)
			else:
				where_clause=" and hostname ='%s'"%(hostname_string)
	
	if advisory_string!=None:
		#if advisory has a ,
		if re.search(",",advisory_string):
			advisory_arr=[]
			#split on the , to get the advisory
			for advisory in advisory_string.split(","):
				#trim the advisories in case there are spaces
				advisory=advisory.strip()
				#add ' around each advisory
				advisory_arr.append("'%s'"%(advisory))
			
			#join the advisories
			advisory_string=",".join(advisory_arr)			
			
			if where_clause==None:
				where_clause="where ADVISORY in (%s)"%(advisory_string)
			else:
				where_clause=" and ADVISORY in (%s)"%(advisory_string)
		else:
				
			if where_clause==None:
				where_clause="where ADVISORY ='%s'"%(advisory_string)
			else:
				where_clause=" and ADVISORY ='%s'"%(advisory_string)
				
	if missing!=None:
		if where_clause==None:
			where_clause="where DUE in ('*','+','-','','F','A')"
		else:
			where_clause=" and DUE in ('*','+','-','','F','A')"
	
	if where_clause==None:
		where_clause=""
	
	logging.debug("where clause: %s"%(where_clause))
	
	return where_clause
	
def generate_csv_report(dbconn,hostname_string,advisory_string,output_file,missing):
	cursor = dbconn.cursor()
	table="lssecfixes"
	fileobj=None
	filename=""
	
	#select distinct(ADVISORY) from lssecfixes order by ADVISORY desc;
	#select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes order by ADVISORY desc, hostname desc;
	
	#get all the APARs represented
	where_clause=gen_where_clause(hostname_string,advisory_string,missing)
	
	#print "sql select distinct(ADVISORY),DUE_DATE,DESCRIPTION,SEV from lssecfixes %s order by ADVISORY desc"%(where_clause)

	logging.debug("select distinct(ADVISORY),DESCRIPTION,DUE_DATE,SEV,DUE,hostname from lssecfixes %s order by ADVISORY desc"%(where_clause))
	cursor.execute("select distinct(ADVISORY),DESCRIPTION,DUE_DATE,SEV,DUE,hostname from lssecfixes %s order by ADVISORY desc"%(where_clause))
	
	OutputWriter = csv.writer(open(output_file, 'wb'), quoting=csv.QUOTE_MINIMAL)
	
	allentries=cursor.fetchall()
	#output CSV Heading
	OutputWriter.writerow(['ADVISORY', 'DESCRIPTION', 'DUE_DATE', 'SEV','DUE','HOSTNAME'])

	
	for ADVISORY,DESCRIPTION,DUE_DATE,SEV,DUE,HOSTNAME in allentries:
		#output CSV row
		if DUE=="":
			DUE=" "
		OutputWriter.writerow([ADVISORY,DESCRIPTION,DUE_DATE,SEV,DUE,HOSTNAME])
		
	
def generate_html_report(dbconn,hostname_string,advisory_string,missing):
	
	
	cursor = dbconn.cursor()
	table="lssecfixes"
	fileobj=None
	filename=""
	
	#select distinct(ADVISORY) from lssecfixes order by ADVISORY desc;
	#select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes order by ADVISORY desc, hostname desc;
	
	#get all the APARs represented
	where_clause=gen_where_clause(hostname_string,advisory_string,missing)
			
	#print "sql select distinct(ADVISORY),DUE_DATE,DESCRIPTION,SEV from lssecfixes %s order by ADVISORY desc"%(where_clause)

	logging.debug("select distinct(ADVISORY),DESCRIPTION,DUE_DATE,SEV,DUE,hostname from lssecfixes %s order by ADVISORY desc"%(where_clause))
	cursor.execute("select distinct(ADVISORY),DESCRIPTION,DUE_DATE,SEV,DUE,hostname from lssecfixes %s order by ADVISORY desc"%(where_clause))
	#cursor.execute("select distinct(ADVISORY),DESCRIPTION,DUE_DATE,SEV,DUE from lssecfixes %s order by ADVISORY desc"%(where_clause))
	#cursor.execute("select distinct(lssecfixes.ADVISORY),lssecfixes.DUE_DATE,lssecfixes.DESCRIPTION,lssecfixes.SEV from lssecfixes order by ADVISORY desc")
	
	allentries=cursor.fetchall()
	
	print output_html_heading(None)
	
	#print "Advisories: "
	print """
	<div style="border-style: dotted; padding: 20px; background-color: rgb(238, 238, 238);">
  <h2>APARs</h2>

  <p>The following APARs are represented in this report. Click on a specifc Apar to see the results for that APAR:  </p>
  <table border="1" summary="The following APARs are represented in this report">
    <caption>
      APARs
      <a name="APAR_List" id="APAR_List"></a>
    </caption>
	<tr>
      <td>Advisory</td>
      <td>Sev</td>
      <td>Due Date </td>
      <td>Description</td>
	  <td>Lssecfixes Results</td>
    </tr>

	"""

	
	prev_advisory=""
	prev_description=""
	advisory_arr=[]
	due_arr=[]
	
	host_results={}
		
	#print "num entries: "+str(len(allentries))
	for ADVISORY,DESCRIPTION,DUE_DATE,SEV,DUE,HOSTNAME in allentries:
		#print ADVISORY,DUE_DATE,DESCRIPTION,SEV
		link="A"+ADVISORY
		link=link.replace(':','_')
		link=link.replace('.','_')

		# Clean up any non-ascii unicode characters
		#make sure we have a unicode string
		#test=DESCRIPTION
		#test = unicode(test, "iso-8859-1")
		#http://stackoverflow.com/questions/2700859/how-to-replace-unicode-characters-by-ascii-characters-in-python-perl-script-give
		DESCRIPTION=unicodedata.normalize('NFKD',DESCRIPTION).encode('ascii','ignore')
		#Title=re.sub("\[CentOS\]\s+\[CentOS\-announce\]\s+","",DESCRIPTION)
		
		
			
		if prev_advisory=="":
			prev_advisory=ADVISORY
		elif prev_advisory != ADVISORY:
			#print "count: "
			#print len(advisory_arr)
			
			if len(advisory_arr)>0:
				print_advisories_table(advisory_arr,due_arr)
			
				advisory_arr=[]
				due_arr=[]
			
			prev_description=""
			prev_advisory=""
		
		if prev_description !=DESCRIPTION:
			advisory_arr.append({"link":link, "ADVISORY":ADVISORY, "SEV":SEV, "DUE_DATE":DUE_DATE, "DESCRIPTION":DESCRIPTION})
		
		#print >> sys.stderr,"Appending %s for hostname: %s"%(ADVISORY,HOSTNAME)
		if host_results.has_key(HOSTNAME):
			pass
			
		else:
			#print >> sys.stderr,"new"
			host_results[HOSTNAME]=[]
			
		host_results[HOSTNAME].append({"ADVISORY":ADVISORY, "DUE_DATE":DUE_DATE, "DESCRIPTION":DESCRIPTION, "DUE":DUE, "SEV":SEV})
		#print >> sys.stderr,(host_results)
			
			
		due_arr.append(DUE)
		
		prev_description=DESCRIPTION
		prev_advisory=ADVISORY
			
	#print >> sys.stderr,(host_results)
	#print "<pre>"
	#pp.pprint(host_results)
	#print "</pre>"
	#sys.exit(1)
	
	#print any left over advisories
	if len(advisory_arr)>=1:
		print_advisories_table(advisory_arr,due_arr)
	
	#print "<pre>"
	#print host_results
	#print "</pre>"
		
	#print out ending of the APAR table
	print """</table>
  <p><br />
	</p>
	</div>
	<br /><br /><br /><br />
	"""
	
	
	
	
	#rpm_regex=re.compile("(?P<package_title>[A-Za-z0-9\-\_\+]+)\-(?P<package_version>(?:2002d|\d+\.)\S+)\.(?:i386|x86_64|i586|i686|s390|s390x|noarch|ia64|ia32e|athlon|ppc|centos)")
	
	#select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes order by ADVISORY desc, hostname desc;
	
		
	print "<h2>Lssecfixes Results </h2>"
	print """<a name="due_date_explanation" id="due_date_explanation"></a>DUE DATE EXPLANATION:
	<pre>
   '*' = Security fix is overdue.
   '+' = Security fix is overdue and has a revision
         level higher than the current system.
         (e.g. 4.3.2.x -> 4.3.3.x)
   '-' = Security fix is not yet due, but has a higher
         revision level than the current system.
   ' ' = Security fix is not yet due.
   'I' = Security fix has already been installed.
   'E' = Equivalent e-fix has been applied.
   'W' = Workaround has been implemented or affected service not running.
  'NA' = Security fix does not apply.
   'F' = Security fix has not been released (future).
   'A' = Security fix has been released, but not formally announced.
	</pre>"""

	#get all the APARs represented
	#print "sql: select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes %s order by ADVISORY desc, hostname desc"%(where_clause)
	cursor.execute("select ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb from lssecfixes %s order by ADVISORY desc, hostname desc"%(where_clause))
	allentries=cursor.fetchall()
	
	prev_advisory=""
	advisory_arr=[]

	
	for ADVISORY,DUE_DATE,DESCRIPTION,DUE,SEV,hostname,report_date,lssecfixes_version,fixdb in allentries:
		anchor="A"+ADVISORY
		anchor=anchor.replace(':','_')
		anchor=anchor.replace('.','_')
		
		# Clean up any non-ascii unicode characters
		#make sure we have a unicode string
		#test=DESCRIPTION
		#test = unicode(test, "iso-8859-1")
		#http://stackoverflow.com/questions/2700859/how-to-replace-unicode-characters-by-ascii-characters-in-python-perl-script-give
		DESCRIPTION=unicodedata.normalize('NFKD',DESCRIPTION).encode('ascii','ignore')
		
		if prev_advisory=="":
			prev_advisory=ADVISORY
		elif prev_advisory != ADVISORY:			
			if len(advisory_arr)>0:
				print_advisories(advisory_arr)
			
			advisory_arr=[]
				
			prev_advisory=ADVISORY

			
		advisory_arr.append({"anchor":anchor, "ADVISORY":ADVISORY, "DUE_DATE":DUE_DATE, "DESCRIPTION":DESCRIPTION, "DUE":DUE, "SEV":SEV, "hostname":hostname, "report_date":report_date,
							"lssecfixes_version":lssecfixes_version, "fixdb":fixdb})
		
		
					
			
		
	#print any left over advisories
	if len(advisory_arr)>=1:
		print_advisories(advisory_arr)
		
		if prev_advisory != ADVISORY:
			prev_advisory=ADVISORY
			
	

	
	#print footer
	print """<p class="note">Version %s, last updated %s.
	&nbsp;Created by Steve McKay, 2011.</p>

	<!-- start popup footer //////////////////////////////////////////// -->
	<div id="popup-footer">
	<div class="hrule-dots">&nbsp;</div>

	<div style="clear: both;">&nbsp;</div>

	</div>

	<!-- stop popup footer //////////////////////////////////////////// -->
	</div>

	<!-- stop main content --></div>

	<!-- stop content //////////////////////////////////////////// -->
	</body>
	</html>
	"""%(VERSION,Last_Updated)
		
#subclass OptionParser to make the epilog not strip the newlines - http://stackoverflow.com/questions/1857346/python-optparse-how-to-include-additional-info-in-usage-output
class MyParser(optparse.OptionParser):
	def format_epilog(self, formatter):
		return self.epilog
			
#call main function
if __name__ == "__main__":

	#cmd line options
	pathname, scriptname = os.path.split(sys.argv[0])
	
	version_string="%s %s - smckay@us.ibm.com"%(scriptname,VERSION)
	#parser =MyParser(version="%prog 1.0 - smckay@us.ibm.com",
	
	parser =MyParser(version=version_string,
	epilog=
"""Examples:

#Load one lssecfixes data file
%s -l -i folder/lssec_fixes_output_for_server.txt

#Load all the lssecficxes files in the directory
%s -l -d folder_with_multiple_lssec_fixes_files/

#create a report based on what is in the database for all hosts and redirect to html file
%s -r html > lssecfixes_report.html

#create a report for one host and redirect to html file
%s -r html -m server > lssecfixes_report_sample.html

#create a report for multiple hosts and redirect to html file
%s -r html -m "server1,server2" > lssecfixes_report_sample.html

#create a html report for one advisory and redirect to html file
%s -r csv -a 2011:0487.1 > lssecfixes_report_sample.html

#create a html report for multiple advisories and redirect to html file
%s -r html -a "2011:0487.1,2010:2605.1" > lssecfixes_report_sample.html

#create a csv report (output is by default lssecfixes_output.csv)
%s -r csv 

#create a report of only the missing advisories
%s -r csv --missing

#list servers in the db
%s -s

#list advisories in the db
%s -V

""" %(scriptname,scriptname,scriptname,scriptname,scriptname,scriptname,scriptname,scriptname,scriptname,scriptname,scriptname)
)
	hostname=""
	
	parser.add_option('-i', '--Input_file', help='Patching Detail Report from Lssecfixes', type="string", dest="input_file")
	parser.add_option('-d', '--input_Directory', help='Directory that holds multiple lssecfixes output files', type="string", dest="input_directory")
	#parser.add_option('-o', '--output_file', help='File to create based on input file', type="string", dest="output_file")
	parser.add_option('-l', '--Load', help='Load the files into the db', action="store_true", dest="load")
	parser.add_option('-r', '--Report', help='Create a report [csv|html]', type="string", dest="report")
	parser.add_option('-m', '--hostnaMe', help='host(s) to analyze', type="string", dest="hostname")
	parser.add_option('-a', '--Advisory', help='advisory to analyze', type="string", dest="advisory")
	parser.add_option('-s', '--servers', help='List servers in the db', action="store_true", dest="servers")
	parser.add_option('-v', '--adVisories', help='List advisories in the db', action="store_true", dest="advisories")
	parser.add_option('-g', '--logging-level', help='Logging Level - critical/error/warning/info/debug', type="string", dest="logging_level")
	parser.add_option('-n', '--missing', help='generate a report of only the missing advisories', action="store_true", dest="missing")
	
	#TODO: add switch to list hostnames in db
	#TODO: add switch to list APARS in db
	#Load CIRAT/
	
	#pp.pprint(parser.parse_args())
	(options,args)=parser.parse_args()
	#(option, arg) = parser.parse_args(sys.argv)
	
	if (options.logging_level!=None):
		if LOGGING_LEVELS.has_key(options.logging_level):
			print "*Setting logging level to %s"%(options.logging_level)
		else:
			print >> sys.stderr,"**Don't know how to handle logging Level %s"%(options.logging_level)
			print >> sys.stderr,"**Supported levels are ",LOGGING_LEVELS.keys()
			parser.print_help()
			sys.exit(1)
		
		logging_level = LOGGING_LEVELS.get(options.logging_level, logging.NOTSET)	
		logging.basicConfig(level=logging_level,
						  format='%(asctime)s %(levelname)s: %(message)s',
						  datefmt='%Y-%m-%d %H:%M:%S')

	else:
		#if the logging level is not set, set it to critical
		logging_level = LOGGING_LEVELS.get('error', logging.NOTSET)	
		logging.basicConfig(level=logging_level,
						  format='%(asctime)s %(levelname)s: %(message)s',
						  datefmt='%Y-%m-%d %H:%M:%S')
						  
	dbconn= None

	if (os.path.exists('lssecfixes.sqlite')):	
		dbconn = connect('lssecfixes.sqlite')

	
	#List servers in the db
	if (options.servers!=None):
		#ensure db is there
		if (not os.path.exists('lssecfixes.sqlite')):
			loggign.error("\n**ERROR: You must load data prior to running a report\n")
			parser.print_help()
			sys.exit(1)
		
		list_servers_in_db()
		
	#List servers in the db
	if (options.advisories!=None):
		#ensure db is there
		if (not os.path.exists('lssecfixes.sqlite')):
			logging.erorr("\n**ERROR: You must load data prior to running a report\n")
			parser.print_help()
			sys.exit(1)
		
		list_advisories_in_db()
	
	if (options.load==None and options.report==None and options.advisories==None and options.servers==None):
		logging.error("\n**ERROR: You must specify to load or report\n")
		parser.print_help()
		sys.exit(1)
		
	#Load Data
	if (options.load!=None):
		#print "HERE"
		#create db
		create_table=False
		#see if the db file exists
		#print os.path.exists('lssecfixes.sqlite')
		#print os.path.isfile('lssefixes.sqlite')
		if (os.path.exists('lssecfixes.sqlite')==False):
			create_table=True
			logging.debug("lssecfixes.sqlite doesn't exist")
		
		#if create_table==True:
		dbconn = connect('lssecfixes.sqlite')
		logging.debug("creating lssecfixes.sqlite if not exists")
		cursor=dbconn.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS \"lssecfixes\" (\"ADVISORY\" VARCHAR ,\"DUE_DATE\" VARCHAR,\"DESCRIPTION\" VARCHAR,\"DUE\" VARCHAR,\"SEV\" VARCHAR,\"inserted\" DATETIME,\"last_updated\" DATETIME, \"hostname\" VARCHAR, \"report_date\" VARCHAR, \"lssecfixes_version\" VARCHAR, \"fixdb\" VARCHAR)")
		logging.debug("commit")
		dbconn.commit()
		#else:
		#	print "found existing lssecfixes.sqlite"
	

	
	#Create Report
	#import pdb; pdb.set_trace()
	if (options.report!=None):
		#if options.hostname==None:
		#	hostname=""
		#else:
		# hostname=options.hostname 
		#if options.advisory==None:
		#	advisory=""
		#else:
		#	advisory=options.advisory
		
		#print "hostname: %s, advisory: %s, missing: %s"%(options.hostname,options.advisory,options.missing)
		if options.report.upper()=="HTML":
			generate_html_report(dbconn,options.hostname,options.advisory,options.missing)
		elif options.report.upper()=="CSV":
			generate_csv_report(dbconn,options.hostname,options.advisory,output_file,options.missing)
		else:
			logging.error("\n**ERROR: Don't know how to handle report type %s\n"%(options.report))
			parser.print_help()
			sys.exit(1)
	#Do the load
	if (options.load!=None):
		#ensure db is there
		if (not os.path.exists('lssecfixes.sqlite')):
			logging.error("\n**ERROR: You must load data prior to running a report\n")
			parser.print_help()
			sys.exit(1)
		
		#ensure at least download or analyze was selected
		if (options.input_file==None and options.input_directory==None):
			logging.error("\n**ERROR: You must specify an input file or directory to analyze\n")
			parser.print_help()
			sys.exit(1)
		
		#if -d is specified
		if (options.input_directory!=None):
			input_directory=options.input_directory
			
			#if the input_directory doesn't have a trailing / add it
			if input_directory[-1] is "/":
				input_directory=input_directory[:-1]
			
			
			if (os.path.exists(input_directory)==False):
				logging.error("could not find directory: "+input_directory)
				parser.print_help
				sys.exit(1)
			else:
				for file in os.listdir(input_directory):
					#print "file: "+file
					#skip directories - http://www.penzilla.net/tutorials/python/fileio/
					if (os.path.isdir(input_directory+"/"+file)):
						continue
					elif(os.path.isfile(input_directory+"/"+file)):
						parse_n_load_lssecfixes(dbconn,input_directory+"/"+file)	
					else:
						logging.error("\n**ERROR: Can't tell what %s is\n"%(input_directory+"/"+file))
						parser.print_help()
						sys.exit(1)
					
		
		#elseif -i is specified
		elif (options.input_file!=None):
			file=options.input_file
			parse_n_load_lssecfixes(dbconn,file)
			
		

		
				
					

