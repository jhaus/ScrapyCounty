# -*- coding: utf-8 -*-
# -*- author: mxiz -*-
import time
import gspread
import csv
import os
import subprocess
from zillow_function import findzillow
import httplib2
import random
import multiprocessing
import time
from apiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.service_account import ServiceAccountCredentials
import tkMessageBox


MRS_ADDS = 'https://docs.google.com/spreadsheets/d/1v5sNJuIiLGwU6fH9Kpfr9XRxQCxrf7bx_PR_1fNA_6Q/edit#gid=0'
ESS_ADDS = 'https://docs.google.com/spreadsheets/d/1isOSOsyvGFTuCZwuqEEkmou0uxWm9AVCrNx_V0_JDmc/edit#gid=0'
BGN_ADDS = 'https://docs.google.com/spreadsheets/d/1aZBeaENA0xjxqpmKYNDrjIM4c_zy-MhHuLaunmPLv98/edit#gid=0'
HTD_ADDS = 'https://docs.google.com/spreadsheets/d/1kjiHt_daqvIueDw6qD7wk75mTFo0_ubRUFCnHNn4J8E/edit#gid=0'
MIS_ADDS = 'https://docs.google.com/spreadsheets/d/1W-6ngztdGnx-N2-YA8v7dtOgw39OYi9cauYtMa4t-lw/edit#gid=0'
UNI_ADDS = 'https://docs.google.com/spreadsheets/d/1koChyqS8UbXCoWV662YY8zVXT57lR4snW6j5aMrU1Rw/edit#gid=0'
#TEST_ADD = 'https://docs.google.com/spreadsheets/d/1em7oEKzfA3qbNcHdn8d892y0rJvxjF5UnUY7XK6Yyik/edit#gid=0'
MEC_ADDS = 'https://docs.google.com/spreadsheets/d/1c2AiIahiFZFA37FCa5SJOcsWDXJQxa3qwmHw0rlB7eY/edit#gid=0'
MON_ADDS = 'https://docs.google.com/spreadsheets/d/1RHMczsQ6mpajEZT0gYcJqCXz3FR5SSZepxXZnGTXmy4/edit#gid=0'
PSC_ADDS = 'https://docs.google.com/spreadsheets/d/1zlClRl91bAcBtG1zA5NlyOHqUoV1wYHfnzyl_mof1qw/edit#gid=0'

KEY = 'flipnj-4f3fbac03d23.json'

morris = {'name': 'Morris', 'csv': 'morris_items.csv', 'add': MRS_ADDS}
essex = {'name': 'Essex', 'csv': 'essex_items.csv', 'add': ESS_ADDS}
bergen = {'name': 'Bergen', 'csv': 'bergen_items.csv', 'add': BGN_ADDS}
hunterdon = {'name': 'Hunterdon', 'csv': 'hunterdon_items.csv', 'add': HTD_ADDS}
union = {'name': 'Union', 'csv': 'union_items.csv', 'add': UNI_ADDS}
mercer = {'name': 'Mercer', 'csv': 'mercer_items.csv', 'add': MEC_ADDS}
middlesex = {'name': 'Middlesex', 'csv': 'middlesex_items.csv', 'add': MIS_ADDS}
monmouth = {'name': 'Monmouth', 'csv': 'monmouth_items.csv', 'add': MON_ADDS}
passaic = {'name': 'Passaic', 'csv': 'passaic_items.csv', 'add': PSC_ADDS}
#test = {'name': 'Test', 'csv': 'essex_items.csv', 'add': TEST_ADD}
'''
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetID, range='C6', valueRenderOption='FORMULA').execute()
print result['values'][0][0]
'''
COUNTY = [morris, essex, bergen, hunterdon, union, mercer, middlesex, monmouth, passaic]
'''
0             1       2      3        4    5   6    7      8    9
sale_date,sheriff_no,upset,att_ph,case_no,plf, att,address,dfd,schd_data
1      2            3           6          7         10       11        12       13
date, SHERIFF'S #, ADDRESS, Judegment,	NEW UPSET, PLF/DEF, ATTY/FIRM, DOCKET#, Zillow
'''
###
###
###
def scrapy(num, e):
	countyname = county['name']
	filename = county['csv']
	try:
		os.remove(filename)
	except OSError:
		pass
	print "%s county is starting ..." % countyname
	subprocess.call("scrapy crawl %s -o %s" % (countyname.lower(), filename), shell=True)
	e.set()
	print "%s county done scraping" % countyname

###
###
###
def backup(num, e):
	print "Backing Up ..."

	startrow = 6
	caseno = worksheet_old.cell(startrow, 2).value
	while caseno is not "":
		requests = []
		requests.append({
		    'insertDimension': {
		        "range": {"sheetId": 0, "dimension": 1, "startIndex": 5, "endIndex": 6},
		        "inheritFromBefore": False,
		    }
		})

		try:
			cell = worksheet_all.find(caseno)
			print caseno + "at: " + cell.value + " is deleted."
			requests.append({
			    'deleteDimension': {
				    "range": {
					    "sheetId": 0, "dimension": 'ROWS', "startIndex": cell.row, "endIndex": cell.row + 1,
				    },
			    }
			})
		except gspread.CellNotFound as err:
			print "Not Found in Sheet_All"

		requests.append({
		    'copyPaste': {
			    "source": {
				    "sheetId": worksheet_old_id, "startRowIndex": startrow - 1, "endRowIndex": startrow,
			    },
			    "destination": {
			    	"sheetId": 0, "startRowIndex": 5, "endRowIndex": 6,
			  },
				"pasteType": "PASTE_NORMAL",
		    }
		})
		batchUpdateRequest = {'requests': requests}
		service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()
		startrow = startrow + 1
		caseno = worksheet_old.cell(startrow, 2).value
		#print str(startrow) + " not null: " + str(caseno)

	print "--------------------------------------------------"
	print("\t\tBack up is done.")
	print "--------------------------------------------------"
	e.set()

###
###
###
def write_continue(num):
	SS_ADDRESS = county['add']
	filename = county['csv']

	worksheet_new_name = time.strftime("%m/%d/%Y")
	worksheet_new = get_gspread(SS_ADDRESS, worksheet_new_name)
	#new_no = find_sheetId(SS_ADDRESS, worksheet_new_name)
	new_no = '5187536'
	'''
	### Read Data ###
	'''
	print "Reading Data ..."
	try:
		with open(filename, "rb") as csvfile:
			filereader = csv.reader(csvfile)
			data = list(filereader)
			row_count = len(data)
	except IOError as err:
		print "No Such File: %s" % filename
		exit(0)

	print "--------------------------------------------------"
	print county['name'] + " County has " + str(row_count) + " items!"
	print "--------------------------------------------------"
	start = 127
	for line in data[117:]:
		#print line
		try:
			caseno = line[1]
			#print caseno
			cell = worksheet_all.find(caseno)
			Found = True
			date = worksheet_all.cell(cell.row, 1).value
			address = worksheet_all.cell(cell.row, 3).value
			address = address.replace(',', ' ')
			address = address.replace('\n', ' ')
			print str(cell.row) + "/" + str(cell.col) + ": " + str(cell.value)

			requests = []
			requests.append({
			    'copyPaste': {
				    "source": {
					    "sheetId": 0, "startRowIndex": cell.row - 1, "endRowIndex": cell.row, },
				    "destination": {
					  	"sheetId": new_no, "startRowIndex": start - 1, "endRowIndex": start, },
					"pasteType": "PASTE_NORMAL",
			    }
			})
			batchUpdateRequest = {'requests': requests}
			service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()
			worksheet_new.update_cell(start, 6, line[2]) #upset
			if date != line[0]:
				worksheet_new.update_cell(start, 1, date + "->" + line[0]) #date
			#worksheet_new.update_cell(start, 16, line[63]) #status

		except gspread.CellNotFound as err:
			print ("CellNotFound!")
			Found = False
			if line[0] == line[9] or line[9] == 0:
				worksheet_new.update_cell(start, 1, line[0]) #date
			else:
				worksheet_new.update_cell(start, 1, line[9] + '->' + line[0]) #date
			worksheet_new.update_cell(start, 2, line[1]) #shriff
			worksheet_new.update_cell(start, 12, line[4]) #case
			#worksheet_new.update_cell(start, 6, line[55]) #add
			address = line[7].replace('\n', ' ')
			worksheet_new.update_cell(start, 6, line[2]) #upset
			if line[3] == '':
				worksheet_new.update_cell(start, 11, line[6]) #date
			else:
				worksheet_new.update_cell(start, 11, line[6] + '\nPhone: ' + line[3]) #date
			#worksheet_new.update_cell(start, 16, line[1]) #status
			worksheet_new.update_cell(start, 10, 'PLF: ' + line[5] + '\nDEF' + line[8]) #plantiff
		'''
		except ValueError as err:
			print "value error"
			exit(0)
		'''
		zipcode = address.split(" ")[-1:][0]
		#print zipcode
		if zipcode.isdigit():
			#print "IS DIGIT"
			zillow = findzillow(address, zipcode)
		else:
			zillow = findzillow(address, '')
			if zillow[3] != '':
				print "!!!Address replaced"
				address = address + ' ' + zillow[3] 
		#print zillow
		worksheet_new.update_cell(start, 13, zillow[1]) #zestimate
		if zillow[2] == '' and Found:
			#print line
			worksheet_new.update_cell(start, 3, address) #add	
		else:
			requests = []
			requests.append({
			    'updateCells': {
				    "rows": { 
				    	"values": [{
				    		"userEnteredValue": {
				    			"formulaValue": '=HYPERLINK("' + zillow[2] + '","' + address + '")', }, }], },
				    "fields": "*",
				    "start": {
				    	"sheetId": new_no, "rowIndex": start - 1, "columnIndex": 2,},}
			})
			batchUpdateRequest = {'requests': requests}
			service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()

		start=start+1

def new_sheet(num, e):
	e.wait()
	SS_ADDRESS = county['add']
	filename = county['csv']

	try:
		print "Creating new sheet ..."
		requests = []
		new_no = random.randrange(1, 99999999)
		worksheet_new_name = time.strftime("%m/%d/%Y")
		requests.append({
		    'addSheet': {
			    "properties": {"sheetId": new_no, "title": worksheet_new_name,
			}, }
		})
		# Copy Title
		requests.append({
		    'copyPaste': {
			    "source": {
				    "sheetId": 0, "startRowIndex": 0, "endRowIndex": 4,},
			    "destination": {
			    	"sheetId": new_no, "startRowIndex": 0, "endRowIndex": 4,},
				"pasteType": "PASTE_NORMAL", }
		})
		batchUpdateRequest = {'requests': requests}
		service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()
		worksheet_new = get_gspread(SS_ADDRESS, worksheet_new_name)
	except HttpError as err:
		print "Google Error. Already Exists"
		exit(0)
	'''
	### Read Data ###
	'''
	print "Reading Data ..."
	try:
		with open(filename, "rb") as csvfile:
			filereader = csv.reader(csvfile)
			data = list(filereader)
			row_count = len(data)
	except IOError as err:
		print "No Such File: %s" % filename
		exit(0)

	print "--------------------------------------------------"
	print county['name'] + " County has " + str(row_count) + " items!"
	print "--------------------------------------------------"
	start = 6
	for line in data[1:]:
		#print line
		try:
			caseno = line[1]
			#print caseno
			cell = worksheet_all.find(caseno)
			Found = True
			date = worksheet_all.cell(cell.row, 1).value
			address = worksheet_all.cell(cell.row, 3).value
			address = address.replace(',', ' ')
			address = address.replace('\n', ' ')
			print str(cell.row) + "/" + str(cell.col) + ": " + str(cell.value)

			requests = []
			requests.append({
			    'copyPaste': {
				    "source": {
					    "sheetId": 0, "startRowIndex": cell.row - 1, "endRowIndex": cell.row, },
				    "destination": {
					  	"sheetId": new_no, "startRowIndex": start - 1, "endRowIndex": start, },
					"pasteType": "PASTE_NORMAL",
			    }
			})
			batchUpdateRequest = {'requests': requests}
			service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()
			worksheet_new.update_cell(start, 6, line[2]) #upset
			if date != line[0]:
				worksheet_new.update_cell(start, 1, date + "->" + line[0]) #date
			#worksheet_new.update_cell(start, 16, line[63]) #status

		except gspread.CellNotFound as err:
			print ("CellNotFound!")
			Found = False
			if line[0] == line[9] or line[9] == 0:
				worksheet_new.update_cell(start, 1, line[0]) #date
			else:
				worksheet_new.update_cell(start, 1, line[9] + '->' + line[0]) #date
			worksheet_new.update_cell(start, 2, line[1]) #shriff
			worksheet_new.update_cell(start, 12, line[4]) #case
			#worksheet_new.update_cell(start, 6, line[55]) #add
			address = line[7].replace('\n', ' ')
			worksheet_new.update_cell(start, 6, line[2]) #upset
			if line[3] == '':
				worksheet_new.update_cell(start, 11, line[6]) #date
			else:
				worksheet_new.update_cell(start, 11, line[6] + '\nPhone: ' + line[3]) #date
			#worksheet_new.update_cell(start, 16, line[1]) #status
			worksheet_new.update_cell(start, 10, 'PLF: ' + line[5] + '\nDEF' + line[8]) #plantiff
		'''
		except ValueError as err:
			print "value error"
			exit(0)
		'''
		zipcode = address.split(" ")[-1:][0]
		#print zipcode
		if zipcode.isdigit():
			#print "IS DIGIT"
			zillow = findzillow(address, zipcode)
		else:
			zillow = findzillow(address, '')
			if zillow[3] != '':
				print "!!!Address replaced"
				address = address + ' ' + zillow[3] 
		#print zillow
		worksheet_new.update_cell(start, 13, zillow[1]) #zestimate
		if zillow[2] == '' and Found:
			#print line
			worksheet_new.update_cell(start, 3, address) #add	
		else:
			requests = []
			requests.append({
			    'updateCells': {
				    "rows": { 
				    	"values": [{
				    		"userEnteredValue": {
				    			"formulaValue": '=HYPERLINK("' + zillow[2] + '","' + address + '")', }, }], },
				    "fields": "*",
				    "start": {
				    	"sheetId": new_no, "rowIndex": start - 1, "columnIndex": 2,},}
			})
			batchUpdateRequest = {'requests': requests}
			service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body=batchUpdateRequest).execute()

		start=start+1

def new_write(num, old_tab):

	# Get credentials
	# Get Google Sheets official API
	global service
	service = get_google_service()
	global county
	county = COUNTY[num]
	global spreadsheetID
	global SS_ADDRESS
	old_tab_name = old_tab
	SS_ADDRESS = county['add']
	spreadsheetID = SS_ADDRESS.split('/')[5]

	global worksheet_old
	global worksheet_old_id
	global worksheet_all_name
	global worksheet_all

	worksheet_old = get_gspread(SS_ADDRESS, old_tab_name)
	worksheet_old_id = find_sheetId(spreadsheetID, old_tab_name)
	worksheet_all_name = find_sheetname(spreadsheetID, 0)
	worksheet_all = get_gspread(SS_ADDRESS, worksheet_all_name)

	if worksheet_old_id is None or worksheet_all_name is None:
		print "No Such Tab Name"
		tkMessageBox.showerror("Error!", "Tab Name : %s is not found" % old_tab)
		exit(0)
	'''
	e1 = multiprocessing.Event()
	e2 = multiprocessing.Event()
	e = multiprocessing.Event()
	scrapyworker = multiprocessing.Process(name = "ScrapyWorker",
            target = scrapy,
            args = (num, e1,))

	backupworker = multiprocessing.Process(name = "GoogleSheet_backup",
            target = backup,
            args = (num, e2,))

	newsheetworker = multiprocessing.Process(name = "GoogleSheet_newsheet",
            target = new_sheet,
            args = (num, e,))

    ### scrapy ###
	scrapyworker.start()
    ### back up ###
	backupworker.start()
	### New Sheet ###
	newsheetworker.start()
	while not (e1.is_set() and e2.is_set()):
		time.sleep(1)
        print 'wait...'
	e.set()
	'''
	write_continue(num)


def get_gspread(SS_ADDRESS, sheetname):
	scope_gs = ['https://spreadsheets.google.com/feeds']
	credentials_gs = ServiceAccountCredentials.from_json_keyfile_name(KEY, scope_gs)
	gc = gspread.authorize(credentials_gs)
	sh = gc.open_by_url(SS_ADDRESS)
	worksheet = sh.worksheet(sheetname)
	return worksheet

def get_google_service():
	scope_gl = 'https://www.googleapis.com/auth/spreadsheets'
	credentials_gl = ServiceAccountCredentials.from_json_keyfile_name(KEY, scope_gl)
	http = credentials_gl.authorize(httplib2.Http())
	discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
	service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
	return service

def find_sheetId(spreadsheetID, sheetname):
	service = get_google_service()
	result = service.spreadsheets().get(spreadsheetId=spreadsheetID).execute()
	for item in result['sheets']:
		if item['properties']['title'] == sheetname:
			return item['properties']['sheetId']
	return None

def find_sheetname(spreadsheetID, sheetId):
	service = get_google_service()
	result = service.spreadsheets().get(spreadsheetId=spreadsheetID).execute()
	for item in result['sheets']:
		if item['properties']['sheetId'] == sheetId:
			return item['properties']['title']
	return None