#!/usr/bin/env python3
'''
Created 30.08.2017
@author haeejuut
'''

import urllib, sys, os, shutil
from time import sleep
from ast import literal_eval as make_tuple

import feedparser
# https://pythonhosted.org/feedparser/
from selenium import webdriver
# http://selenium-python.readthedocs.io/

DATA_PATH = 'tyopaikat.dat'
PHANTOMJS_PATH = 'C:/MyTemp/phantomjs/bin/phantomjs.exe'
RSS ='http://paikat.te-palvelut.fi/tpt-api/tyopaikat.rss?valitutAmmattialat=133&valitutAmmattialat=25&valitutAmmattialat=35&ilmoitettuPvm=1&vuokrapaikka=---'


def tarkasta_pvm():
    '''
    palauttaa DATA_PATH polussa olevan tiedoston ensimmäisen tuplen päivämäärän
    '''
    with open(DATA_PATH, 'r') as f:
        viimeisin = f.readline()
    pvm = make_tuple(viimeisin)[1]    
    print('Viimeisin haettu ilmoitus:',pvm)
    return pvm # muotoa: Wed, 30 Aug 2017 12:53:02 +0300
    

def hae_linkit(feed):
    '''
    Hakee rss feediltä linkit ottaa vain sellaiset, joita ei tyopaikat.dat tiedostossa vielä ole
    '''
    try:
        viimeisin = tarkasta_pvm()
    except:
        viimeisin = 'Ei haettu vielä'
    
    li = []    
    lkm = 0
    for post in feed['entries']:
        if viimeisin == post['published']:
            break
        # välttää feedin viimeisen, joka ei ole työpaikkailmoitus
        if post['link'] != 'http://paikat.te-palvelut.fi/tpt/': 
            li.append((post['title'], post['published'], post['link']))
            lkm += 1    
    if lkm == 0:
        print('Ei löydetty uusia linkkejä, lopetetaan...')
        sys.exit(1)              
    print(lkm,'uutta linkkiä haettu rss feediltä')
    return li
    
def get_html(browser, url, haettu):    
    '''
    Hakee html täysin ladatusta sivusta ja palauttaa haetun luokan omaavan tägin sisällä olevat tekstit
    '''    
    try:        
        browser.get(url)        
        sleep(1)
        print(haettu,'>>',browser.current_url)        
        content = browser.find_element_by_class_name('detailText')
        html_source = content.get_attribute('innerHTML')
        return html_source
    except:        
        return 'Ei löytynyt'

def clear():
    '''
    Tyhjää konsolin
    '''
    name = os.name
    if name == 'posix':
        os.system('clear')
    elif name == 'nt' or name == 'dos':
        os.system('cls')
    else:
        print("\n" * 30)    

def ask(question):
    answer = input(question +" [y/n] > ")
    return answer in ['y', 'Y', 'Yes', 'YES', 'yes']        
    
def kirjoita_tiedostoon(linkki_sisalto):
    '''
    Kirjoittaa uudet ilmoitukset temp.dat tiedostoon,
    lisää datan niiden perään, ja kopioi kokonaisuuden taas datatiedostoon
    '''
    with open('temp.dat', 'a') as tmp, open(DATA_PATH, 'r') as data:
        for tup in linkki_sisalto:
            tmp.write(str(tup) + '\n')
        for line in data:
            tmp.write(line)    
    
    shutil.copyfile('temp.dat', DATA_PATH)
    os.remove('temp.dat')    
    

def main():    
    '''    
    Hakee työpaikkailmoitukset te-palveluiden rss feediltä tyopaikat.dat tiedostoon,
    muodossa 1 rivi = 1 tuple, joka on muotoa ('otsikko', 'pvm', 'linkki', 'sisältö')
    Vaatii python3, selenium, phantomjs
    '''
    clear()    
    print('Skripti hakee te-palveluiden rss syötteeltä työpaikkailmoituksien kuvaukset tyopaikat.dat tiedostoon')
    print('Jos haluat vaihtaa työpaikkojen rajauksia, vaihda rss url kaivuri.py tiedostoon')
    print('Varmista, että kaivuri.py osoittaa phantomjs.exe tiedostoon (DATA_PATH)')
    if ask('Haluatko jatkaa? (avaa seleniumilla uuden phantomjs driverin)'):
        pass
    else:
        sys.exit(1)
    
    # varmistus, että tiedosto on olemassa
    if os.path.exists(DATA_PATH):
        print(DATA_PATH,'löydetty.')
    else:
        print(DATA_PATH,'ei löydetty.')
        sys.exit(1)
    
    feed = feedparser.parse(RSS)
    linkit = hae_linkit(feed)    
    
    if ask('Haetaanko sisällöt? 1 sekunti / linkki'):
        pass
    else:
        sys.exit(1)
    
    linkki_sisalto = []    
    try:
        browser = webdriver.PhantomJS(PHANTOMJS_PATH)
        haettu = 0
        for linkki in linkit:
            sisalto = get_html(browser, linkki[2], haettu)
            linkki_sisalto.append((linkki[0],linkki[1],linkki[2],sisalto))
            haettu += 1    
        browser.close()        
        kirjoita_tiedostoon(linkki_sisalto)    
        print('\nTyöpaikkailmoitukset kirjoitettu tiedostoon', DATA_PATH)    
    except KeyboardInterrupt:
        print('Keskeytit ajon, ilmoituksia ei tallennettu')
    
    print('-'*30)    
    
   
##############################################################################

if __name__ == '__main__':
    main()