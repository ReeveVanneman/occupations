# jobs.py
#	version 0.2.1
#		revision: adds disambiguation of capitalized/ non-capitalized titles (e.g., President, president)
#		titles to be disambiguated now have negative values in jobs.json (e.g., "president": -12, )
#	reads a series of text files and identifies and codes all words, bigrams, and trigrams that are "job" (or other position) titles
#		codes these ~30,000 "jobtitles" into 2010 3-digit U.S. Census codes 
#		several added codes for "jobtitles" that are not employment Census occupations
#			(e.g., wife, criminal, miiitary, France)
#			these text titles are coded into new (non-Census) codes
#			also, some Census codes are subdivided: e.g., (CEOs: govt & pvt; 
#
#	arg= prefix is a filename prefix to output (& input) files
#		e.g. python3 jobs.py NYT
#
#	input:
#		prefix+files.txt (e.g., NYTfiles.txt)= a file of filenames of text files to be read and coded.
#			this is the only input file created for each execution of jobs.py
#			the other three files below are fixed inputs to jobs.py
#		jobs.json = a json file of "job" titles and Census 2010 codes
#			this file can always be improved and updated.
#				esp. jobtitles based on a 2016 Census coding list that often had multiple Census codes, only one of which could be used.
#			the jobs.py program divides jobs.json into three Python dicts: 1-word, 2-word, and 3-word "job" titles.
#			3-word phrase from text are checked first if it matches a 3-word titles (abc), 
#				then 2-word bigram are formed from those 3 words (ab, ac) and checked against jobs.json, 
#				then the first word of the 3 is checked against one word titles from jobs.json (a).
#				if no match, the program moves on to next 3-word phrase (bcd).
#				texts are checked only within a sentence (i.e., abc never spans two sentences)
#		occs2010.json = a json file of (the somewhat expanded) Census 2010 codes and their titles.
#		nosingularize.txt = a file of words (jobtitles) that should not be singularized in the texts
#			but would be incorrectly singularized by inflect.singnoun (e.g., boss, waitress)
#			or are in the plural in jobs.json: bahamas, data, physics
#		two lists initialized below in the program, but probably would be more flexible as external files:
#			1 file of words that are coded as jobs only if lower case (e.g., potter)
#			1 file of words that are coded as jobs only if upper case (e.g., General)
#
#	to compile jobs.py:
#		uses python standard packages: re json sys
#		uses python packages that must be downloaded and installed: nltk inflect BeautifulSoup
#
# todo (maybe):
#	optimize; python program was written to get the work done, not optimized
#	is there  a better program to singularize words than inflect.
#		work around now identifies ~200  words that should not be singularized, e.g., boss, bus
#			and changes the inflect default using the inflect routine defnoun
#	punctuation: 
#		' :	's is now a separate word (e.g., Harper's agent-> " 's agent" = 500, performer's agent)
#			s' ???
#			n't should be replaced with " not"
#	how to handle text files with non-ASCII character codes
#	identify (& drop?) headings for newspapers (multiplies "writer" etc.)?
#		do not code lines: BYLINE
#	expand the industrial sector jobtitles/ codes
#		expand the government code to specific government agencies
#	edit the ridiculously long military jobtitles in jobs.json
#	disambiguation:
#		ambiguities, more than one possible code, mostly  coded into 9998 : 
#			band, crew, driver, Georgia, intern, officer, page, partner, team,
#		ambiguities, coded into most common code::
#			broker (4920= real estate broker, not 4820 investment broker )
#			cast (2700= actors, not to cast aspersions etc.)
#			collector (2400= archivists)
#			critic (2005= experts, advisors, not journalist)
#			dishwasher (16101, the appliance, not the restaurant worker, 4140; but "dish washer"= 4140)
#			gardeners (4250= a landscape worker, not the home gardener)
#			General (9800= military officer, not in general))
#			Indian (13356= country; not Native American Indian)
#			king (33= monarch; not chess piece or playing card)
#			minister (2040= clergy; not government minister)
#			painter (2600= artist; not construction worker)
#			queen (33= monarch; not chess piece or playing card or Queen Anne furniture)
#			producer (2710= producers and directors; not a producer of x, coal producer)_
#			sailor (9300= hired seaman, not a sailboat sailor; nor a US Navy sailor)
#			scout (9812= military, rank ns: not to scout, not baseball scout)
#			sitter (4600= baby sitter, child care worker is most common but also =4900, artists/photographer sitter, or chair sitter, fence sitter)
#			stringer (2610= reporter, news stringer; not factory stringer)
#		ambiguities, coded into less specific, overall code:
#			director (3280= professional managerial, nec)
#		ambiguities, coded into 3288= larger prof/mgr code that captures only one meaning
#			associate (3288= likely prof/mgr, not ..associates with..)
#			aide, associate, backer, owner, staff, staff member
#		some jobs only if the word is a noun: command, guide
#		should some plurals be recognized as a separate code?  eg. spouses=couple spouse=individual
#			and some plurals should not be coded: counts, royalties
#			some words would specify jobs/positions mainly in the plural: academics
#		President(=12, usually US President) vs president(=10, chief executive) depends on correct capitalization
#		all caps words have been changed to titles (e.g. COOPER = Cooper)
#

import re
import json
import sys

# there should be one and only one argument in calling Python
Nargs= len(sys.argv)
if Nargs<2:
	print("You need to call jobs.py with an argument giving the filename prefix")
	print("	e.g., python3 jobs.py movies")
	print("	exiting...")
	sys.exit()
else:
	prefix= sys.argv[1]
	print("prefix: ", prefix)

# inflect will singularize words in text
#	it's not very good and requires several fixes.
import inflect
inf=inflect.engine()

# to strip html code from text:
from bs4 import BeautifulSoup

# to split text file into sentences
import nltk
from nltk import sent_tokenize, word_tokenize

# read file of words that are incorrecctly singularized by inflect.singular_noun
#	e.g., waitress, boss, chorus, police
#	also includes words that will not be singularized which are titles mainly when plural (e.g., sales)
dontsing= open("nosingularize.txt").read()
# dontsing is a long string with many end of line characters:
dontsing=dontsing.split('\n')
# number of 1-word lower case jobtitles not to be singularized:
Ndontsing=len(dontsing)
# strip off end of file line:
dontsing=dontsing[0:Ndontsing-1]
print ('dontsing (jobtitles not singularized)= ' + str(type(dontsing)) + ' Nlines=' + str(len(dontsing)))
#
# contractions to be expanded (easier just to expand all "n\'t" to " not"; misses ain't, can't, shan't, won't, only can't and won't deserve separate replaces.
#notwords= [ 'ain\'t', 'aren\'t', 'can\'t', 'couldn\'t', 'didn\'t', 'doesn\'t', 'don\'t', 'hadn\'t', 'hasn\'t', 'haven\'t', 'isn\'t', 'mustn\'t', 'needn\'t', 'oughtn\'t', 'shan\'t', 'shouldn\'t', 'wasn\'t', 'weren\'t', 'won\'t', 'wouldn\'t' ]
#
# words that change meaning when capitalized or lower case:
#	someday these might be external files, easier to maintain
notUpper= ['archer', 'associate', 'baker', 'barber', 'barker', 'beller', 'boilermaker', 'bowman', 'brewer', 'butler', 'carman', 'carpenter', 'carney', 'carver', 'celebrity', 'cook', 'cooper', 'coopersmith', 'courier', 'cowboy', 'craftsman', 'diver', 'draper', 'driver', 'dyer', 'fletcher', 'foreman', 'frazer', 'gilder', 'glazer', 'goldsmith', 'hammersmith', 'hooker', 'hooper', 'houseman', 'hunter', 'jackman', 'knight', 'linderman', 'lumper', 'mailer', 'mariner', 'mason', 'miller', 'moulder', 'oiler', 'packer', 'pinker', 'pirate', 'pitman', 'porter', 'potter', 'presser', 'ranger', 'rich', 'road warrior', 'roper', 'sander', 'sawyer', 'sexton', 'shearer', 'shepherd', 'shoemaker', 'silversmith', 'singer', 'skinner', 'slater', 'smith', 'spanner', 'steeler', 'stockman', 'stoker', 'striker', 'stringer', 'tanner', 'teller', 'tribune', 'turner', 'wagoner', 'warrior', 'wasp', 'waterman', 'weaver', 'webber', 'wheeler', 'whellwright', 'whistler', 'white' ]
notLower= ['count', 'general', 'justice', 'major', 'marine', 'polish', 'pvt' ]
# these are jobtitles when allcaps but something else if not all caps:
#	IT DO were dropped because found so often in all-cap title meaning "it" not "information technology"
allUpper= ['da', 'coo', 'st', 'us']
#allUpper= ['DA', 'COO', 'ST', 'US']

####################################
# readfile of occupation (& other) titles (mostly from US Census):
occs2010= open("occs2010.json").read()
# occs2010 is a long string, make occs2010 into a dict, censuslabels:
censuslabels= json.loads(occs2010)
print  ('\ncensuslabels (occs 2010 titles from Census+)= ' + str(type(censuslabels)) + ' Nlines=' + str(len(censuslabels)) )
#
# readfile of job titles (mostly from US Census):
jobs= open("jobs.json").read()
# jobs is a long string, make jobs into a dict, joblabels:
joblabels= json.loads(jobs)
print  ('\njoblabels (jobtitles mostly from Census+)= ' + str(type(joblabels)) + ' Nlines=' + str(len(joblabels)) )
# separate jobs.json into 3 dicts (1-word, 2-word, or 3-word jobtitles) for testing texts:
jobs1= {}
jobs2= {}
jobs3= {}
for job in joblabels:
	Nwords= len(job.split())
	if Nwords==1:
		jobs1[job]=joblabels[job]
	elif Nwords==2:
		jobs2[job]=joblabels[job]
	elif Nwords==3:
		jobs3[job]=joblabels[job]
print ('	jobs1 (one-word jobtitles from Census)= ' + str(type(jobs1)) + ' Nlines=' + str(len(jobs1)))
print ('	jobs2 (two-word jobtitles from Census)= ' + str(type(jobs2)) + ' Nlines=' + str(len(jobs2)))
print ('	jobs3 (three-word jobtitles from Census)= ' + str(type(jobs3)) + ' Nlines=' + str(len(jobs3)))

# store (disambiguated) census code for each joblabel found across all texts:
jobscensus= {}

####################################
# output files:
#	do we really need all these outputs?
#	maybe drop the jobfile?
#
# main output: after processing each text file, writes one record for each occ2010 found, regardless of "job" title
#	blank line at beginning of each text
#	writes as tab delimited file for input into spreadsheet/ stats program
censusfile= prefix + "Census.xls"	
censusf= open(censusfile, "w")
censusf.write ("filename" + "	" + "OccCode" + "	" + "Nocc" + "	" + "Nplurals" + "	" + "Occlabel" + "\n" )
#
# after processing each text, writes a count of #words, #sentences, etc., one line per text
textsfile= prefix + "Texts.xls"	
textsf= open(textsfile, "w")
textsf.write ("filename	Ntitles	Nmentions	Npara	Nsentences	Nwords	Nbytes")
#
# writes key-word-in-context file: a sentence for every "job" title found in the text
#	useful for checking code accuracy
#	also can be input to subsequent program to analyze sentiment or other characteristics about the "occ"
#	if a sentence has more than one "job" title, the kwic sentence is written for each "job" title
kwicfile= prefix + "kwic.txt" 
kwic= open(kwicfile, "w")
#
# after processing all texts, writes totals for each occ2010 and the jobs found in that occ2010
totalsfile= prefix + "Totals.txt"	
totalsf= open(totalsfile, "w")
totalsf.write ("\n    	N	 Plurals	Ntexts	code	jobtitle")
#
# after processing each text, writes a line for every "job" title found; probably unnecessary output file
jobfile= prefix + "Jobs.txt"	
jobsf= open(jobfile, "w")

####################################
# read list of filenames of input texts such as files with movie plots, newspaper articles, other texts...
infilelist= prefix + "files.txt"
files=open(infilelist).read()
# files is a long string with all file names:
# number of files:
textfiles=files.split('\n')
Ntextfiles=len(textfiles)
# strip off end of file line:
textfiles=textfiles[0:Ntextfiles-1]
print ('\nList of text files to be analyzed: ' + infilelist + " " + str(type(textfiles)) + ", #files= " + str(len(textfiles)) + '\n')

Sumtitles=0
Sumpara=0
Sumsentences=0
Sumwords=0
Sumcensuscounts= {}
Sumcensusplurals= {}
Ntextscensus= {}
Sumjobcounts= {}
Sumjobplurals= {}
Ntextsjob= {}

for file in textfiles:
	# write text file name to ...Census.txt file:
	#censusf.write ("\n" + file + ":\n" )
	jobsf.write ("\n" + file + ":\n" )
	kwic.write ("\n" + file + ":\n" )
	# write blank line to ...census.txt file:
	censusf.write ("\n")
	foundjobs= []
	Nfound= [0]
	Nplural= [0]
	jcensus= [0]
	ijob=0
	# todo: work with different codings
	text0=open(file, encoding = "ISO-8859-1").read()
	# drop html:
	text1= BeautifulSoup(text0, features="html.parser")
	textstring= text1.get_text()
	Nbytes=len(textstring)
	#print ("\n" + file + ":\n" + str(textstring))
	#Nwords=textstring.count(" ")
	#print ("\n" + file + ":\n" + str(textstring) + "\nNwords= " + str(Nwords))
	#
	# add end of paragraph marker (2 end of lines together) because the sentence tokenizer will ignore paragraphing:
	textstring=re.sub(r'(\w)\n\n', r'\1.\nThis is an EOP.\n', textstring)
	textstring=re.sub(r'(\W)\n\n', r'\1\nThis is an EOP.\n', textstring)
	#
	# sentencing:
	#	drop newlines to make one long text:
	textstring=textstring.replace('\n', ' ')
	#
	# 9 Aug 2018: delete hyphens
	#	hyphens are probably meaningless only grammatical distinctions between e.g., working-class and working class
	#	also will match 3-word hypthenated phrases that get lost when making hyphen a separate word (e.g., child - care aide)
	textstring=textstring.replace('-',' ')
	#	but a couple of exceptions:
	textstring=textstring.replace('x ray','x-ray')
	textstring=textstring.replace('pre k','pre-k')
	#textstring=textstring.replace('teen ager','teen-ager')
	#
	# the following abbreviations cause the sentence tokenizer to split the sentence incorrectly & are part of jobs.json
	textstring=textstring.replace('Assn.', 'Association')
	textstring=textstring.replace('Capt.', 'Captain')
	textstring=textstring.replace('C.I.A.', 'CIA')
	textstring=textstring.replace('Comdr.', 'Commander')
	textstring=textstring.replace('Cpl.', 'Corporal')
	textstring=textstring.replace('D.A..', 'DA')
	textstring=textstring.replace('Dem.', 'Democrat')
	textstring=textstring.replace('Dept.', 'Department')
	textstring=textstring.replace('dept.', 'department')
	textstring=textstring.replace('F.B.I.', 'FBI')
	textstring=textstring.replace('Gov.', 'Governor')
	textstring=textstring.replace('K.G.B.', 'KGB')
	textstring=textstring.replace('J.D.', 'JD')
	textstring=textstring.replace('Lieut.', 'Lt')
	textstring=textstring.replace('M.D.', 'MD')
	textstring=textstring.replace('Pvt.', 'Pvt')
	textstring=textstring.replace('R.N.', 'RN')
	textstring=textstring.replace('Repub.', 'Republican')
	textstring=textstring.replace('Rev.', 'Reverend')
	textstring=textstring.replace('Sgt.', 'Sergeant')
	textstring=textstring.replace('Univ.', 'University')
	textstring=textstring.replace('V.P.', 'VP')
	# the following abbreviations cause the sentence tokenizer to split the sentence incorrectly
	textstring=textstring.replace('e.g.', 'eg')
	textstring=textstring.replace('etc.', 'etc')
	textstring=textstring.replace('et al.', 'et al')
	textstring=textstring.replace('i.e.', 'ie')
	# the following abbreviations get confused with real words meaning something else:
	textstring=textstring.replace('Md.', 'Maryland')
	textstring=textstring.replace('Pa.', 'Pennsylvania')
	textstring=textstring.replace('PA.', 'Pennsylvania')
	textstring=textstring.replace('S.C..', 'South Carolina')
	textstring=textstring.replace('St.', 'Saint')
	textstring=textstring.replace('ST.', 'SAINT')
	#
	# reduce multiple blanks to a single blank
	textstring= re.sub(" +", " ", textstring)
	# but no blank at start of line:
	#textstring=textstring.replace("\n ", "\n")
	# and no tab at end of line:
	#textstring=textstring.replace("	\n", "\n")
	# and no blank at end of line:
	#textstring=textstring.replace(" \n", "\n")
	# drop indentations in NYTimes:
	textstring=textstring.replace('\xa0','')
	#
	Nwords=textstring.count(" ")
	#print ("\n" + file + ":\n" + str(textstring) + "\nNbytes=" + str(Nbytes) + " " + "Nwords= " + str(Nwords))
	#
	# make each sentence a new string
	textlines= sent_tokenize(textstring)
	#
	# process each sentence in the file:
	Npara=0
	iline=0
	for line0 in textlines:
		#print (str(line0) + "\n")
		iline=iline+1
		# drop EOP marker:
		if "This is an EOP." in line0:
			Npara=Npara+1
		line=line0.replace('This is an EOP.', '')
		# 
		# these replaces are done line by line (rather than for the whole textlines file) so that the kwic file looks more like the original
		# 
		# periods only at tend of line kept as separate word
		line=re.sub('\.$', ' \.', line)
		#	otherwise periods are abbreviations that have not caused sent_tokenize to break the line:
		#	these non-problematic abbreviations are kept in jobs.json without periods
		line=re.sub('\.', '', line)
		# EOL is just an extra "word" at the end of the line so that the last trigram includes a real word to test as the first (2nd to last) word
		line=re.sub('$', ' EOL ', line)
		line=re.sub('^ EOL $', '', line)
		# footnotes in wikipedia plot texts:
		line=line.replace('[',' [ ')
		line=line.replace(']',' ] ')
		# punctuation (except hyphens) becomes a separate word:
		line=line.replace(',', ' , ')
		#line=line.replace('.',' .')
		line=line.replace('/',' / ')
		line=line.replace('|',' | ')
		line=line.replace('?',' ?')
		line=line.replace('!',' !')
		line=line.replace(';',' ;')
		line=line.replace(':',' :')
		line=line.replace('>',' > ')
		line=line.replace('(',' ( ')
		line=line.replace(')',' ) ')
		line=line.replace('\*',' \* ')
		# replace ', 's,  and "
		line=line.replace('\"',' \" ')
		line=line.replace("\'\'",' \" ')  # some files use '' for "
		line=line.replace('\'',' \' ')		# apostrophes become separate word 
		line=line.replace(' \' s ',' \'s ')	# except apostrophe s which is its own word
		#
		# initialize in order to create tri-grams, bigrams
		wordnewU='X'
		wordlastU='X'
		word2ndlastU='X'
		wordnewS='x'
		wordlastS='x'
		word2ndlastS='x'
		plural2ndlast=0
		plurallast=0
		pluralnew=0
		wordbiU= word2ndlastU + ' ' + wordlastU 
		wordbi2U= word2ndlastU + ' ' + wordnewU 
		wordtriU= word2ndlastU + ' ' + wordlastU + ' ' + wordnewU
		# skipword is a flag to note a word has already been included in trigram, bigram
		skipword=0
		# create list of words for this line:
		linelist= line.split(' ')
		for wordnewU in linelist:
			# problems with inflect singular_noun:
			#	inflect.singular_noun wrongly singularizes many words, esp those ending in "ss", e.g, waitress, class,
			#		so, jobs.py needs 200+ lines of code (defnoun) above to fix those mistakes
			#	IT = (Information Technology) but also = it which is the singular of they,them, etc. 
			#		& so gets coded a lot, but not filtered out by IT must be in caps; 
			#		so IT now dropped from jobs.json
			pluralnew= 1
			if wordnewU.lower() in dontsing: # wordnewU in list not to singularize
				pluralnew=0
				wordnewS= wordnewU
				#print ('Dont singularize ', wordnewU, ': ', line)
			else:
				wordnewS= inf.singular_noun(wordnewU)	# wordnewS= singular root of wordnewU (maintains case)
				if not wordnewS:  # wordnewU already singular
					pluralnew=0
					wordnewS=wordnewU
			# 
			# form trigram and bigrams with [singularized] new word
			wordtriU= word2ndlastU + ' ' + wordlastU + ' ' + wordnewU
			wordtriS= word2ndlastS + ' ' + wordlastS + ' ' + wordnewS
			wordtri= wordtriS.lower()
			#
			wordbiU= word2ndlastU + ' ' + wordlastU
			wordbiS= word2ndlastS + ' ' + wordlastS
			wordbi=  wordbiS.lower()
			#
			wordbi2U= word2ndlastU + ' ' + wordnewU
			wordbi2S= word2ndlastS + ' ' + wordnewS
			wordbi2=  wordbi2S.lower()
			#
			word2ndlast= word2ndlastS.lower()
			#
			if skipword<1 and wordtri in jobs3:
				skipword= 3
				census= jobs3[wordtri]
				# check whether this job trigram has already been found for this file:
				if wordtri in foundjobs:
					# trigram has been found before in this file, so just increment count
					iword= foundjobs.index(wordtri)+1
					Nplural[iword]= Nplural[iword]+pluralnew
					Nfound[iword]= Nfound[iword]+1
				else:
					# trigram has not been found before in this file, so add to list of jobs found
					ijob=ijob+1
					iword= ijob
					Nfound.append(1)
					Nplural.append(pluralnew)
					jcensus.append(census)
					foundjobs.append(wordtri)
				# print this job trigram (whether new or not)
				#	prints line close to the original format (line0) , before most replacements (line).
				kwic.write (file + "	" + str(iline) + "	" + str(iword) + "	3	" + str(census) + " " + wordtriU + "	" + line0 + "\n")
			#
			# next, check if first 2 words of trigram == any bigram job titles
				# only check if wordbi has not been part of an earlier trigram
			elif skipword<1 and wordbi in jobs2:
				skipword=2
				census= jobs2[wordbi]
				# check whether this job bigram has already been found for this file:
				if wordbi in foundjobs:
					# bigram has been found before in this file, so just increment count
					iword= foundjobs.index(wordbi)+1
					Nplural[iword]= Nplural[iword]+plurallast
					Nfound[iword]= Nfound[iword]+1
				else:
					# bigram has not been found before in this file, so add to list of jobs found
					ijob=ijob+1
					iword= ijob
					Nfound.append(1)
					Nplural.append(plurallast)
					jcensus.append(census)
					foundjobs.append(wordbi)
				# print this job bigram (whether new or not)
				kwic.write (file + "	" + str(iline) + "	" + str(iword) + "	2	" + str(census) + " " + wordbiU + "	" + line0 + "\n")
			#
			# next, check if first & 3rd words of trigram == any bigram job titles
				# only check if wordbi2 has not been part of an earlier trigram
			elif skipword<1 and wordbi2 in jobs2:
				skipword=3
				census= jobs2[wordbi2]
				# check whether this job bigram has already been found for this file:
				if wordbi2 in foundjobs:
					# bigram has been found before in this file, so just increment count
					iword= foundjobs.index(wordbi2)+1
					Nplural[iword]= Nplural[iword]+plurallast
					Nfound[iword]= Nfound[iword]+1
				else:
					# bigram has not been found before in this file, so add to list of jobs found
					ijob=ijob+1
					iword= ijob
					Nfound.append(1)
					Nplural.append(plurallast)
					jcensus.append(census)
					foundjobs.append(wordbi2)
				# print this job bigram (whether new or not)
				kwic.write (file + "	" + str(iline) + "	" + str(iword) + "	2	" + str(census) + " " + wordbi2U + "	" + line0 + "\n")
			#
			# finally, check if first word of trigram == any unigram job title
				# if trigram and bigram are	not a job title, check whether the first word in the trigram is a job:
				#	(2nd word will become first word in next bigram & will be checked then)
				#	except if 1st word has been part of the previous trigram or bigram (skipword>=1)
			elif skipword<1 and word2ndlast in jobs1:
				skipword==1
				census= jobs1[word2ndlast]    # word2ndlast is sigularized and lower case
				# 
				# census code <0 => word2ndlast is ambiguous but can be disambiguated based on capitalization:
				if census<0:
					census=-census			# default code is the negative of what is stored
					# separate entries for upper case / lower case titles in foundjobs:
					#	default jobtitle in foundjobs is capitalized (title)
					#word2ndlast= word2ndlast.title()
					#  do this when first seen as wordnew?
					if word2ndlastS.isupper():   # all upper case is usually an article title; translate to proper name titled
						# a couple of exceptions: DA, COO, etc.:
						if word2ndlast not in allUpper: # for these special all uppercase jobs (DA etc.) keep as upper case
						# otherwise translate to proper name as best guess:
							word2ndlastS= word2ndlastS.title()
					if word2ndlast in notLower: # e.g., general, lower case
						if word2ndlastS.islower():
							census= 9998
						else:
							#census=census	
							word2ndlast= word2ndlast.title()
					elif word2ndlast in notUpper: # e.g., Potter, capitalized
						if word2ndlastS.islower():
							#census=census	# (default code -- the negative of what is stored in jobs.json)
							word2ndlast= word2ndlastS.lower()  # redundant, kept only for code symmetry
						else:
							census= 9998
							word2ndlast= word2ndlast.title()  # change to capitalized
					elif word2ndlast in allUpper:
						if word2ndlastS.isupper():
							#census=census	# (default code -- the negative of what is stored in jobs.json)
							word2ndlast= word2ndlast.upper()
						else:
							census= 9998
							#word2ndlast= word2ndlast.lower()
					elif census==12:  # president=10 / President=12
						if word2ndlastS.islower():
							census=10
							#word2ndlast= word2ndlastS.lower()
						else:
							#census= 12
							word2ndlast= word2ndlast.title()  # change to capitalized ("President")
					elif census==30: # representative(s)=3288 / Representative=30
						if word2ndlastS.islower():
							census=3288
							#word2ndlast= word2ndlastS.lower()
						else:
							#census= 30
							word2ndlast= word2ndlast.title()  # change to capitalized ("Representative")
					elif census==35: # secretary(s)=5700 / (Cabinet) Secretary=35
						if word2ndlastS.islower():
							census=5700
							#word2ndlast= word2ndlastS.lower()
						else:
							#census= 35
							word2ndlast= word2ndlast.title()  # change to capitalized ("Secretary")
					elif census==33 and (word2ndlastU=="Queens" or word2ndlastU=="QUEENS"): # probably borough of Queens
						census= 9998
						word2ndlast= "Queens"
					elif census==33 and (word2ndlastU=="Kings" or word2ndlastU=="KINGS"): # probably not multiple kings if capitalized
						census= 9998
						word2ndlast= "Kings"
				# either jobtitle not ambiguous (census>0) or after disambiguation:
				#	then check whether this single-word job has already been found for this file:
				if word2ndlast in foundjobs:
					# word2ndlast has been found before in this file, so just increment count:
					iword= foundjobs.index(word2ndlast)+1
					Nfound[iword]= Nfound[iword]+1
					Nplural[iword]= Nplural[iword]+plural2ndlast
				else:
					# word has not been found before in this file, so add to list of jobs found
					ijob=ijob+1
					iword= ijob
					Nfound.append(1)
					Nplural.append(plural2ndlast)
					jcensus.append(census)
					foundjobs.append(word2ndlast)  # word2ndlast has been disambiguated according to capitalization
				# print this line (whether job is new or not)
				kwic.write (file + "	" + str(iline) + "	" + str(iword) + "	1	" + str(census) + " " + word2ndlastU + '	' + line0 + "\n")
			# reset 1st and 2nd words in trigram:
			word2ndlastU=wordlastU
			word2ndlastS=wordlastS
			plural2ndlast=plurallast
			wordlastU=wordnewU
			wordlastS=wordnewS
			plurallast=pluralnew
			if skipword>0:
				skipword= skipword-1
	# 
	# print results of this file:
	# number of sentences:
	Ntitles=len(Nfound)-1
	Nmentions= sum(Nfound)
	Nsentences=len(textlines) - Npara
	#Nwords= Nwords+Nsentences-Npara
	#Nwords= Nwords+Nsentences
	Nwords= Nwords - 4*Npara
	#Nsentences=Nsentences-1
	Npara=Npara
	print (file + "	#jobtitles=" + str(Ntitles) + " #mentions=" + str(Nmentions) + "	# paragraphs=" + str(Npara) + 	"	#sentences=" + str(Nsentences) + "	#words=" + str(Nwords) )
	textsf.write ("\n" + file + "	" + str(Ntitles) + "	" + str(Nmentions) + "	" + str(Npara) + "	" + str(Nsentences) + "	" + str(Nwords) + "	" + str(Nbytes) )
	#
	# accumulate totals across files:
	Sumtitles= Sumtitles+Ntitles
	Sumpara= Sumpara+Npara
	Sumsentences= Sumsentences+Nsentences
	Sumwords= Sumwords+Nwords
	ijob=0
	censuscounts={}  	#	#mentions of this census code in this text file
	censusplurals={}	#	#plurals of this census code in this text file
	for job in sorted(foundjobs):	# list job titles alphabetically
		ijob=foundjobs.index(job)+1
		# write to text file X job title output:
		#	tabs make this easy to import into stata, excel:
		jobsf.write (file + '	' + str(ijob) + '	#mentions=	' + str(Nfound[ijob]) + '	#plurals=	' + str(Nplural[ijob]) + "	census=	" + str(jcensus[ijob]) + '	' + job + "\n")
		# accumulate totals by job title across text files:
		if job in Sumjobcounts:
			Sumjobcounts[job]= Sumjobcounts[job] + Nfound[ijob]
			Sumjobplurals[job]= Sumjobplurals[job] + Nplural[ijob]
			Ntextsjob[job]= Ntextsjob[job] + 1
		else:
			Sumjobcounts[job]= Nfound[ijob]
			Sumjobplurals[job]= Nplural[ijob]
			Ntextsjob[job]= 1
			jobscensus[job]= jcensus[ijob]  # store disambiguated census code for this job ngram
		# accumulate totals by census code across job titles for this text file:
		if jcensus[ijob] in censuscounts:
			censuscounts[jcensus[ijob]] = censuscounts[jcensus[ijob]] + Nfound[ijob]
			censusplurals[jcensus[ijob]] = censusplurals[jcensus[ijob]] + Nplural[ijob]
		else:
			censuscounts[jcensus[ijob]] = Nfound[ijob]
			censusplurals[jcensus[ijob]] = Nplural[ijob]
	for code in sorted(censuscounts):
		# write text file totals to ..Census.txt file:
		censusf.write (file + "	" + str(code) + "	" + str(censuscounts[code]) + "	" + str(censusplurals[code]) + "	" + censuslabels[str(code)] + "\n" )
		# accumulate totals by census code for all files:
		if code in Sumcensuscounts:
			Sumcensuscounts[code]= Sumcensuscounts[code] + censuscounts[code]
			Sumcensusplurals[code]= Sumcensusplurals[code] + censusplurals[code]
			Ntextscensus[code]= Ntextscensus[code] + 1
		else:
			Sumcensuscounts[code]= censuscounts[code]
			Sumcensusplurals[code]= censusplurals[code]
			Ntextscensus[code]= 1

print (" ")
# end of python program; print total files processed
print ("# titles=" + str(Sumtitles) + " # files=" + str(len(textfiles)) + " # sentences=" + str(Sumsentences) + " # words=" + str(Sumwords) )
for code in sorted(Sumcensuscounts):
	totalsf.write ("\n" + str(code) + "=	" + str(Sumcensuscounts[code]) + "	" + str(Sumcensusplurals[code]) + "	" + str(Ntextscensus[code]) + "	" + censuslabels[str(code)] + "\n")
	for job in sorted(Sumjobcounts):
		if jobscensus[job]==code:
			totalsf.write ("	" + str(Sumjobcounts[job]) + "	" + str(Sumjobplurals[job]) + "	" + str(Ntextsjob[job]) + "	" + str(jobscensus[job]) + "	" + job + "\n")

