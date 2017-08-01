# -*- coding: utf-8 -*- 

import requests
from bs4 import BeautifulSoup
import csv
from multiprocessing import Pool

url = "https://rozetka.com.ua/literatura/c4005167/page=1;vozrast-rebenka-68527=1,16,18,372538,372550,372562,372682,372688/"
base_url = 'https://rozetka.com.ua/literatura/c4005167/'
page_part = 'page='
query_part = ';vozrast-rebenka-68527=1,16,18,372538,372550,372562,372682,372688/'

def get_html(url):
    r = requests.get(url)
    return r.text

#counting number of total pages with books 
def get_number_of_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.findAll('a', class_ = 'novisited paginator-catalog-l-link')[-1].get('href')
    total_pages = pages.split('=')[1].split(';')[0]
    
    return int(total_pages)

def get_url_gen(url):
    urls_gen = []
    for i in range(1, get_number_of_pages(get_html(url))):
        url_gen = base_url + page_part + str(i)+ query_part
        urls_gen.append(url_gen)
    return urls_gen
        
#getting links for every book from one page     
def get_books_links(urls_gen):
    books_links = []
    for link in urls_gen:
        soup = BeautifulSoup(get_html(link), 'lxml')
        for div in soup.findAll('div', class_ = 'g-i-tile-i-title clearfix'):
            for a in div.findAll('a'):
                books_links.append(a.get('href'))
            
    return books_links
    
#collecting data for every book on one page
def get_data(books_link):
    soup = BeautifulSoup(get_html(books_link), 'lxml')
    try:
        name = soup.find('h1', class_ ='detail-title').text.strip()
    except:
        name = ''
    try:
        price = soup.find('div', class_ ='detail-price-uah').find('meta')['content']
    except:
        price = ''
    try:
        for i in soup.findAll('div', class_ ='detail-chars-l-i'):
            if (i.find('dt', class_ = 'detail-chars-l-i-title').text.strip() == "Язык"):
                language = i.find('dd', class_ = 'detail-chars-l-i-field').text.strip()
    except:
        language = ''
    try:
        age = soup.find('dd', class_ ='detail-chars-l-i-field').text.strip()
    except:
        age = ''
        
    data = {'name': name, 'price': price, 'language': language, 'age': age}
    write_csv(data)
    
def write_csv(data):
    with open('rozetka_kids_bookss.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['name'],
                         data['price'],
                         data['language'],
                         data['age']))
    
    
def main():    
    #generating links for every page with books
    with Pool(100) as p:
        p.map(get_data, get_books_links(get_url_gen(url)))
    
if __name__ == '__main__':
    main()