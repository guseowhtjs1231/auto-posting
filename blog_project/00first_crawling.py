def scrap_end_point(start_point, end_point):
    from bs4 import BeautifulSoup
    import requests
    import re
    import csv
    import time
    from selenium import webdriver
    from urllib.request import urlopen
    from urllib.parse import quote_plus

    basic_url = 'https://stackoverflow.com/questions?tab=votes&page='

    question_url_list = []
    try:
        for p in range(61417,75000):
            response = requests.get(basic_url + str(p))
            bs = BeautifulSoup(response.text, 'html.parser')
            url_list = bs.find_all('div',{'class':re.compile('question-summary')})
            time.sleep(5)
            prod_url_list = []
            for url in url_list:
                real_url = url.find('a',{'class':re.compile('question-hyperlink')})
                prod_url_list.append(real_url.attrs['href'])

            setted_urllist = set(prod_url_list)
            print(p)
            print(setted_urllist)
            question_url_list.append(setted_urllist)

        question_url_info = [{
            'url'          : props,
        } for props in question_url_list]

        with open(f'question_url_info{end_point}.csv','w') as csvfile:
            csvout = csv.DictWriter(csvfile,['url'])
            csvout.writeheader()
            csvout.writerows(question_url_info)

    except:
        question_url_info = [{
            'url'          : props,
        } for props in question_url_list]

        with open(f'question_url_info{end_point}.csv','w') as csvfile:
            csvout = csv.DictWriter(csvfile,['url'])
            csvout.writeheader()
            csvout.writerows(question_url_info)