def content_scrap(last_point):
    import os, django, sys
    import datetime

    from bs4 import BeautifulSoup
    import requests, re, csv, time

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
    django.setup()

    from blog.models import Question, Answer, Tag

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
    questions = Question.objects.filter(id__gt=last_point)

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