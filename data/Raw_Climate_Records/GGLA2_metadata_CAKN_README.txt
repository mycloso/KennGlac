README

List of Data Products:
WC_A: Protocol Narrative and Standard Operating Procedures. A pdf file updated as needed.
WC_B: Map documenting location of stations participating in the network's climate monitoring. Data provided as 1) ESRI layer (.lpk), 2) JPEG, and 3) KMZ
WC_C: Site visit worksheets. One worksheet per site visit documenting in a standard form the condition of the site, actions taken, and final configuration. Packaded as a cumulative set of all worksheets for all stations in a particular year zipped into one file.
WC_D: Datalogger program code. The program source code installed into the dataloggers for all stations over a field season. Packaged as a ZIP of .CR1 files.
WC_E: Photos. One set of photos per site per field season used to document physical conditions. JPEG files wrapped into ZIP files for each site. All sites packaged subsequently packaged together as one ZIP file.
WC_F: Raw data. Raw data downloaded as a cumulative collection of station observations from the datalogger. Packaged as on ZIP file per field season containing one downloaded file from each station visited that year.
WC_G: Corrected data. Cumulative data file that has undergone quality control. See below for details.
WC_H: Annual operations report. Annual report summarizing operations and data in the form of an NPS NRR or NRDS publication.
WC_I: Calibration certificate images. Scanned images of sensor calibration records provided by the instrument vendor/servicer.
WC_J: Periodic Report. Multi-year climate analysis based on the parameters collected by stations, written in the form of an NPS NRR publication.

Listing of site names, locations, codes, and park units:

Site Code	Site Name	Park Code*	Latitude	Longitude	Elevation (ft)	Install Date
CREA2		Chicken Creek	WRST		62.1240		-141.8473	5240		8/21/2004
CTUA2		Chititu		WRST		61.2736		-142.6209	4544		8/20/2004
CCLA2		Coal Creek	YUCH		65.3041		-143.1570	958		9/16/2004
DKLA2		Dunkle Hills	DENA		63.2675		-149.5392	2651		8/1/2002
EVCA2		Eielson VC	DENA		63.4309		-150.3108	3652		6/4/2005
GGLA2		Gates Glacier	WRST		61.6029		-143.0132	4058		7/6/2005
RUGA2		Ruth Glacier	DENA		62.7097		-150.5397	3301		9/6/2008
SMPA2		Stampede	DENA		63.7478		-150.3281	1801		8/1/2002
TANA2		Tana Knob	WRST		60.9080		-142.9013	3740		7/5/2005
TEBA2		Tebay		WRST		61.1810		-144.3422	1880		7/8/2005
TKLA2		Toklat		DENA		63.5242		-150.0433	2920		6/16/2005
UPRA2		Upper Charley	YUCH		64.5167		-143.2022	3655		8/3/2005
WIGA2		Wigand		DENA		63.8142		-150.1094	1782		8/13/2013

*WRST:Wrangell-St. Elias National Park and Preserve, YUCH: Yukon-Charley Rivers National Preserve, and DENA: Denali National Park and Preserve.					

WC_G: Corrected Data details:
Quality control and record processing is completed annually following the procedures in SOP 11 of the Arctic, Central Alaska, and Southeast Alaska  Weather and Climate Vital Sign Monitoring Standard Operating Procedures 2017 (in review). 
The Aquatic Informatics Aquarius software is used for record processing. 
The network has used the software to meet its record processing needs, but its use does not constitute an endorsement by the U.S. Government.
Exported, corrected data series are saved as .csv files. 
Please cite this dataset as: Hill, K and Sousanes, PJ. (YYYY). National Park Service Central Alaska Inventory and Monitoring Network Quality Controlled Climate Dataset. Available online at https://irma.nps.gov/DataStore/Reference/Profile/2240059. Accessed MM-DD-YYYY.

The information below describes parameter codes, units, sensor heights, quality grades, approval levels, and interpolation types given in the WC_G Corrected Data files. 
More information is available in SOP11: Quality Control and Record Processing (https://irma.nps.gov/DataStore/Reference/Profile/2253025).

Parameter Code	Parameter		Time Interval	Units		Sensor Height
Date-Time	MM/DD/YYYY HH:MM	hourly		UTC time zone	--
RNIN		Rainfall		hourly total	inches		~2.5 meters
WSM		Wind Speed		hourly mean	mph		~2.5 meters
WDD		Wind Direction		hourly mean	degrees		~2.5 meters
ATF		Air Temperature		hourly mean	Farenheit	2 meters
RHP		Relative Humidity	hourly mean	percent		2 meters
BVV		Battery Voltage		hourly mean	volts		--
WDDP		Wind Direction		Peak Gust Dir.	degrees		~2.5 meters
WSMP		Wind Speed		hourly maximum	mph		~2.5 meters
SRW		Solar Radiation		hourly mean	W m-2		~2.5 meters
SDI		Snow Depth		hourly sample	inches		~2.5 meters
AT1L		Air Temperature		hourly minimum	Farenheit	2 meters
AT1H		Air Temperature		hourly maximum	Farenheit	2 meters
STF		Soil Temperature 1	hourly mean	Farenheit	10  cm
STF2		Soil Temperature 2	hourly mean	Farenheit	20 cm
STF3		Soil Temperature 3	hourly mean	Farenheit	50 cm
STF4		Soil Temperature 4	hourly mean	Farenheit	75 cm


Quality Grades, Approval Levels, and Interpolation Types			
Type		Description		Code
Grade		Unusable		-2
Grade		Undefined		 0
Grade		Partial			 4
Grade		Suspect			 6
Grade		Poor			 11
Grade		Good			 31

Interpolation	Preceding Avg.		 2
Interpolation	Discrete Value		 7
Interpolation	Inst. Values		 1

Approval	Undefined		 0
Approval	Working			 1
Approval	In Review		 2
Approval	Approved		 3
Approval	Rejected		 4
