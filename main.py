from lxml import html
import requests
from lxml import etree
from io import StringIO, BytesIO
import json
import pandas as pd
import numpy as np
link1= 'http://www.kozbeszerzes.hu/adatbazis/megtekint/hirdetmeny/portal_'

id_list=[]
#for num in range(1,3):
#    pagelists.append(str(link1) + str(num+5950) + '_2018/')
for numb in range(1,1000):
    id_list.append(str(numb+1000) + '/2018')

#print(pagelists)

# search for the new notices

#load the database
filename = 'dict.json'
with open(filename) as f_obj:
    notices_existing = json.load(f_obj)

download_notices = []  
for ids in id_list:
    if ids in notices_existing.keys():
        continue
    else:
        download_notices.append(ids)
print('Downloading: ', download_notices )
pagelists=[]
for items in download_notices:
    num= int(items[:items.find('/')])
    pagelists.append(str(link1) + str(num) + '_2018/')
notice = {}
for link in pagelists:
    notice_page = requests.get(link)
    tree = html.fromstring(notice_page.content)
    notice_attributes = {}
    notice_attributes_all = {}

    notice_page = (notice_page.content).decode('utf-8')
    
    if notice_page.find('A keresett oldal nem található') == -1:
    
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
        #if notice_attributes['Beszerzés tárgya:'] == 'Szolgáltatásmegrendelés' :
        #    continue
        #if 'Árubeszerzés' in notice_attributes['Beszerzés tárgya:']:
        #    continue
        if 'módosítás' in notice_attributes['Hirdetmény típusa:'].lower()  :
            continue
        if 'Bírósági határozat' in notice_attributes['Hirdetmény típusa:'] :
            continue
        if '2-es minta' in notice_attributes['Hirdetmény típusa:'] :
            continue
        if 'helyesbítés' in notice_attributes['Hirdetmény típusa:'].lower() :
            continue
        notice_attributes_all.update(notice_attributes)
        
        #Fixing the the text in notice_attributes_all. replace new line with ', '
        for k, value in notice_attributes_all.items():
            #In case of the replace function doesn't work, don't do anything
            try:
                value=value.replace('\n',', ')
            except AttributeError:
                continue
            notice_attributes_all.update({k: value})
        
        #Ajánlatkérő
        length_name_start= notice_page.find('I.1) Név és címek')
        length_name_end = notice_page.find('I.2) Közös közbeszerzés')
        if length_name_end ==-1 :
            length_name_end = notice_page.find('II. szakasz')
        sub_tree_string = notice_page[length_name_start:length_name_end]
        
        #print('Ajánlatkérő,60:', length_name_start, length_name_end)
        
        parser = etree.HTMLParser()
        sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
        contracting_authority_names = sub_tree.xpath('//div[@style="padding-left:2em;"]/text()')
        for contracting_authority_name in contracting_authority_names:
            length_name_find = sub_tree_string.find(contracting_authority_name)
            length_name_start= sub_tree_string[length_name_find:].find('<span')
            length_name_end = sub_tree_string[length_name_find:].find('</span>')
            tree_name_string = sub_tree_string[length_name_find+length_name_start+47:length_name_find+length_name_end]
            notice_attributes_all['Ajánlatkérő/ ' + str(contracting_authority_name)] =  tree_name_string
    
        #Tárgy
        
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
        #print(subject_categories)        
        for subject_category in subject_categories:
            length_name_start= notice_page.find(subject_category)
            try:
                length_name_end = notice_page[length_name_start:].find(subject_categories[subject_categories.index(subject_category)+1])
            except IndexError:
                length_name_end = notice_page.find('III. szakasz:')
                if length_name_end ==-1 :
                    length_name_end = notice_page.find('IV. szakasz')
                if length_name_end ==-1 :
                    length_name_end = notice_page.find('VI. szakasz') 
    
            sub_tree_string = notice_page[length_name_start:length_name_start+length_name_end]
            parser = etree.HTMLParser()
            sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
            subject_items = sub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
            subject[subject_category]=subject_items
            #print(subject_category)
        
        notice_attributes_all.update(subject)

        #megkötés dátuma
        if notice_page.find('V.2.1) A szerződés megkötésének dátuma') != -1:
          length_name_start= notice_page.find('V.2.1) A szerződés megkötésének dátuma')
          length_name_end = notice_page.find('V.2.2) Ajánlatokra vonatkozó információk')
          sub_tree_string = notice_page[length_name_start:length_name_end]
          parser = etree.HTMLParser()
          sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
          result_items = sub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
          try:
            result_date = result_items[0]
          except IndexError:
            notice_attributes_all['Szerződés megkötés dátuma'] = None
          else:
            notice_attributes_all['Szerződés megkötés dátuma']= result_date
        
          #nyertes
          result_contractor_attrib = {}
          length_name_start= notice_page.find('V.2.3) A nyertes ajánlattevő neve és címe')
          length_name_end = notice_page.find('V.2.4) A szerződés/rész')
          sub_tree_string = notice_page[length_name_start:length_name_end]
          parser = etree.HTMLParser()
          sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
          result_categories = sub_tree.xpath('//div[@style="padding-left:2em;"]/text()')
        
          for result_category in result_categories:
              length_name_start= sub_tree_string.find(result_category)
              try:
                length_name_end = sub_tree_string[length_name_start:].find(result_categories[result_categories.index(result_category)+1])
              except IndexError:
                length_name_end = 10
          
              subsub_tree_string = sub_tree_string[length_name_start:length_name_start+length_name_end]
              #print('nyertes,150:', length_name_start, length_name_end)
              parser = etree.HTMLParser()
              subsub_tree   = etree.parse(StringIO(subsub_tree_string), parser)
              result_items = subsub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
              try:
                result_contractor_attrib['Nyertes/ ' + str(result_category)]=result_items[0]
              except IndexError:
                result_contractor_attrib['Nyertes/ ' + str(result_category)] = None
              notice_attributes_all['Nyertes'] = 'Volt'  
          notice_attributes_all.update(result_contractor_attrib)
        else:
          notice_attributes_all['Szerződés megkötés dátuma'] = None
          notice_attributes_all['Nyertes'] = None
        try:
            notice_attributes_all[' II.1.1) Elnevezés: '] = notice_attributes_all[' II.1.1) ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.1.1) ']
        try:
            notice_attributes_all[' II.1.1) Elnevezés: '] = notice_attributes_all[' Elnevezés: ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' Elnevezés: ']
        try:
            notice_attributes_all[' II.1.4) A közbeszerzés rövid ismertetése: '] = notice_attributes_all[' II.1.4) Rövid meghatározás: ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.1.4) Rövid meghatározás: ']
        try:
            notice_attributes_all[' II.1.5) Részekre bontás '] = notice_attributes_all[' II.1.6) Részekre vonatkozó információk ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.1.6) Részekre vonatkozó információk ']
        try:
            notice_attributes_all[' II.1.6) A beszerzés végleges összértéke (ÁFA nélkül) '] = notice_attributes_all[' II.1.7) A beszerzés végleges összértéke (áfa nélkül) ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.1.7) A beszerzés végleges összértéke (áfa nélkül) ']
        try:
            notice_attributes_all[' II.1.4) A közbeszerzés rövid ismertetése: '] = notice_attributes_all[' II.2.4) A közbeszerzés ismertetése: ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.2.4) A közbeszerzés ismertetése: ']
        try:
            notice_attributes_all[' II.2.9) További információ: '] = notice_attributes_all[' II.2.14) További információ: ']
        except KeyError:
            x=1
        else:
            del notice_attributes_all[' II.2.14) További információ: ']
        to_delete =[' (éééé/hh/nn) ',' Árubeszerzés ', ' Építési beruházás ',' II.1.2) ',' II.1.2) Fő CPV-kód: ', ' II.1.3) A szerződés típusa ', ' II.1.3) A szerződés típusa Szolgáltatásmegrendelés ', ' II.1.5) ', ' II.1.5) Becsült teljes érték vagy nagyságrend: ', ' II.1.6) Részekre bontás ', ' II.2.1) ', ' II.2.1) Elnevezés: ', ' II.2.10) Opciókra vonatkozó információ ', ' II.2.11) Opciókra vonatkozó információ ', ' II.2.13) További információ ', ' II.2.6) Becsült érték: ',' II.2.6) Becsült teljes érték vagy nagyságrend: ', ' II.2.9) Változatokra (alternatív ajánlatokra) vonatkozó információk ']
        
        for to_dele in to_delete:
            try:
                del notice_attributes_all[to_dele]
            except KeyError:
                y=1
        try:
            notice_attributes_all['Beszerzés összege'] = notice_attributes_all[' II.1.6) A beszerzés végleges összértéke (ÁFA nélkül) '][0]
            notice_attributes_all['Beszerzés pénzneme'] = notice_attributes_all[' II.1.6) A beszerzés végleges összértéke (ÁFA nélkül) '][-1]
        except (KeyError, IndexError):
                y=1
        
        try:
            notice_attributes_all['Beszerzés összege'] = notice_attributes_all[' ) '][0]
            notice_attributes_all['Beszerzés pénzneme'] = notice_attributes_all[' ) '][-1]
        except (KeyError, IndexError):
            x=1
        else:
            del notice_attributes_all[' ) ']
        try:
            notice_attributes_all['Beszerzés összege']=notice_attributes_all['Beszerzés összege'].replace('.','')
            notice_attributes_all['Beszerzés összege']=notice_attributes_all['Beszerzés összege'].replace(',','')
            notice_attributes_all['Beszerzés összege']=notice_attributes_all['Beszerzés összege'].replace('-','')
            notice_attributes_all['Beszerzés összege']=notice_attributes_all['Beszerzés összege'].replace(' ','')
            notice_attributes_all['Beszerzés összege']=notice_attributes_all['Beszerzés összege'].replace('Ft','')
        except KeyError:
            x=1
        
        notice[notice_attributes['Iktatószám:']] = notice_attributes_all
       
        print('Ready to export: ', notice_attributes['Iktatószám:'])
    else:
      continue
notices_existing.update(notice)
print('All: ', notices_existing.keys())

#import to DataFrame
Notices = pd.DataFrame.from_dict(notices_existing, orient='index')

#export to csv

Notices.to_csv(path_or_buf='notices.csv', sep='$')

#export to json
json = json.dumps(notices_existing,  indent=4)
f = open("dict.json","w")
f.write(json)
f.close()
