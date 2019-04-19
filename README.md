# jobs.py  
a python3 program to read a series of text files and code all words, bigrams, and trigrams that are "job" (or other position) titles.
jobs.py codes these ~30,000 "jobtitles" into 4-digit U.S. Census 2010 codes.

Several "jobtitles" that are not employment Census jobs have been added with new (non-Census codes)
(e.g., wife-> 10312, criminal-> 9850, miiitary-> 9812)
These additions expand the codes to 5-digits)
Also, some Census codes are subdivided: e.g., (CEOs: government-> 35;  waitress-> 4111)

## arguments  
jobs.py is called with one argument, a prefix for input and output files.
e.g. python3 jobs.py NYT

## compiling jobs.py:  
jobs.py uses python standard packages: re json sys  
jobs.py also uses python packages that must be downloaded and installed: nltk inflect BeautifulSoup

## input files:  
- jobs.json  
= a json file of "job" titles and Census 2010 codes.  
This file can always be improved and updated.
The main source was a 2016 Census coding list, The Alphabetical Indexes of Industries and Occupations, ( https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/occupation-index-september-2016.xlsx ).
This listing often provided multiple Census codes for a single job title, only one of which could be used in jobs.json.
So, the Census codes in jobs.json are often a compromise, or worse, misleading and need correction.  

    The jobs.py program divides jobs.json into three Python dicts: 1-word, 2-word, and 3-word "jobtitles"  
jobs.py works backwards from many text mining programs;
instead of searching a text for a word or phrase,
it searches the list of jobtitles for words and phrases from the text.
A 3-word phrase from a text is checked first if it matches a 3-word jobtitle(abc);
then two 2-word bigrams are formed from those 3 words (ab, ac) and checked against jobs.json;
then the first word of the 3 is checked against one word titles from jobs.json (a).
if no match is found to a jobs.json title from these 4 searches, the program moves on to next 3-word phrase (bcd).
Text phrases are checked only within a sentence (i.e., abc never spans two sentences)

- occs2010.json   
= a json file of (the somewhat expanded) Census 2010 codes and their titles.

- nosingularize.txt   
= a file of words (jobtitles) that should not be singularized by jobs.py.
All "jobtitles" in jobs.json are listed in the singular.
So, jobs.py singularizes words in the text before matching them to the list of job titles.
The program keeps a separate count of plurals (since they are often more culturally meaningful).
Currently, jobs.py uses a routine from the python package inflect to singularize plural nouns.
But inflect will alter many singular nouns (e.g., boss, waitress) and thus not match correctly to jobs.json. 
The current work around (nosingular.txt) identifies ~200  words that should not be singularized by jobs.py.

- abbreviations.json   
= abbreviations whose periods would confuse the sentencing algorithm.
(e.g., U.S.A. is replaced with USA)

- prefix+files.txt (e.g., NYTfiles.txt)  
= a file of filenames of text files to be read and coded.
These are local file names (which can include absolute or relative addresses) that jobs.py loops through searching for jobtitles.
In practice, output files will be more compact if the text files are in the same directory as jobs.py.

- notupper, mustbeupper  
notupper= text words that are coded as jobs only if they are all lower case (e.g., potter)  
mustbeupper= words that are coded as jobs only if the first letter is upper case (e.g., General)  
These are now two python lists initialized in jobs.py, but they would probably be more flexible if maintained as external files.

## output files:  
( "XX" below is the prefix arg, e.g., NYT )

- main output: XXcensus.xls  
After processing each text file, writes one record for each occ2010 code found, regardless of "jobtitle"

- text file descriptions: XXtexts.xls  
after processing each text, writes a count of #words, #sentences, etc., one line per text

- key-word-in-context file: XXkwic.txt  
A sentence for every "jobtitle" found in the text
This is useful for checking coding accuracy.
It also might be input to subsequent program to analyze sentiment or other characteristics about the coded "occ".
if a sentence has more than one "jobtitle", a separate line is written for each "jobtitle".

- summary stats: XXtotals.txt  
After processing all text files, jobs.py writes total counts for each occ2010 code and the jobtitles found within each code.

- ~~dropped: jobs.txt~~
~~After processing each text file, writes a line for each "jobtitle" found~~

## todo (maybe):

- singularizing text words:  
Find a better package than inflect?

- punctuation:  
Possessive 's now becomes a separate word.  That helps for some codings;
e.g., Harper's agent -> Harper 's agent" (= 500, performer's agent)
Plural possessives, s' , become s '  ; i.e., apostrophe is treated as a separate word.  OK?
And n't should be replaced with " not".

- non-ASCII character codes:  
Text files with non-ASCII character codes are not handled well now.

- headings e.g., for newspapers  
Some heading lines probably should not be coded. 
For example, BYLINE in newspaper text files will end up multiplying counts for "writer".

- disambiguation issues:  
    -  Several jobtitles are now coded into 9998, indicating they could be more than one possible code.
e.g., band, crew, driver, intern, officer, page, partner, team,
    -  Other jobtitles are coded into the most common code, but might be further disambiguated.  
cast (2700= actors, not to cast aspersions etc.)  
critic (2005= experts, advisors, not journalist)  
General (9800= military officer, not in general))  
minister (2040= clergy; not government minister)  
painter (2600= artist; not construction worker)  
producer (2710= producers and directors; not a producer of x, coal producer)  
scout (9812= military, rank ns: not to scout, not baseball scout)  
    -  coded into less specific, overall code:  
director (3280= professional managerial, nec, for both movie director and Center director)
    -  coded into 3288= larger prof/mgr code that captures only one meaning
aide, backer, owner, staff, staff member
    -  POS (part of speech)   
Some words are jobtitles only if the word is a noun: command, guide  
    - plurals  
Some plurals could be a different code than their singular forms eg. spouses=couple spouse=individual.
Some plurals should not be coded: counts, royalties, Queens
Some words would specify jobtitles only in the plural: academics
    - capitalization  
Should some capitalized be separate code?
e.g., President = 15 (usually US President); presdient=10 (chief executive)  
All caps words confuse the check for proper names (e.g., COOPER=Cooper, POTTER=Potter)  
