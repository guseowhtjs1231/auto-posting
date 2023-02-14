os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()
import time, json



#blogger 295~395 9/24/2021
#tistory 62~78 함

def blog_upload_content(blog_platform,start_point,end_point):
    url_list = ["https://www.tistory.com/apis/post/write",f'https://www.googleapis.com/blogger/v3/blogs/{config.blogger["blog_id"]}/posts?key={config.blogger["api_key"]}']
    visibility = 3       # 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
    category = 1009236   # 카테고리 아이디 (기본값: 0)
    #slogan =  1           # 문자 주소
    #acceptComment =1     # 댓글 허용 (0, 1 - 기본값)
    #password =            # 보호글 비밀번호
    #'Content-Type': 'application/json; charset=utf-8',
    questions = Question.objects.prefetch_related('tag_set','answer_set').filter(id__gt=start_point,id__lt=end_point)
    for question in questions:
        content = ""
        original_content = ""
        translated_content = ""
        title = ""
        #original_title      = question.original_title           # 글 제목 (필수)
        translated_title    = config.html_decode(question.translated_title)
        title += translated_title
        # title += " en)"
        # title += original_title 
        
        # published = datetime.datetime.today()      # 발행시간 (TIMESTAMP 이며 미래의 시간을 넣을 경우 예약. 기본값: 현재시간)
        
                        # 태그 (',' 로 구분)
        tags = question.tag_set.all()
        tag_list = []
        tag = "" 
        if blog_platform =="blogger":
            for t in tags:
                tag_list.append(t.tag)
        elif blog_platform == "tistory":
            for t in tags:
                tag += t.tag + ", "
        
        answers = question.answer_set.all()
        
        # original_question = question.original_question           # 글 내용
        # original_content += original_question
        translated_content += '<p>질문자 :<strong>' +  question.questioner + '</strong></p><br/>'
        translated_content += question.translated_question

        for a in answers:
            answerer = a.answerer if a.answerer != None else 'Anonymous'
            # original_content += "<br/><br/><br/>" + a.original_answer + '<br><strong>' +  a.answerer + '</strong>'
            translated_content += "<br><br>" + a.translated_answer + '<br><strong>' +  answerer + '</strong>'

        endpoint = question.question_endpoint
        content += translated_content #+ '<br/><br/><br/>' + original_content
        content += '<br><br><p>출처 : <a href="http://www.stackoverflow.com' + endpoint +'">여기를 클릭하세요</a></p>'
        content += '<br>'
        content += '<p>출처 : http:www.stackoverflow.com' + endpoint + '</p>'
        print(title)
        if blog_platform =="blogger":
            url = url_list[1]
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
            if result.status_code == 200:
                print(result)
                time.sleep(20)
            else:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                time.sleep(20)
                continue
        elif blog_platform == "tistory":
            header = {
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
                }
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
            url = url_list[0]
            obj = config.configs['main']
            access_token = obj['access_token']
            blogName = obj['blog_name']
            result = requests.post(url, data=data, headers=header)
            if result.status_code == 200:
                print(result)
                print(result.text)
            else:
                print(result.reason)
                print(result.text)
                print(result.status_code)
                continue