# jobs.py: A Python Program to Code Occupations in Text Files

## version
This is beta version 0.2.6  
  renumbers non-Census occs to a more rational order.
  Adds disambiguation of capitalized/ non-capitalized titles (e.g., President, president)  
  The list of "jobtitles" (jobs.json) is constantly being updated and expanded so the last digit ("patches") will change often.

## suggested citation:
Vanneman, Reeve. 2019.  "jobs.py: A Python Program to Code Occupations in Text Files." 
url: https://github.com/ReeveVanneman/occupations Version 0.2.1.

## jobs and occupations
jobs.py codes over 35,000 "jobtitles" (in jobs.json) into a 5-digit coding system (in occs2010.json) based mainly on the U.S. Census 2010 occupation codes.
While most of the jobtitles and occupation codes reflect occupations,
several "jobtitles" that are not employment Census jobs have been added with new (non-Census codes), e.g.,
- military->9800
- criminal->9850
- immigrants->15170
- Muslims->15400
- wife->16104
- France->18250
These additions expand the codes to 5-digits.  
  
Also, several Census codes are subdivided: e.g., 
- more detail on government officials and separated from non-government managers
- waiter-> 4110, waitress-> 4111.  
(see occs2010.json for a numerical listing of all "occupation" codes)

## arguments  
jobs.py is called with one argument, a prefix for input and output files.  e.g.,  
	 python3 jobs.py NYT  
would look for a file NYTfiles.txt that lists all the text filenames to be processed.
It would also produce output files with the prefix NYT (NYTCensus.xls, NYTTotals.txt, etc.)
  
## compiling jobs.py:  
jobs.py uses python standard packages: re json sys  
jobs.py also uses python packages that must be downloaded and installed: nltk inflect BeautifulSoup

## input files:  
- prefix+files.txt (e.g., NYTfiles.txt)  
= a file of filenames of text files to be read and coded.
These are local file names (which can include absolute or relative addresses) that jobs.py loops through searching for jobtitles.
In practice, output files will be more compact if the text files are in the same directory as jobs.py.  
This is the only input file created for each execution of jobs.py.
The other three files below are fixed inputs to jobs.py

- jobs.json  
= a json file of "job" titles and Census 2010 codes.  
This file can always be improved and updated.
The main source was a 2016 Census coding list, The Alphabetical Indexes of Industries and Occupations, ( https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/occupation-index-september-2016.xlsx ).
This listing often provided multiple Census codes for a single job title, only one of which could be used in jobs.json.
So, the Census codes in jobs.json are often a compromise, or worse, misleading and need correction.  
  
The jobs.py program divides jobs.json into three Python dicts: 1-word, 2-word, and 3-word "jobtitles".
jobs.py works backwards from many text mining programs;
instead of searching a text for a word or phrase,
it searches the list of jobtitles (jobs.json) for words and phrases from the text.
A 3-word phrase from a text is checked first if it matches a 3-word jobtitle(abc);
then two 2-word bigrams are formed from those 3 words (ab, ac) and checked against jobs.json;
then the first word of the 3 is checked against one word titles from jobs.json (a).
if no match is found to a jobs.json title from these 4 searches, the program moves on to next 3-word phrase (bcd).
Text phrases are checked only within a sentence (i.e., abc never spans two sentences)

- occs2010.json   
= a json file of (the somewhat expanded) Census 2010 codes and their titles.

- nosingularize.txt   
= a file of words (jobtitles) that should not be singularized by jobs.py.
Almost all "jobtitles" in jobs.json are listed in the singular.
So, jobs.py singularizes words in the text before matching them to the list of job titles.
The program keeps a separate count of plurals (since they are often more culturally meaningful).
Currently, jobs.py uses a routine from the python package inflect to singularize plural nouns.
But inflect will alter many singular nouns (e.g., boss->bos, waitress->waitres) and thus not match correctly to jobs.json. 
The current work around (nosingularize.txt) identifies ~200  words that should not be singularized by jobs.py.

## output files:  
( "XX" below is the prefix arg, e.g., NYT )

- main output: XXcensus.xls  
After processing each text file, jobs.py writes one record for each occ2010 code found in that text.
Each record gives the name of the text file, the numeric occupation code, the number of times it was matched in the text file, of these the number of times it was a plural in the text, and a label for the occupation.

- text file descriptions: XXtexts.xls  
after processing each text, writes a count of #words, #sentences, etc., one line per text

- key-word-in-context file: XXkwic.txt  
A sentence for every "jobtitle" found in the text
This is useful for checking coding accuracy.
It also might be input to subsequent program to analyze sentiment or other characteristics about the coded "occ".
If a sentence has more than one "jobtitle", a separate line is written for each "jobtitle".

- summary stats: XXtotals.txt  
After processing all text files, jobs.py writes total counts for each occ2010 code and the jobtitles found within each code.

- ~~to be dropped: jobs.txt~~
~~After processing each text file, writes a line for each "jobtitle" found~~

## an example:

- Oscarsfiles.txt lists filenames for all Academy Award winners, 1930-2018 (e.g., movies/The_Shape_of_Water)
Executing a python3 program (python3 jobs.py Oscars) with these files will produce output files:
- OscarsCensus.xls
- OscarsJobs.txt
- OscarsTexts.xls
- OscarsTotals.txt
- Oscarskwic.txt

These files can be processed by other statistical software to analyze trends, compare sources, 
investigate internal consistencies, and many other issues in cultural studies.
For example, the file Oscars.do is a stata program that uses the jobs.py output files, OscarsCensus.xls and OscarsTexts.xls
to investigate whether working-class characters have become more or less common in recent Best Picture movies 
(spoiler alert: they haven't).  The program recodes the occupations in OscarsCensus.xls into working class or not, 
aggregates the counts to a movie-level file (OscarsCounts.dta),
merges it with a file of release year,
and then tests for trends over time.

This is a simple example of the possibilities of jobs.py.  The text files in occupations/movies/ are
plot summaries from Wikipedia.  Other analyses have been based on a corpus of ~20k movie plots from Wikipedia.


## todo (maybe):

- singularizing text words:  
Find a better package than inflect?  
nosingularize.txt now has 200+ lines of titles to override the behavior of the inflect routine singular_noun

- punctuation:  
Possessive 's now becomes a separate word.  That helps for some codings;
e.g., "Harper's agent" -> "Harper 's agent" (= 500, performer's agent, not a government agent)  
But plural possessives, s' , become s '  ; i.e., apostrophe is treated as a separate word.
This might better be singularized to 's to match the above.
And contractions like n't might be replaced with " not"; or each contraction replaced separately.

- non-ASCII character codes:  
Text files with non-ASCII character codes are not handled well now.

- headings e.g., for newspapers  
Some heading lines probably should not be coded.
For example, BYLINE in newspaper text files will end up multiplying counts for "writer".

- jobtitle disambiguation issues:  
    -  Several jobtitles are now coded into 9997, indicating they could be more than one possible code;
e.g., crew, deputy, officer.

    -  Many jobtitles are now coded into 9998, indicating they are sometimes an occupation and sometimes not;
e.g., guide, host, orderly, printer.

    -  Other ambiguous jobtitles are coded into the most common code, but might be further disambiguated.  
cast (2700= actors, not to cast aspersions etc.)  
critic (2005= experts, advisors, not journalist)  
General (9800= military officer, not in general, not General Foods)  
minister (2040= clergy; not government minister, but specific government ministers such as "foreign minister" =31, legislative leader)  
painter (2600= artist; not construction worker)  
producer (2710= producers and directors; not a producer of x, coal producer)  
rebel (9813= rebel military, rank ns; not the broader meaning of a "rebellious" person, nor "Old Miss Rebels"))
scout (9812= military, rank ns: not to scout, not baseball scout)  

    -  some ambiguous jobtitles are coded into a broad, overall occupation code that captures multiple occupations:  
director (3280= professional managerial, nec, for both movie director and Center director)  
    -  other somewhat ambiguous jobtitles are coded into 3288= likely prof/mgr code, that captures only one meaning but might not be an occupation;
e.g., aide, backer, owner.
    -  POS (part of speech)   
Some words are jobtitles only if the word is a noun: guide  
    - plurals  
Some plurals should not be coded as occupations: royalties.  
Some plurals could be a different code than their singular forms eg. spouses=couple spouse=individual.  
Some words would specify jobtitles mainly in the plural: academics.  
    - capitalization  
ALL CAPS words confuse the check for proper names (e.g., COOPER=Cooper, POTTER=Potter) that are job titles only when not capitalized.
jobs.py now translates all caps words into an initial capital, assuming that all caps words are more often proper nouns than not.
That would correctly catch (and not code) the notUpper list of common last names that match jobs (e.g., Potter)
although it would miss actual jobs such as a potter if it had been written in all caps .
And jobs.py incorrectly renders as proper names the notLower list of words that are not usually jobs titles, 
but are jobs only when the initial letter is upper case (e.g., General).
  
