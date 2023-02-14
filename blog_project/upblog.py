import os, django, sys
import datetime, json, pytz

import requests, re, csv, time
import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from django.http import HttpResponse
from django.db.models import Q
from blog.models import *

def scrap_end_point(start_point, end_point):
    basic_url = 'https://stackoverflow.com/questions?tab=votes&page='

    question_url_list = []
    try:
        for p in range(start_point,end_point):
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

        with open(f'{end_point}.csv','w') as csvfile:
            csvout = csv.DictWriter(csvfile,['url'])
            csvout.writeheader()
            csvout.writerows(question_url_info)

    except:
        question_url_info = [{
            'url'          : props,
        } for props in question_url_list]

        with open(f'{end_point}.csv','w') as csvfile:
            csvout = csv.DictWriter(csvfile,['url'])
            csvout.writeheader()
            csvout.writerows(question_url_info)

def content_scrap():
    def remove_emoji(string):
        emoji_pattern = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                u"\U00002500-\U00002BEF"  # chinese char
                                u"\U00002702-\U000027B0"
                                u"\U00002702-\U000027B0"
                                u"\U000024C2-\U0001F251"
                                u"\U0001f926-\U0001f937"
                                u"\U00010000-\U0010ffff"
                                u"\u2640-\u2642"
                                u"\u2600-\u2B55"
                                u"\u200d"
                                u"\u23cf"
                                u"\u23e9"
                                u"\u231a"
                                u"\ufe0f"  # dingbats
                                u"\u3030"
                                "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

    #1 .어디서부터 할 건지 체크!
    questions = Question.objects.filter(original_title__isnull=True)

    basic_url = 'https://stackoverflow.com'

    for idx, question in enumerate(questions):
        url = basic_url + question.question_endpoint
        print(idx)
        print(url)
        response = requests.get(url)
        bs = BeautifulSoup(response.text, 'html.parser')
        if bs.find(class_="fs-headline1 mb4") != None:
            continue
        scrap_title = str(bs.find(id="question-header").find('a').text)
        question_part = bs.find(class_="postcell")
        tags = bs.find(class_="d-flex ps-relative").find_all('a')
        # driver.get(url)
        original_question = question_part.find('div',{'class':"s-prose js-post-body"})
        questioner  = None
        if question_part.find(itemprop="author") != None:
            if question_part.find(itemprop="author").find('a') != None:
                questioner = question_part.find(itemprop="author").find('a').text
            else:
                questioner = question_part.find(itemprop="author").find('span').text
        else:
            questioner = "Community Wiki"
        
        answers     = bs.find_all(class_="answercell")#driver.find_elements_by_css_selector("div.answercell")
        asked_at    = bs.find(itemprop="dateCreated")['datetime']

        for tag in tags:
            Tag.objects.create(question=question, tag=tag.text)
            
        print('--TAG SUCCEED--')

        for answer in answers:
            answerer = None
            if answer.find(itemprop="author") != None:
                if answer.find(itemprop="author").find('a') != None:
                    answerer = answer.find(itemprop="author").find('a').text
                else: 
                    answerer = answer.find(itemprop="author").find('span').text
            else:
                answerer = "Community Wiki"
            
            original_answer = str(answer.find('div',{'class':"s-prose js-post-body"}))
            Answer.objects.create(original_answer=original_answer,question=question,answerer=answerer)

        print('--ANSWER DONE--')

        question.original_title = scrap_title
        question.questioner     = questioner
        question.asked_at       = asked_at
        question.original_question = str(original_question)
        print('--QUESTION DONE--')
        question.save()
        print(idx)
        time.sleep(2)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
        django.setup()

def data_input_from_csv(filename):

    CSV_PATH_PRODUCTS = f'/Users/youngbinha/Desktop/blogproject/{filename}.csv'

    with open(CSV_PATH_PRODUCTS) as in_file:
        data_reader = csv.reader(in_file)
        next(data_reader,None)
        for row in data_reader:
            row_data    = row[0].strip('{').strip('}').split(', ')
            for i in row_data:
                end_point = i.strip("'")
                Question.objects.create(question_endpoint=end_point)
                print(end_point)

def translation_content():
    target_language = 'ko'
    questions = Question.objects.filter(translated_title__isnull=true)

    for idx ,question in enumerate(questions):
        eng_question = question.original_question
        eng_title    = question.original_title

        kor_question = config.translate_text(target_language, eng_question)
        kor_title    = config.translate_text(target_language, eng_title)
        
        question.translated_question    = kor_question["translatedText"]
        question.translated_title       = config.html_decode(kor_title["translatedText"])
        print(idx)
        print(question.translated_title)
        question.save()

        answers = question.answer_set.all()
        count = 0
        for answer in answers:
            eng_answer = answer.original_answer
            kor_answer = config.translate_text(target_language, eng_answer)

            answer.translated_answer = kor_answer["translatedText"]
            answer.save()
            count+=1
        print(str(count) + ' Answer done ' )
        tags = question.tag_set.all()
        count = 0
        for tag in tags:
            eng_tag = tag.tag
            kor_tag = config.translate_text(target_language, eng_tag)
            Tag.objects.create(question=question, tag=kor_tag["translatedText"])
            count+=1
        print(str(count) + ' Tag done')
        print(str(idx) + "번째 끝 ")

def tistory_up():
    blog = 'tistory'
    #blogger 295~395 9/24/2021
    #tistory 62~78 함
    url = "https://www.tistory.com/apis/post/write"
    visibility = 3       # 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
    category = 1009236   # 카테고리 아이디 (기본값: 0)
    #slogan =  1           # 문자 주소
    #acceptComment =1     # 댓글 허용 (0, 1 - 기본값)
    #password =            # 보호글 비밀번호
    #'Content-Type': 'application/json; charset=utf-8',
    if check_availablity(blog):
        param = languageStartEnd(blog)
        lan     = param["lan"]
        start   = param["start"]
        end     = param["end"]
        questions = Question.objects.prefetch_related(
            'tag_set',
            'answer_set').filter(id__gt=start,id__lte=end)
        
        for idx, question in enumerate(questions):
            content = ""
            original_content = ""
            translated_content = ""
            title = ""
            if lan == "en":
                title += question.original_title           # 글 제목 (필수)
            elif lan == "ko":
                title += config.html_decode(question.translated_title)
            else:
                title += config.html_decode(question.translated_title)
                title += " en)" + question.original_title
            
            tags = question.tag_set.all()
            tag_list = []
            tag = "" 

            for t in tags:
                tag += t.tag + ", "
            endpoint = question.question_endpoint
            answers = question.answer_set.all()
            if lan == "en":
                content += question.original_question             # 글 제목 (필수)
                for a in answers:
                    answerer = a.answerer if a.answerer != None else 'Anonymous'
                    content += "<br/><br/><br/>" + a.original_answer + '<br><strong>' +  answerer + '</strong>'
                content += '<br><br><p>Retrieved from : http:www.stackoverflow.com' + endpoint + '</p>'

            elif lan == "ko":
                content += '<p>질문자 :<strong>' +  question.questioner + '</strong></p><br/>'
                content += question.translated_question
                for a in answers:
                    answerer = a.answerer if a.answerer != None else 'Anonymous'
                    content += "<br><br>" + a.translated_answer + '<br><strong>' +  answerer + '</strong>'
                
                content += '<br><br><p>출처 : http:www.stackoverflow.com' + endpoint + '</p>'

            print(title)
            obj = config.tistory
            access_token = obj['access_token']
            blogName = obj['blog_name']
            data = {
                'access_token':access_token,
                'blogName': blogName,
                'title': title,
                'content': content, 
                'visibility': visibility,
                'category': 0, 
                'tag': tag,
                'output':'json',
                'category':category
            }
            header = {
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            }
            result = requests.post(url, data=data, headers=header)
            standard = Standard.objects.get(blog_name=blog)

            if result.status_code == 200:
                print(result)
                time.sleep(1)
                where_stop = question.id
                if lan == "en":
                    standard.last_finish_en = where_stop
                elif lan == "ko":
                    standard.last_finish_ko = where_stop
                if len(questions) == idx + 1:
                    standard.day_history = datetime.datetime.now()
                standard.today_did += 1
                standard.save()
            elif result.status_code == 401:
                print(result.reason)
                print(result.text)
                return result
            elif result.status_code == 403:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                time.sleep(20)
                continue
            else:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                break
    else:
        print("Today is done")

def papago_translation_content():
    target_language = 'ko'
    questions = Question.objects.filter(translated_title__isnull=True)

    for idx ,question in enumerate(questions):
        eng_question = question.original_question
        eng_title    = question.original_title

        kor_question = config.papago(target_language, eng_question)
        kor_title    = config.papago(target_language, eng_title)
        
        if kor_title == "Failed": 
            print('Translation Failed')
            break

        question.translated_question    = kor_question
        question.translated_title       = config.html_decode(kor_title)
        print(idx)
        print(question.translated_title)
        question.save()

        answers = question.answer_set.all()
        count = 0
        for answer in answers:
            eng_answer = answer.original_answer
            kor_answer = config.papago(target_language, eng_answer)

            answer.translated_answer = kor_answer
            answer.save()
            count+=1
        print(str(count) + ' Answer done ' )
        tags = question.tag_set.all()
        count = 0
        for tag in tags:
            eng_tag = tag.tag
            kor_tag = config.papago(target_language, eng_tag)
            Tag.objects.create(question=question, tag=kor_tag)
            count+=1
        print(str(count) + ' Tag done')
        print(str(idx) + "번째 끝 ")

def check_availablity(blog_platform):
    tz_info = pytz.UTC
    today = datetime.datetime.now(tz_info)
    standard = Standard.objects.get(blog_name=blog_platform)
    if (today - standard.day_history).days >= 1: 
        standard.today_did = 0
        standard.save()
    if standard.limit == standard.today_did: 
        return False
    else:
        return True

def blogger_up():
    url = f'https://www.googleapis.com/blogger/v3/blogs/{config.blogger["blog_id"]}/posts?key={config.blogger["api_key"]}'
    blog = 'blogger'
    if check_availablity(blog):
        param = languageStartEnd(blog)
        lan     = param["lan"]
        start   = param["start"]
        end     = param["end"]
        questions = Question.objects.prefetch_related(
            'tag_set',
            'answer_set').filter(id__gt=start,id__lte=end)
        
        for idx, question in enumerate(questions):
            content = ""
            original_content = ""
            translated_content = ""
            title = ""
            if lan == "en":
                title += question.original_title           # 글 제목 (필수)
            elif lan == "ko":
                title += config.html_decode(question.translated_title)
            else:
                title += config.html_decode(question.translated_title)
                title += " en)" + question.original_title
            
            tags = question.tag_set.all()
            tag_list = []
            tag = "" 

            for t in tags:
                tag += t.tag + ", "
            endpoint = question.question_endpoint
            answers = question.answer_set.all()

            if lan == "en":
                content += question.original_question             # 글 제목 (필수)
                for a in answers:
                    answerer = a.answerer if a.answerer != None else 'Anonymous'
                    content += "<br/><br/><br/>" + a.original_answer + '<br><strong>' +  answerer + '</strong>'
                content += '<br><br><p>Retrieved from : http:www.stackoverflow.com' + endpoint + '</p>'

            elif lan == "ko":
                content += '<p>질문자 :<strong>' +  question.questioner + '</strong></p><br/>'
                content += question.translated_question
                for a in answers:
                    answerer = a.answerer if a.answerer != None else 'Anonymous'
                    content += "<br><br>" + a.translated_answer + '<br><strong>' +  answerer + '</strong>'
                
                content += '<br><br><p>출처 : http:www.stackoverflow.com' + endpoint + '</p>'
            print(idx)
            print(title)
            data = json.dumps({
                "content":content,
                "title":title,
                "labels":tag_list,
            })
            google_access_token = config.blogger['access_token']
            headers = {
            # 'Accept':'application/json',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'ContentType': 'application/json',
            'Authorization': f"Bearer {google_access_token}"
            }
            options = {
                "headers":headers,
                "payload":data,
            }
            print(url)
            result = requests.post(
                    url=url,
                    data=data,headers=headers)
            standard = Standard.objects.get(blog_name=blog)
            if result.status_code == 200:
                print(result)
                time.sleep(1)
                where_stop = question.id
                if lan == "ko":
                    standard.last_finish_ko = where_stop
                elif lan == "en":
                    standard.last_finish_en = where_stop
                standard.today_did += 1
                if len(questions) == idx+1:
                    standard.day_history = datetime.datetime.now()
                standard.save()
            elif result.status_code == 401:
                print(result.reason)
                print(result.text)
                break
            elif result.status_code == 403:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                time.sleep(60)
                continue
            else:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                break
    else:
        print("Today is done")

def languageStartEnd(blog):
    questions   = Question.objects.all()
    kor_post = questions.filter(translated_title__isnull=False).count()
    standard = Standard.objects.get(blog_name=blog)
    if (kor_post - standard.last_finish_ko) < standard.limit:
        lan = "en"
        start = standard.last_finish_en
    else:
        lan = "ko"
        start = standard.last_finish_ko
    end = start + standard.limit - standard.today_did
    result = {
        "lan"   : lan,
        "start" : start,
        "end"   : end
    }

    return result