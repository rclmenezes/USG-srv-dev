# -*- encoding: utf-8 -*-

dept_codes = u"""
AAS Program in African-American Studies
AFS Program in African Studies
AMS Program in American Studies
ANT Anthropology
AOS Program in Atmospheric and Oceanic Sciences
APC Program in Applied and Computational Mathematics
ARA Arabic
ARC School of Architecture
ART Art and Archaeology
AST Astrophysical Sciences
ATL Atelier
BCS Bosnian-Croatian-Serbian
CEE Civil and Environmental Engineering
CHE Chemical Engineering
CHI Chinese
CHM Chemistry
CHV University Center for Human Values
CLA Classics
CLG Classical Greek
COM Comparative Literature
COS Computer Science
CWR Program in Creative Writing
CZE Czech
DAN Dance
EAP Program in East Asian Studies
EAS East Asian Studies
ECO Economics
ECS Program in European Cultural Studies
EEB Ecology and Evolutionary Biology
EGR Engineering
ELE Electrical Engineering
ENG English
ENV Program in Environmental Studies
EPS Program in Contemporary European Politics and Society
FIN Program in Finance
FRE French
FRS Program of Freshman Seminars in the Residential Colleges
GEO Geosciences
GER German
HEB Hebrew
HIN Hindi
HIS History
HLS Program in Hellenic Studies
HOS Program in History of Science
HUM Program in Humanistic Studies
ISC Integrated Science Curriculum
ITA Italian
JDS Program in Judaic Studies
JPN Japanese
JRN Journalism
KOR Korean
LAS Program in Latin American Studies
LAT Latin
LIN Program in Linguistics
MAE Mechanical and Aerospace Engineering
MAT Mathematics
MED Program In Medieval Studies
MOD Media and Modernity
MOG Modern Greek
MOL Molecular Biology
MSE Program In Materials Science And Engineering
MUS Music
NES Near Eastern Studies
NEU Program in Neuroscience
ORF Operations Research and Financial Engineering
PAW Program In The Ancient World
PER Persian
PHI Philosophy
PHY Physics
PLS Polish
POL Politics
POP Program In Population Studies
POR Portuguese
PSY Psychology
QCB Program in Quantitative and Computational Biology
REL Religion
RUS Russian
SAS Program in South Asian Studies
SLA Slavic Languages And Literatures
SOC Sociology
SPA Spanish
STC Council On Science And Technology
SWA Swahili
THR Program In Theater And Dance
TPP Program In Teacher Preparation
TRA Program in Translation, Intercultural Communication
TUR Turkish
URB Program in Urban Studies
VIS Program In Visual Arts
WOM Program In the Study of Women and Gender
WRI Princeton Writing Program
WWS Woodrow Wilson School Of Public And International Affairs
#MISC Miscellaneous
""".split(u'\n')

dept_data = u"""
ANT,http://www.princeton.edu/anthropology/,Lawrence Rosen,lrosen@princeton.edu
ARC,http://soa.princeton.edu/,Mario Gandelsonas,mgndlsns@princeton.edu
ART,http://www.princeton.edu/artandarchaeology/,Anne McCauley,mccauley@princeton.edu
AST,http://www.astro.princeton.edu/,Neta Bahcall,neta@astro.princeton.edu
CHE,http://www.princeton.edu/che/,Julie Sefa,jsefa@princeton.edu
CHM,http://www.princeton.edu/~chemdept/,Jeffrey Schwartz,jschwart@princeton.edu
CEE,http://www.princeton.edu/cee/,Jennifer Poacelli,poacelli@princeton.edu
CLA,http://www.princeton.edu/~classics/,Harriet Flower,hflower@princeton.edu
COM,http://www.princeton.edu/complit/,Thomas Hare,thare@princeton.edu
COS,http://www.cs.princeton.edu/,Brian Kernighan,bwk@cs.princeton.edu
EAS,http://eastasia.princeton.edu/,David Leheny,dleheny@princeton.edu
EEB,http://www.princeton.edu/eeb/,James Gould,gould@princeton.edu
ECO,http://www.princeton.edu/economics/,Avinash Dixit,dixitak@princeton.edu
ELE,http://www.ee.princeton.edu/,Bradley Dickinson,bradley@princeton.edu
ENG,http://english.princeton.edu/,Jeff Dolven,jdolven@princeton.edu
FRE,http://www.princeton.edu/fit/,André Benhaïm,abenhaim@princeton.edu
ITA,http://www.princeton.edu/fit/,André Benhaïm,abenhaim@princeton.edu
GEO,http://www.princeton.edu/geosciences/,Satish Myneni,smyneni@princeton.edu
GER,http://www.princeton.edu/german/,Thomas Levin,tylevin@princeton.edu
HIS,http://www.princeton.edu/history/,James Dun,jamesdun@princeton.edu
MAT,http://www.math.princeton.edu/index.html,Simon Kochen,kochen@math.princeton.edu
MAE,http://www.princeton.edu/mae/,Michael Littman,mlittman@princeton.edu
MOL,http://www.molbio.princeton.edu/,Mark Rose,mdrose@princeton.edu
MUS,http://www.music.princeton.edu/,Elizabeth Bergman,elizberg@princeton.edu
NES,http://www.princeton.edu/~nes/,Erika Gilson,ehgilson@princeton.edu
ORF,http://www.orfe.princeton.edu/,Alain Kornhauser,alaink@princeton.edu
PHI,http://philosophy.princeton.edu/,John Burgess,jburgess@princeton.edu
PHY,http://www.princeton.edu/physics/,Edward Groth III,groth@princeton.edu
POL,http://www.princeton.edu/politics/,Melissa Harris-Lacewell,lacewell@princeton.edu
PSY,https://weblamp.princeton.edu/~psych/psychology/home/index.php,Daniel Osherson,osherson@princeton.edu
REL,http://www.princeton.edu/religion/,Judith Weisenfeld,jweisenf@princeton.edu
SLA,http://slavic.princeton.edu/,Petre Petrov,ppetrov@princeton.edu
SOC,http://sociology.princeton.edu/,Mitchell Duneier,mduneier@princeton.edu
SPA,http://www.princeton.edu/spo/,Angel Loureiro,loureiro@princeton.edu
POR,http://www.princeton.edu/spo/,Angel Loureiro,loureiro@princeton.edu
WWS,http://wws.princeton.edu/,Stanley Katz,snkatz@princeton.edu
""".split(u'\n')

class Department(object):
    def __init__(self, dept, url, contact, email):
        self.dept    = dept
        self.url     = url
        self.contact = contact
        self.email   = email

    def __repr__(self):
        data = repr((self.dept, self.url, self.contact, self.email))
        return 'Department%s' % data

NAMES = {}
DEPTS = {}

for line in dept_codes:
    line = line.strip()
    if not line:
        continue

    dept, irrelevant, name = line.partition(u' ')
    NAMES[dept] = name

for line in dept_data:
    line = line.strip()
    if not line:
        continue

    dept, url, contact, email = line.split(',')

    assert dept in NAMES, dept
    assert len(dept) == 3, dept
    assert u'@' in email, email

    DEPTS[dept] = Department(dept, url, contact, email)

def is_valid_dept(dept):
    return dept.upper() in NAMES.keys()

def get_dept_name(dept):
    """Returns the full department name for the :obj:`dept` code, an
    empty string if none found."""

    if is_valid_dept(dept):
        return NAMES[dept.upper()]
    else:
        return u''

def get_dept(dept):
    """Returns a :class:`ptx.dept.Department` object if the
    department name passed has contact information associated with it,
    :obj:`None` otherwise."""

    return DEPTS.get(dept.upper())
