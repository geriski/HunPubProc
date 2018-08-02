from lxml import html
import requests

link = 'http://www.kozbeszerzes.hu/adatbazis/megtekint/hirdetmeny/portal_9621_2018/'
notice_page = requests.get(link)
tree = html.fromstring(notice_page.content)

notice_main_names = tree.xpath('//table[@class="notice__heading"]/tr/th/text()')
notice_main_values = tree.xpath('//table[@class="notice__heading"]/tr/td/text()')
        
notice_main_attributions = dict(zip(notice_main_names,notice_main_values))


print(notice_main_attributions)
