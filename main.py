from lxml import html
import requests
from lxml import etree
from io import StringIO, BytesIO

link = 'http://www.kozbeszerzes.hu/adatbazis/megtekint/hirdetmeny/portal_8621_2018/'
notice_page = requests.get(link)
tree = html.fromstring(notice_page.content)
notice_attributes = {}
notice_page = (notice_page.content).decode('utf-8')

notice_table_names = tree.xpath('//table[@class="notice__heading"]/tr/th/text()')

for notice_table_name in notice_table_names:
    
    length_name_find = notice_page.find(notice_table_name)
    length_name_start= notice_page[length_name_find:].find('<td>')
    length_name_end = notice_page[length_name_find:].find('</td></tr>')
    tree_name_string = notice_page[length_name_find+length_name_start+4:length_name_find+length_name_end]
    notice_attributes[notice_table_name] =  tree_name_string
    
    #HREF correction
    
    if notice_table_name == 'Letöltés:':
         
        length_name_find = notice_page.find(notice_table_name)
        length_name_start= notice_page[length_name_find:].find('href="')
        length_name_end = notice_page[length_name_find+7:].find('target="')
        tree_name_string = notice_page[length_name_find+length_name_start+7:length_name_find+length_name_end+5]
        tree_name_string = 'http://www.kozbeszerzes.hu/' + tree_name_string
        notice_attributes[notice_table_name] =  tree_name_string
    
    if notice_table_name == 'Közbeszerzési eljárás:':
        length_name_find = notice_page.find(notice_table_name)
        length_name_start= notice_page[length_name_find:].find('href="')
        length_name_end = notice_page[length_name_find+7:].find('target="')
        tree_name_string = notice_page[length_name_find+length_name_start+6:length_name_find+length_name_end+5]
        notice_attributes[notice_table_name] =  tree_name_string

#Ajánlatkérő
notice_attributes['Ajánlakérő:'] ={}
contracting_authority={}
length_name_start= notice_page.find('I.1) Név és címek')
length_name_end = notice_page.find('I.2) Közös közbeszerzés')
sub_tree_string = notice_page[length_name_start:length_name_end]

parser = etree.HTMLParser()
sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
contracting_authority_names = sub_tree.xpath('//div[@style="padding-left:2em;"]/text()')
for contracting_authority_name in contracting_authority_names:
    length_name_find = sub_tree_string.find(contracting_authority_name)
    length_name_start= sub_tree_string[length_name_find:].find('<span')
    length_name_end = sub_tree_string[length_name_find:].find('</span>')
    tree_name_string = sub_tree_string[length_name_find+length_name_start+47:length_name_find+length_name_end]
    contracting_authority[contracting_authority_name] =  tree_name_string
notice_attributes['Ajánlakérő:'] = contracting_authority
notice_attributes['Ajánlakérő:']['Ajánlatkérő típusa:'] = notice_attributes['Ajánlatkérő típusa:']
notice_attributes['Ajánlakérő:']['Ajánlatkérő fő tevényeségi köre:'] = notice_attributes['Ajánlatkérő fő tevényeségi köre:']

#Tárgy
notice_attributes['Tárgy'] ={}
subject={}
length_name_start= notice_page.find('II. szakasz:')
length_name_end = notice_page.find('III. szakasz:')
if length_name_end ==-1 :
    length_name_end = notice_page.find('IV. szakasz')

sub_tree_string = notice_page[length_name_start:length_name_end]

parser = etree.HTMLParser()
sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
subject_categories = sub_tree.xpath('//div[@style="padding-left:0px;"]/text()')
deleting = ['II.1)','II.2)']
for dele in deleting:
    for sc in subject_categories:
        if dele in sc:
            subject_categories.remove(sc)
        
for subject_category in subject_categories:
    length_name_start= notice_page.find(subject_category)
    length_name_end = notice_page[length_name_find:].find('"padding-left: 0px;"')    
    sub_tree_string = notice_page[length_name_start:length_name_end]
    parser = etree.HTMLParser()
    sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
    subject_items = sub_tree.xpath('//div[@style="padding-left:0px;"]/span/text()')
    subject[subject_category]=subject_items

print(subject)