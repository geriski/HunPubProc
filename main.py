from lxml import html
import requests
from lxml import etree
from io import StringIO, BytesIO

link = 'http://www.kozbeszerzes.hu/adatbazis/megtekint/hirdetmeny/portal_9621_2018/'
notice_page = requests.get(link)
tree = html.fromstring(notice_page.content)
notice_attributes = {}
notice_page = (notice_page.content).decode('utf-8')

notice_table_names = tree.xpath('//table[@class="notice__heading"]/tr/th/text()')

for notice_table_name in notice_table_names:
    
    length_name_find = notice_page.find(notice_table_name)
    #print(length_name_find)
    length_name_start= notice_page[length_name_find:].find('<td>')
    #print(length_name_start)
    length_name_end = notice_page[length_name_find:].find('</td></tr>')
    #print(length_name_end)
    tree_name_string = notice_page[length_name_find+length_name_start+4:length_name_find+length_name_end]
    #print(tree_name_string)
    notice_attributes[notice_table_name] =  tree_name_string
    
    #HREF correction
    
    if notice_table_name == 'Letöltés:':
         
        length_name_find = notice_page.find(notice_table_name)
        length_name_start= notice_page[length_name_find:].find('href="')
        #print(length_name_start)
        length_name_end = notice_page[length_name_find+7:].find('target="')
        #print(length_name_end)
        tree_name_string = notice_page[length_name_find+length_name_start+7:length_name_find+length_name_end+5]
        #print(tree_name_string)
        tree_name_string = 'http://www.kozbeszerzes.hu/' + tree_name_string
        notice_attributes[notice_table_name] =  tree_name_string
    
    if notice_table_name == 'Közbeszerzési eljárás:':
        length_name_find = notice_page.find(notice_table_name)
        length_name_start= notice_page[length_name_find:].find('href="')
        #print(length_name_start)
        length_name_end = notice_page[length_name_find+7:].find('target="')
        #print(length_name_end)
        tree_name_string = notice_page[length_name_find+length_name_start+6:length_name_find+length_name_end+5]
        #print(tree_name_string)
        notice_attributes[notice_table_name] =  tree_name_string

print(notice_attributes)
