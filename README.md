# ScrapyCounty
Implemented with Python 2.7 by Xi Zhang for Noah Luk at LNH Holding LLC

## Overview:
    Collecting sales data from <http://salesweb.civilview.com/>
    Counties supported:
    - Morris
    - Essex
    - Bergen
    - Hunterdon
    - Middlesex coming soon.

## Installation:
Check pip:
 - pip is already installed if you're using Python 2 >=2.7.9 or Python 3 >=3.4 downloaded from python.org, but you'll need to upgrade ir.<pip install -U pip>
 - Download pip <https://pip.pypa.io/en/stable/installing/>

### Part 1: (For scrapy crawler)
- Scrapy <http://scrapy.org/>
	>Install:  $ pip install scrapy

- Selenium <https://pypi.python.org/pypi/selenium>
	>Install: $ pip install selenium

- PhantomJS <http://phantomjs.org/>
	>Install: $ sudo pkg install phantomjs

    	Tip for Windows:
        	Change path for PhantomJS first

### Part 2:
- gspread (Google Spreadsheets Python API <https://github.com/burnash/gspread>)
	>Install: $ pip install gspread

- Obtain OAuth2 credentials from Google Developers Console
	[http://gspread.readthedocs.io/en/latest/oauth2.html]

- pyzillow <https://pypi.python.org/pypi/pyzillow/0.5.5>
	>Install: $ pip install pyzillow

- Obtain zillow's official API :
  	<http://www.zillow.com/howto/api/APIOverview.htm>
	
	Attention: 	
		1000 max search properties.

- Obtain PDF to Excel API:
	Replace line 22 in hunterdon_save.py
	<https://pdftables.com/pdf-to-excel-api>
	
	Attention: 
		50 max free convert. 
		Pay for more.

- DataBaker <https://scraperwiki.github.io/eot-docs/>
	>Install: pip install databaker

## Run:
	python scrapycounty.py
