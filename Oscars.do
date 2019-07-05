capture log close
log using Oscars.txt, text replace

* Oscars.do
*	reads OscarsCensus.xls from jobs.py, occ-level file for each movie from jobs.py
*	saves OscarsCensus.dta
*	collapses to a movie-level file, Oscars.dta
*		just one example of creating useful variables from the Census occupation codes.

clear all
set more off
pwd

dir Oscars*.xls

*import delimited OscarsCensus.xls,clear /* earlier stata version */
insheet using OscarsCensus.xls,clear
	describe
	summarize, sep(0)

*drop the directory ("movies/") prefix:
gen str url=substr(filename,8,.)
	order url, before(filename)
	drop filename

rename occcode occ2010
	label variable occ2010 "Census occ 2010 codes in text"
	run occ2010labels.do
	label values occ2010 occ2010
	* drop ambiguous and non-"job" categories:
	tab occ2010 if occ2010>=9990 & occ2010<=9999
		drop if occ2010>=9997 & occ2010<=9999

rename nocc mentions
	label variable mentions "# mentions of Census occ in text"
	tab mentions

rename nplurals plurals
	label variable plurals "# plurals per Census occ in text"
	tab plurals

rename occlabel occ2010label
	label variable occ2010label "occ2010 short label"

sort url occ2010

label data "OscarsCensus: occ2010(+) level results from Wikipedia movie plots, synopses, & summaries"
	save OscarsCensus.dta, replace
	describe
	summarize, sep(0)
	list in 1/20, sepby(url) str(20)

* collapse to movie level counts:
gen omentions= mentions if occ2010>0 & occ2010<9780
	label variable omentions "# mentions of any occupation"
	summarize omentions if omentions>=1, detail

* create working class counts:
gen owkocc= 0 if omentions>0
	replace owkocc= mentions if occ2010>=3300 & occ2010<=3690 /* medical technicians */
	replace owkocc= mentions if occ2010>=3740 & occ2010<=4760 /* police, security, retail sales  */
	replace owkocc= mentions if occ2010>=4940 & occ2010<=9759 /* other lower white collar & blue collar */

	label variable owkocc "working class occs mentions"
	summarize owkocc, detail

sort url mentions occ2010

collapse (sum) mentions plurals omentions owkocc (last) occ2010, by(url)
	describe
	summarize, sep(0)

label variable mentions 	"# mentions of any code"
label variable omentions	"# mentions of any occupation code"
label variable owkocc   	"# mentions of a working class occupation code"

label variable occ2010 "most mentioned occ"
	run occ2010labels.do
	label values occ2010 occ2010
	tab occ2010, missing

gen pwkocc= owkocc / omentions
	label variable pwkocc "% of occupation mentions that are working class"
	format pwkocc %8.3f
	summarize pwkocc, detail

sort url

label data "OscarsCounts: Oscars movie-level # mentions of broad occ categories"
save OscarsCounts.dta, replace
	describe
	summarize, sep(0)

* read in movie-level files:
*	first, counts of words etc. output from jobs.py
insheet using OscarsTexts.xls,clear
	describe
	summarize, sep(0)

*drop the directory ("movies/") prefix:
gen str url=substr(filename,8,.)
	order url, before(filename)
	drop filename

	sort url
	save temptexts.dta, replace

* then list of year released and titles
insheet using Oscarstitles.xls,clear
	describe
	summarize, sep(0)
	sort url

merge 1:1 url using temptexts.dta, gen(_mtexts)
	describe, short

merge 1:1 url using OscarsCounts.dta, gen(_mcounts)
	label data "OscarsCounts: Oscars movie-level # mentions of broad occ categories"
	save OscarsCounts.dta, replace
	describe
	summarize, sep(0)

gen int decade=10*floor(year/10)

recode owkocc (0/2=0) (3/max=1), gen(y3owkocc)
 	label variable y3owkocc "Three+ mentions of working class occupations"
 	label define y3 0 "0-2 mentions 0" 1 "3+ mentions 3"
	label values y3owkocc y3
	tab y3owkocc, missing

tab decade y3owkocc,row 
sort year 
list year title owkocc omentions pwkocc if owkocc>=3, sepby(decade)

* end of Oscars.do
log close
exit

