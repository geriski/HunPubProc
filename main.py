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
for numb in range(1,800):
    id_list.append(str(numb+24810) + '/2018')

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

alkalmassag_kod_valtoz =[]
alkalmassag_kodok = ['TT','TK','TKö','TV','TE','TH','É','BÉ','ÉKM','K','KÉ','KÉ-VA','KÉ-VK','KÉ-VV','KÉ-K','KÉ-KK','KÉ-L','KÉ-LK','KÉ-HA','KÉ-HK','HI','HI-V','HI-VN','VZ','VZ-TEL','VZ-TER','VZ-VKG','B','GO','EN','EN-HŐ','EN-VI','EN-ME','EN-A','HT','T','T-É','G','G-ÉF','V','GT','ME-É','ME-M','ME-G','ME-V','ME-KÉ','ME-KÉ-VV','ME-HI','ME-HI-TÉ','ME-HI-TV','ME-VZ','ME-B','ME-GO','ME-EN','ME-EN-VEM','E-EN-TH','ME-EN-VI','ME-EN-A','MV-É','MV-É-R','MV-É-M','MV-M','MV-ÉG','MV-ÉG-R','MV-ÉV','MV-ÉV-R','MV-KÉ','MV-KÉ-R','MV-VV','MV-VV-R','MV-TE','MV-TE-R','MV-TV','MV-TV-R','MV-VZ','MV-VZ-R','MV-B','MV-B-R','MV-GO','MV-GO-R','MV-EN','MV-EN-R','MV-EN-A','MV-TH','MV-TH-R','MV-VI','MV-VI-R']
for alkalmassag_kod in alkalmassag_kodok:
    alkalmassag_kod_valtoz.append(" " + alkalmassag_kod+ " ")
    alkalmassag_kod_valtoz.append(" " + alkalmassag_kod+ ")")
    alkalmassag_kod_valtoz.append("(" + alkalmassag_kod+ " ")
    alkalmassag_kod_valtoz.append("(" + alkalmassag_kod+ ")")
    alkalmassag_kod_valtoz.append("(" + alkalmassag_kod.title()+ ")")
    alkalmassag_kod_valtoz.append(" " + alkalmassag_kod.title()+ " ")
    alkalmassag_kod_valtoz.append(" " + alkalmassag_kod.title()+ ")")
    alkalmassag_kod_valtoz.append("(" + alkalmassag_kod.title()+ " ")
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
        if notice_attributes['Beszerzés tárgya:'] == 'Szolgáltatásmegrendelés' :
            continue
        if 'Árubeszerzés' in notice_attributes['Beszerzés tárgya:']:
            continue
        if 'módosítás' in notice_attributes['Hirdetmény típusa:'].lower()  :
            continue
        if 'Bírósági határozat' in notice_attributes['Hirdetmény típusa:'] :
            continue
        if '2-es minta' in notice_attributes['Hirdetmény típusa:'] :
            continue
        if 'helyesbítés' in notice_attributes['Hirdetmény típusa:'].lower() :
            continue
        if 'Árubeszerzés' in notice_attributes['Teljesítés helye:']:
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
        
        #alkalmassági kritériumok
        if notice_page.find('III.1.3)') != -1:
            alkalmassag={}

            length_name_start= notice_page.find('III.1.3)')
            length_name_end = notice_page.find('III.1.4)')
            if length_name_end ==-1 :
                length_name_end = notice_page.find('IV. szakasz')
            
            sub_tree_string = notice_page[length_name_start:length_name_end]
            
            parser = etree.HTMLParser()
            sub_tree   = etree.parse(StringIO(sub_tree_string), parser)
            try:
                alkalmassag_list = sub_tree.xpath('//span[@style="font-weight:200;color: #336699;"]/text()')
            except AssertionError:
                alkalmassag = 'Nincs'
            else:
                
                for alkalmassag_text in alkalmassag_list:
                    for code in alkalmassag_kod_valtoz:
                        length_name_start= alkalmassag_text.find(code)
                        length_name_end = alkalmassag_text[length_name_start:].find('év')
                        if length_name_start ==-1 :
                            x=1
                        else:
                            ev = alkalmassag_text[length_name_start+length_name_end-2:length_name_start+length_name_end-1]
                            if ev.isdigit():
                                alkalmassag[code] = ev    
            
            notice_attributes_all['Alkalmassági kirtériumok'] = alkalmassag
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
        
        #eval_crit_list = {'Többlet tapasztalat':alkalmassag_kod_valtoz}
        #eval_crit_people ={'Munkanélküli':'munkanélküli','Közfoglalkoztatott':'közfoglalkoztatott','Hátrányos helyzetű munkavállaló':'hátrányos'}
        #eval_crit_warr = {'Jótállás':'jótállás'}
        eval_crit_boolean = {'Környezetvédelem':'környezetvédelem',
                             'Fenntarthatóság':'fenntarthatóság',
                             'Örökség':'örökség',
                             'Vízminőség':'vízminőség',
                             'Természet':'természet',
                             'Táj':'táj',
                             'Kötbér':'kötbér',
                             'Munkanélküli':'munkanélküli',
                             'Közfoglalkoztatott':'közfoglalkoztatott',
                             'Hátrányos helyzetű munkavállaló':'hátrányos',
                             'Teljesítési határidő':'teljesítési határidő'}
        
        ertekeles = {}
        eval_crit_exp = {}
        eval_crit_boo = {}
        eval_crit_warr = {}
        ertekeles_corr =[]

        try:
            if notice_attributes_all[' II.2.5) Értékelési szempontok '] != None:
                x = 1
        except KeyError:
            notice_attributes_all[' II.2.5) Értékelési szempontok '] = ['Nincs']
        else:
            for eval_text in notice_attributes_all[' II.2.5) Értékelési szempontok ']:
            
                eval_text_corr = eval_text.replace('\xa0',' ')
                
                ertekeles_corr.append(eval_text_corr)
                
            notice_attributes_all[' II.2.5) Értékelési szempontok '] = ertekeles_corr
            for eval_text in notice_attributes_all[' II.2.5) Értékelési szempontok ']:
                for code in alkalmassag_kod_valtoz:
                    length_name_start= eval_text.find(code)
                    length_name_end = eval_text[length_name_start:].find('hónap')
                    if length_name_start ==-1 :
                        x=1
                    else:
                        ev = eval_text[length_name_start+length_name_end-3:length_name_start+length_name_end-1]
                        if ev.isdigit():
                            eval_crit_exp[code] = ev 
            ertekeles['Szakmai többlettapasztalat'] = eval_crit_exp   
        
            for k,v in  eval_crit_boolean.items():
                for eval_text in notice_attributes_all[' II.2.5) Értékelési szempontok ']:
                    if v in eval_text.lower():
                        eval_crit_boo[k]= True
                    
            
            ertekeles.update(eval_crit_boo)
            
            for eval_text in notice_attributes_all[' II.2.5) Értékelési szempontok ']:
                
                    length_name_start= eval_text.lower().find('jótállás')
                    length_name_end = eval_text[length_name_start:].find('hónap')
                    if length_name_start ==-1 :
                        x=1
                    else:
                        ev = eval_text[length_name_start+length_name_end-3:length_name_start+length_name_end-1]
                        if ev.isdigit():
                            eval_crit_warr['Jótállás'] = ev
                        else:
                            eval_crit_warr['Jótállás'] = 0
            ertekeles.update(eval_crit_warr)             
        
        notice_attributes_all.update(ertekeles)
        filter_parameters = ['Közbeszerzési Értesítő száma:', 'Beszerzés tárgya:', 'Eljárás fajtája:', 'Közzététel dátuma:','Iktatószám:','CPV Kód:','Ajánlatkérő:', 'Teljesítés helye:', 'Nyertes ajánlattevő:', 'Ajánlatkérő típusa:', 'Ajánlatkérő fő tevényeségi köre:', 'Letöltés:','Közbeszerzési eljárás:','Ajánlatkérő/  Nemzeti azonosítószám: ', 'Ajánlatkérő/  Város: ','Ajánlatkérő/  NUTS-kód: ', 'Ajánlatkérő/  Postai irányítószám: ', ' II.1.1) Elnevezés: ', ' II.1.4) A közbeszerzés rövid ismertetése: ',' II.2.3) A teljesítés helye: ', ' II.2.5) Értékelési szempontok ', ' II.2.8) Európai uniós alapokra vonatkozó információk ', 'Nyertes', 'Nyertes/  Város:', 'Nyertes/  NUTS-kód: ', 'Nyertes/  Postai irányítószám: ', 'Nyertes/  A nyertes ajánlattevő adószáma (adóazonosító jele): ', 'Beszerzés összege', 'Beszerzés pénzneme', 'Alkalmassági kirtériumok','Környezetvédelem',
                             'Fenntarthatóság',
                             'Örökség',
                             'Vízminőség',
                             'Természet',
                             'Táj',
                             'Kötbér',
                             'Munkanélküli',
                             'Közfoglalkoztatott',
                             'Hátrányos helyzetű munkavállaló','Jótállás', 'Szakmai többlettapasztalat',
                             'Teljesítési határidő']
        
        notice_attributes_all_filtered ={}
        for filter_parameter in filter_parameters:    
    
            for k, v in notice_attributes_all.items():
                
                if filter_parameter == k:
                    notice_attributes_all_filtered[k] = v
                
        
        notice[notice_attributes['Iktatószám:']] = notice_attributes_all_filtered
       
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
