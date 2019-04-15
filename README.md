# occupations
python program and coding files to code jobs/positions in texts to numeric codes

# arg= prefix is a filename prefix to output (& input) files
#	e.g. python3 jobs.py NYT
#
# jobs.py
#	reads text files and identifies and codes all words, bigrams, and trigrams that are job (or other position) titles
#		codes job titles into 2016 4-digit U.S. Census codes 
#		several added codes for positions that are not jobs (e.g., wife, criminal, miiitary)
#			these text titles are coded into new (non-Census) codes
#	input:
#		jobs.json = a json file of job titles and Census 2010 codes
#			this file can always be improved and updated.
#				esp. jobs from 2016 Census list which often had multiple Census codes, only one of which was used.
#			jobs.py divides jobs.json into three Python dicts: 1-word, 2-word, and 3-word job titles.
#			3-word phrase is taken from text and checked first if it matches a 3-word titles (abc), then 2-word (ab, ac), then 1-word (a).
#				if no match, the program moves on to next 3-word phrase (bcd).
#				texts are checked only within a sentence (i.e., abc never spans two sentences)
#		occs2010.json = a json file of Census 2010 codes and their titles.
#   abbreviations.json = a json file of abbreviations that will be stripped of periods 
#     abbreviations (e.g., Dr.) with periods confuse the ntlk program to divide the text into sentences
#     so jobs.py first strips these abbreviations of the periods and then divides the text into one sentence per line
#		nosingularize.txt = a file of words (jobtitles) that should not be singularized in the texts
#			but would be incorrectly singularized by inflect.singnoun (e.g., boss, waitress)
#		prefix+files.txt (e.g., NYTfiles.txt)= a file of filenames of text files to be coded.
#		two lists initialized below in the program, but probably would be more flexible as external files:
#			1 file of words that are coded as jobs only if lower case (e.g., potter)
#			1 file of words that are coded as jobs only if upper case (e.g., general)
#		uses python standard packages: re json sys
#		uses python packages that must be downloaded and installed: nltk inflect BeautifulSoup
#
# todo (maybe):
#	need a better program to singularize words than inflect.
#		work around now identifies ~200  words that should not be singularized, e.g., boss, bus
#	punctuation: 
#		' :	's is now a separate word (e.g., Harper's agent-> " 's agent" = 500, performer's agent)
#			s' ???
#			n't should be replaced with " not"
#	how to handle text files with non-ASCII character codes
#	analyze headings for newspapers (multiplies "writer" etc.)?
#		do not code lines: BYLINE
#	disambiguation:
#		ambiguities, more than one possible code, mostly  coded into 9998 : 
#			band, crew, driver, intern, officer, page, partner, team,
#		ambiguities, coded into most common code::
#			cast (2700= actors, not to cast aspersions etc.)
#			critic (2005= experts, advisors, not journalist)
#			General (9800= military officer, not in general))
#			minister (2040= clergy; not government minister)
#			painter (2600= artist; not construction worker)
#			producer (2710= producers and directors; not a producer of x, coal producer)_
#			scout (9812= military, rank ns: not to scout, not baseball scout)
#		ambiguities, coded into less specific, overall code:
#			director (3280= professional managerial, nec)
#		ambiguities, coded into 3288= larger prof/mgr code that captures only one meaning
#			aide, backer, owner, staff, staff member
#		some jobs only if the word is a noun: command, guide
#		should some plurals be recognized as a separate code?  eg. spouses=couple spouse=individual
#			and some plurals should not be coded: counts, royalties, Queens
#			some words would specify jobs/positions only in the plural: academics
#		should some capitalized be separate code?  
#			e.g., President = 15 (usually US President); presdient=10 (chief executive)
#		all caps words: mess up the check for proper names (e.g., COOPER=Cooper, POTTER=Potter)
#
