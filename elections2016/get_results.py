#coding: utf8
import urllib2
from bs4 import BeautifulSoup as bs
from BeautifulSoup import BeautifulSoup
import re
import pickle
import sys
import os

DIR = '../../..'
URL_RESULTS = 'http://www.vybory.izbirkom.ru/region/region/izbirkom?action=show&root=1&tvd=100100067795854&vrn=100100067795849&region=0&global=1&sub_region=0&prver=0&pronetvd=0&vibid=100100067795854&type=233'
URL_RESULTS_REG = re.compile('http:\/\/www\.vybory\.izbirkom\.ru')
URL_RESULTS_REG1 = re.compile('http:\/\/www\.vybory\.izbirkom\.ru.+\&type=233')
URL_CIK_PATTERN = u'комиссии субъекта'
ROWS_NAMES = {
    u'Число действительных избирательных бюллетеней': 'valid_papers',
    u'Число избирателей, внесенных в список избирателей на момент окончания голосования': 'voters',
    u'Число избирателей, проголосовавших по открепительным удостоверениям на избирательном участке': 'voters_dist',
    u'Число избирательных бюллетеней, выданных в помещении для голосования в день голосования': 'papers_int',
    u'Число избирательных бюллетеней, выданных вне помещения для голосования в день голосования': 'papers_out',
    u'Число избирательных бюллетеней, выданных избирателям, проголосовавшим досрочно': 'papers_before',
    u'Число избирательных бюллетеней, не учтенных при получении': 'papers_notvalid_initially',
    u'Число избирательных бюллетеней, полученных участковой избирательной комиссией': 'papers_received',
    u'Число избирательных бюллетеней, содержащихся в переносных ящиках для голосования': 'papers_temp_box',
    u'Число избирательных бюллетеней, содержащихся в стационарных ящиках для голосования': 'papers_stationary_box',
    u'Число недействительных избирательных бюллетеней': 'papers_notvalid',
    u'Число открепительных удостоверений, выданных избирателям территориальной избирательной комиссией': 'dist_allowed',
    u'Число открепительных удостоверений, выданных на избирательном участке до дня голосования': 'dist_allowed_before',
    u'Число открепительных удостоверений, полученных участковой избирательной комиссией': 'dist_received',
    u'Число погашенных избирательных бюллетеней': 'papers_used',
    u'Число погашенных неиспользованных открепительных удостоверений': 'papers_dist_notused',
    u'Число утраченных избирательных бюллетеней': 'papers_lost',
    u'Число утраченных открепительных удостоверений': 'papers_lost_dist',
    u'1. ВСЕРОССИЙСКАЯ ПОЛИТИЧЕСКАЯ ПАРТИЯ "РОДИНА"': 'rodina',
    u'10. Общественная организация Всероссийская политическая партия "Гражданская Сила"': 'sila',
    u'11. Политическая партия "Российская объединенная демократическая партия "ЯБЛОКО"': 'apple',
    u'12. Политическая партия "КОММУНИСТИЧЕСКАЯ ПАРТИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ"': 'kprf',
    u'13. Политическая партия "ПАТРИОТЫ РОССИИ"': 'patriots',
    u'14. Политическая партия СПРАВЕДЛИВАЯ РОССИЯ': 'spavros',
    u'2. Политическая партия КОММУНИСТИЧЕСКАЯ ПАРТИЯ КОММУНИСТЫ РОССИИ': 'comros',
    u'3. Политическая партия "Российская партия пенсионеров за справедливость"' : 'renters',
    u'4. Всероссийская политическая партия "ЕДИНАЯ РОССИЯ"' : 'zhuliki',
    u'5. Политическая партия "Российская экологическая партия "Зеленые"': 'green',
    u'6. Политическая партия "Гражданская Платформа"': 'gr_platf',
    u'7. Политическая партия ЛДПР - Либерально-демократическая партия России': 'ldpr',
    u'8. Политическая партия "Партия народной свободы" (ПАРНАС)': 'parnas',
    u'9. Всероссийская политическая партия "ПАРТИЯ РОСТА"': 'rost'
}
ROW1 = u'Число избирателей, внесенных в список избирателей на момент окончания голосования'

def get_all_urls(url, pattern = None):
    html_page = urllib2.urlopen(url)
    soup = bs(html_page, "lxml")
    res = []
    for url in soup.findAll('a'):
        url_path = url.get('href')
        if pattern and pattern.match(url_path):
            res.append(url_path) 
        elif not pattern:
            res.append(url_path)
    return res

def get_matching_url(url, pattern):
    html_page = unicode(urllib2.urlopen(url).read(), 'Windows-1251')
    soup = bs(html_page, "lxml")
    for url in soup.findAll('a'):
        url_path = url.get('href')
        url_text = url.string
        if url_text and pattern in url_text:
                return url_path
    return None

def get_election_results_table(url, text):
    html_page = unicode(urllib2.urlopen(url).read(), 'Windows-1251')
    soup = BeautifulSoup(html_page)
    
    values = []
    
    t = None
    t1 = None
    el = soup.find(lambda tag: tag.text==text)
    t = el.parent.parent
    t1 = el.parent.parent.parent.parent.findAll('table')[1]
    if not t:
        print 'not found', url
    for row in t.findAll('tr')[1:]:
        el = row.findAll("td")[1].text.strip()
        values.append(el)
        if el and el not in ROWS_NAMES and el not in [u'&nbsp;']:
            print el.encode('utf-8')
    if len(values) <> 33:
        print url, len(values)
    
    res = {}
    headers = []
    
    
    cells = t1.findAll('tr')[0].findAll("td")
    for cell in cells:
        el =  cell.text.strip()
        headers.append(el)
    i = 0
    for row in t1.findAll('tr')[1:]:
        cells = row.findAll('nobr')
        j = 0
        for cell in cells:
            val_ =  cell.text.strip()
            key_ = values[i]
            if key_:
                key_ = ROWS_NAMES.get(key_, key_)
                header = headers[j]
                ans = None
                try:
                    ans = re.search('[0-9]+', val_).group(0)
                except:
                    print url, header, ans
                    pass
                try:
                    header = re.search('[0-9]+', header).group(0)
                except:
                    print url, header
                    pass
                if header not in res:
                    res[header] = {}
                res[header][key_] = ans
            j += 1
        i += 1
    return res

def get_OIK_region(url):
    html_page = unicode(urllib2.urlopen(url).read(), 'Windows-1251')
    soup = bs(html_page, "lxml")
    for el in soup.findAll("td"):
        if el.get_text().strip() == u'Наименование избирательной комиссии':
            return el.parent.findAll("td")[1].get_text().strip()

if __name__ == "__main__":
    urls_main = set(get_all_urls(URL_RESULTS, URL_RESULTS_REG))
    print 'main urls downloaded'
    urls_sub = {}
    for url in urls_main:
        tmp = get_all_urls(url, URL_RESULTS_REG1) 
        urls_sub[url] = set(tmp)
    print 'suburls downloaded'
    data = {}
    i = 0
    for url in list(urls_main):
        oblast = get_OIK_region(url)
        sub_urls = urls_sub[url]
        print 'start processing', i, url, len(sub_urls), oblast
        if oblast not in data:
            data[oblast] = {}
        for sub_url in sub_urls:
            url_res = get_matching_url(sub_url, URL_CIK_PATTERN)
            res = get_election_results_table(url_res, ROW1)
            for el in res:
                if el in data[oblast]:
                    print 'ERROR', el, sub_url
                else:
                    data[oblast][el] = res[el]
        print 'success'
        i += 1
    save_path = os.path.abspath(os.path.join(os.getcwd(), DIR, 'elections.pickle'))
    with open(save_path, 'wb') as handle:
        pickle.dump(data, handle)
