#---------------------------------------------------------------------------------------------
#
# Python3 script to pull basic information from a single or list of CAP-1000's via telnet.
# 
# 	Version: 0.4
# 	Last updated: 10/2/19
#
#---------------------------------------------------------------------------------------------

import getpass
import telnetlib
import time
import re
import os
import sys

def printHelp():
		print("Help")
		print("To run, a seperate file containing a list of IP's")
		print ("must be stored in the same directory as this script")
		print ("and labeled iplist.txt")

def main():
	# Specifies the name of the file containing IP's you want to verify.
	# Filename must be 'iplist.txt' for this script to work.
	# List one IP per line.
	try:
		iplist = open("iplist.txt")
		#iplist = open(os.path.dirname(os.path.realpath(__file__))"iplist.txt")
		
	except FileNotFoundError:
		
		print(FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), 'iplist'))
		sys.exit(2)
	
	# User login information via getpass module
	user = input("Enter username: ")
	password = getpass.getpass()

	# Specifies the name of the file containing IP's you want to verify.
	# Filename must be 'iplist.txt' for this script to work.
	# List one IP per line.
	
		
	for line in iplist:
		try:
			Host = line.strip("\n")    
			print("Verifying",Host)	
			tn = telnetlib.Telnet(Host)

			# If you have issues connecting to a host enable telnet debugging.	
			#tn.set_debuglevel(5)

			tn.read_until(b"login: ")   
			tn.write(user.encode('ascii') + b"\n")
			tn.read_until(b"Password: ")
			tn.write(password.encode('ascii')+b"\n")
			time.sleep(2)

			# Specify the command required to run.
			# This can be changed depending on your desired level
			# output required. This script is only setup to parse
			# a few fields but you can add additional fields below.
			# "ConfigDisplay" = Full Cap config dump including input and output
			# "ConfigDisplay -b" = Basic config
			# "ConfigDisplay -l" = Cap license information
			# "ConfigDisplay -b -l" = Basic Config and License information
			# 6a 65 74 68 6f 6d 70 73 6f 6e
			payload = tn.write(b"ConfigDisplay -o\n")
			time.sleep(1)
			payload = tn.read_very_eager().decode('ascii')
			tn.close()
			#print(payload)

			# Start of output parsing. Additional parameters can be defined here
			# depending on your needs. Pattern below was kindly supplied by jbaez.
			#payload = output.decode('ascii')	
		
			parse(payload)
		
		except (TimeoutError, ConnectionRefusedError) :
			print ("unable to connect to " + Host)
			
	iplist.close()

def parse(payload):
	pattern = re.compile(r".*CherryPicker Manager:\ +(?P<CherryPickerMgr>.*?)$"
						 r".*?Splicer\ +Name:\ +(?P<SplicerName>.*?)$"
						 r".*?IP\ +Address:\ +(?P<IPAddress1>.*?)$"
						 r".*Revision:\ +(?P<Revision>.*?)$"
						 r".*Total\ +RAM:\ +(?P<RAM>.*?)$"
						 r".*NTP\ +server:\ +(?P<NTP>.*?)$"
						 r".*CPR\ +Mode:\ +(?P<CPRMode>.*?)$"
						 r".*?Output\ +Port:\ +(?P<outputportname1>.)$",
						 re.MULTILINE | re.DOTALL)
	if pattern is None:
			print('Failed to compile regex pattern...')

	for cap1000 in pattern.finditer(payload):

		# Enable to debug the above pattern.
		print(cap1000.groups())

		cherrypicker_mgr = cap1000.group('CherryPickerMgr')
		splicer_name = cap1000.group('SplicerName')
		ip_address_01 = cap1000.group('IPAddress1')
		revision = cap1000.group('Revision')
		cpr_mode = cap1000.group('CPRMode')
		output_port_01 = cap1000.group('outputport1')


		# There are	two styles of output available.
		# The following is the default and prints in a list
		# for easy reading while running.

		#print('		cherrypicker_mgr = %s' % (cherrypicker_mgr))
		#print('		splicer_name = %s' % (splicer_name))
		#print('		ip_address = %s' % (ip_address))
		#print('		revision = %s' % (revision))
		#print('		cpr_mode = %s' % (cpr_mode))

		# This style of output would be easier if you are planning to input to another script
		# or program e.g. Excel
		#print('%s (%s, %s): [CPR Mode: %s]' % (cherrypicker_mgr, ip_address, revision, cpr_mode))
	
		
if __name__ == "__main__":
	main()
