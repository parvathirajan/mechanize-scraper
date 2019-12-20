# -*- coding: utf-8 -*-
"""
#############################################################################################
# Script Name:			web_scraper.py
# Project Name:			MINE
# Writen By:			Systech Solutions
# Date Written:			Dec 16, 2019
#
# Description:			This script is used to connect the Webpage and download the data.
#
# Parameters:			
#
# Date Modified:		
# Modified By:			
#
# Execution example:	python web_scraper.py
#############################################################################################
"""

from __future__ import print_function
import mechanize
from bs4 import BeautifulSoup
#import argparse
#import urllib3
import os, sys
import datetime
import logging
import traceback
import signal
from http.cookiejar import CookieJar

if sys.version_info[0] == 2:
	import ConfigParser as configparser
else:
	import configparser
  
def getConfig(config_file, config_item):
	"""
	Get the configuration items or credentials for the application name passed
	"""
	config = configparser.RawConfigParser()
	config.read(config_file)
	details_dict = dict(config.items(config_item))
	return details_dict

def chk_err(inp_str):
	"""
	for checking error
	"""
	if 'FATAL_ERROR:' in inp_str:
		# Check the status of the parents process
		check_subprocess_status()
		log_error(inp_str)
	else:
		return inp_str
	
	
def check_subprocess_status():
	"""
	for checking the process status and kill process if parent terminated
	"""
	gpid = int(os.popen("ps -p %d -oppid=" % os.getppid()).read().strip())
	ppid = int(os.getppid())
	pid = int(os.getpid())
	if gpid < 2:
		if ppid < 2:
			logging.info("Parent process has terminated, killing child process id:" + str(pid))
			os.kill(pid, signal.SIGKILL)
		else:
			logging.info("Grand Parent process has terminated, killing Parent process id:" + str(ppid) + " and Child process id:" + str(pid))
			os.kill(ppid, signal.SIGKILL)
			os.kill(pid, signal.SIGKILL)


def log_error(email_body):
	"""
	for logging Error, sending email and exiting process with error
	"""
	#logging.error(email_body)
	#send_mail(from_email_addr, to_email_addr, mail_subject, mail_text, files=log_file, send_cc=cc_email_addr)
	ppid = int(os.getppid())
	os.kill(ppid, signal.SIGKILL)
	sys.exit(1)


class clsBrowserConnect:
	
	def __init__(self, username, password, url):
		self.username = username
		self.password = password
		self.url = url
	
	def openpage(self, browswer_object = None, passed_url = None):
		"""
		Used to open the pages with HTTP responses and browser object.
		"""
		if passed_url is None:
			browswer_object.open(self.url)
			return browswer_object
		else:
			browswer_object.open(passed_url)
			logging.info("Redirected to the specified URL: "+ passed_url)
			return browswer_object
		
	def logintoweb(self):
		"""
		Get the Webpage as input and return the response as HTML after the successful login
		"""
		try:
			logging.info("Started application at: "+ curr_datetime)
			cj = CookieJar()
			br = mechanize.Browser()
			br.set_cookiejar(cj)
			br.open(self.url)
			br.select_form(name="loginForm")
			br.form['login_id'] = self.username
			br.form['password'] = self.password
			br.submit()
			print(br.geturl())
			logging.info("Form has been submitted successfully. \nResponse: "+ str(br))
			return br
		except Exception as e:
			err_msg = "FATAL_ERROR: In Login to Web : {0}\n\n{1}".format(e, traceback.format_exc())
			raise Exception(str(err_msg))
			
	def getdata(self, resp_obj, ret_url, filename):
		"""
		Download the data from web with the base url of the file which is present in the server
		"""
		resp_obj.retrieve(ret_url,filename)
		return resp_obj

if __name__ == '__main__':
	
	try:

		scriptnm = 'web_scraper'
		mail_subject = 'Error While executing script ' + scriptnm
		
		#Required Script Variables from the Configuration file
		script_path = os.path.abspath(os.path.dirname(__file__))
		config_file = (os.path.expanduser(os.path.join(script_path,'.'+scriptnm+'.cfg')))
		print(config_file)
		config = getConfig(config_file, 'rentrak')

		username	= config['username']
		password	= config['password']
		
		#Define Script Variables
		mail_subject = 'Error While executing script ' + scriptnm
		curr_datetime = str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
		
		log_file_nm = '{}_{}.log'.format(scriptnm, curr_datetime)
		log_file = os.path.expanduser(os.path.join(script_path,log_file_nm))
		
		logging.basicConfig(filename=log_file, 
					  format='%(asctime)s:%(msecs)09d %(filename)s (%(lineno)d) %(levelname)s   : %(message)s', 
					  datefmt='%Y%m%d:%H:%M:%S', 
					  level=logging.INFO)
		print(log_file)
		#Create connection with the web server
		scraper_obj = clsBrowserConnect(username, password, 'https://ondemand.rentrak.com')
		
		resp = scraper_obj.logintoweb()
		#print(resp)
		
		rd_url = "https://ondemand.rentrak.com/reports/xtns_by_provider.html"
		rd_url_response = scraper_obj.openpage(resp, rd_url)
		rd_url_response.geturl()
		#print(rd_url_response)

		#print(rd_url_response.geturl())
		#print(rd_url)
		print(rd_url_response.geturl() == rd_url)
		if rd_url_response.geturl() == rd_url:
			logging.info("Redirected Successfully - "+ rd_url)
		else:
			raise Exception
		
        rd_url_response.forms()[4].name
        rd_url_response.form = rd_url_response.forms()[4]
        #i=0
        """
        for control in rd_url_response.form.controls:
            print(control)
            print(control.type, control.name)
            i=i+1
            if 
            print(i)
            print()
        """
        ctrl_name = 'date_range'
        #rd_url_response.form.find_control(ctrl_name, type='select').readonly = False
        rd_url_response.form.find_control(ctrl_name, type='select').value = ["LAST_FULL_MONTH"]
        
        #values = map(int, [item.name for item in rd_url_response.form.find_control(ctrl_name, type='select').items])
            
        response = rd_url_response.submit()
        
		soup = BeautifulSoup(rd_url_response.response().read().decode('utf-8'), "html.parser")
		rpt_extract_list = soup.find_all("a", string="Excel")
		report_file_url = rpt_extract_list[0]['href']
		print(report_file_url)
		#On the Successful redirection we need to call the below func to retieve data form url
		ret_url = scraper_obj.url+report_file_url
		print(ret_url)
		rpt_name = os.path.basename(os.path.splitext(rd_url)[0])
		rpt_file = scriptnm + '_' + rpt_name + '_'+ curr_datetime +'.xls'
		print(rpt_file)
		scraper_obj.getdata(resp, ret_url, rpt_file)

	except Exception as e:
		print('FATAL_ERROR: ' + " from main exception : {0}\n\n{1}".format(e, traceback.format_exc()))


#import pandas as pd
#x= pd.read_excel('web_scraper_xtns_by_provider_20191218_002537_311057.xlsx')




