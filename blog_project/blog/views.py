from django.shortcuts import render, redirect
from blog.models import *
from django.views import View
from django.http import HttpResponse
import requests, upblog
import json, config, time
from asgiref.sync import sync_to_async
from urllib.parse import urlparse
from urllib.parse import parse_qs

class BloggerView(View):
    def get(self, request):
        code = request.GET.get('code', None)
        blog_config = Configuration.objects.get(blog_type="blogger")
        client_id = blog_config.client_id
        client_secret = blog_config.client_secret

        data = {
            'code' : code,
            'url'  : blog_config.url,
            "client_id"                 : client_id,
            "redirect_uri"              : "http://localhost:8080",
            "include_granted_scopes"    : 'true',
            "scope"                     : "https://www.googleapis.com/auth/blogger",
            "response_type"             : "code",
            "access_type"               : "offline",
            "external_url"              : blog_config.url,
        }

        if code is not None:
            get_access_token = f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&redirect_uri=http://localhost:8080&grant_type=authorization_code&code={code}"
            result = requests.post(get_access_token)
            access_token = result.json()["access_token"]
            blog_config.access_token = access_token
            blog_config.save()
            print(result.text)
            print(result.status_code)
            return redirect('/blog/blogger/upload')

        return render(request, 'blogger/getCode.html',{'data':data})
    def post(self, request):
        return redirect('/blog/blogger/upload')

class TistoryView(View):
    def get(self, request):
        blog_config = Configuration.objects.get(blog_type="tistory")
        data = {
            "blog_name"     : blog_config.blog_name,
            "call_back_url" : blog_config.call_back_url,
            "app_id"        : blog_config.app_id,
            "secret_key"    : blog_config.secret_key
        }

        return render(request, 'tistory/getCode.html',{'data':data})
    
    def post(self, request):
        from selenium import webdriver
        login_config = Configuration.objects.get(type="Kakao")
        
        app_id          = request.POST.get("client_id")
        redirect_uri    = request.POST.get("redirect_uri")
        print(app_id)
        print(redirect_uri)
        
        get_code_url = f'https://www.tistory.com/oauth/authorize?client_id={app_id}&redirect_uri={redirect_uri}&response_type=code'
        driver = webdriver.Chrome('./chromedriver')
        driver.implicitly_wait(2)
        driver.get(get_code_url)
        # button = driver.find_elements_by_css_selector('#contents > div.buttonWrap > button.confirm')
        # button.click()
        kakao_login_button = driver.find_element_by_css_selector('#cMain > div > div > div > a.btn_login.link_kakao_id')
        kakao_login_button.click()
        time.sleep(3)
        
        email = driver.find_element_by_css_selector('#loginKey--1')
        passwd = driver.find_element_by_css_selector('#password--2')
        
        email.send_keys(login_config.loginid)
        time.sleep(5)
        passwd.send_keys(login_config.pw_value)
        time.sleep(5)
        driver.find_element_by_css_selector('#mainContent > div > div > form > div.confirm_btn > button.btn_g.highlight.submit').click()
        #id_email_2
        #id_password_3
        #login-form > fieldset > div.item_tf.item_inp
        #loginEmailField > div
        time.sleep(10)
        driver.find_element_by_css_selector('#contents > div.buttonWrap > button.confirm').click()
        parsed_url = urlparse(driver.current_url)
        print(parsed_url)
        code = parse_qs(parsed_url.query)['code'][0]
        driver.quit()
        print(code)
        return redirect(f'/blog/tistory/token?code={code}')
        
class TistoryTokenView(View):
    def get(self, request):
        blog_config = Configuration.objects.get(blog_type='tistory')
        code = request.GET.get('code')
        data = {
            "blog_name"     : blog_config.blog_name,
            "call_back_url" : blog_config.call_back_url,
            "app_id"        : blog_config.app_id,
            "access_token"  : blog_config.access_token,
            "secret_key"    : blog_config.secret_key,
            "code"          : code
        }
        print(blog_config.call_back_url)
        return render(request, 'tistory/getToken.html',{'data':data})
    
    def post(self, request):
        if request.is_ajax():
            blog_config = Configuration.objects.get(blog_type="tistory")
            string = request.body.decode('utf-8')
            parse_str = string.split('=')
            code = parse_str[1].split("&")[0]
            app_id = blog_config.app_id
            secret_key = blog_config.secret_key
            url         = blog_config.call_back_url

            get_access_token = f'https://www.tistory.com/oauth/access_token?client_id={app_id}&client_secret={secret_key}\
                &redirect_uri={url}\
                &code={code}\
                &grant_type=authorization_code'
            result = requests.get(get_access_token)
            access_token = result.text.split('=')[1]
            print(access_token)
            return HttpResponse(access_token)
        else:
            return HttpResponse('FAILED')

class TistoryUploadView(View):
    def get(self, request):
        blog = 'tistory'
        access_token = request.GET.get("access_token")
        blog_config = Configuration.objects.get(blog_type=blog)
        blog_config.access_token = access_token
        blog_config.save()

        param = upblog.languageStartEnd(blog)
        lan     = param["lan"]
        start   = param["start"]
        end     = param["end"]
        print(param)
        data = {
            "language"   : lan,
            "start"      : start,
            "end"        : end
        }
        return render(request,'tistory/upload.html', { "data" : data })
        
    def post(self, request):
        blog = 'tistory'
        if not upblog.check_availablity(blog):
            return HttpResponse("HIT LIMIT")
        elif request.is_ajax():
            string = request.body.decode('utf-8')
            parse_str = string.split('=')
            start = parse_str[1].split("&")[0]
            end = parse_str[2].split("&")[0]
            lan = parse_str[3].split("&")[0]
            visibility = 3       # 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
            category = 1009236   # 카테고리 아이디 (기본값: 0)

            blog_config = Configuration.objects.get(blog_type=blog)
            url = blog_config.url
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
                        content += "<br><br>" + ("" if a.translated_answer == None else a.translated_answer ) + '<br><strong>' +  answerer + '</strong>'
                    
                    content += '<br><br><p>출처 : http:www.stackoverflow.com' + endpoint + '</p>'
                print(title)

                data = json.dumps({
                    "content":content,
                    "title":title,
                    "labels":tag_list,
                })
                
                access_token = blog_config.access_token
                blogName = blog_config.blog_name
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
                    return HttpResponse("FAILED")
                elif result.status_code == 403:
                    print(result.reason)
                    print(result.text)
                    print(result.status_code)
                    return HttpResponse("FAILED")
                else:
                    print(result.reason)
                    print(result.text)
                    print(result.status_code)
                    return HttpResponse("ELSE")
            return HttpResponse("SUCCESS")
        else:
            return HttpResponse("AJAX_FAILED")

class BloggerUploadView(View):
    def get(self, request):
        blog = 'blogger'
        if upblog.check_availablity(blog):
            param = upblog.languageStartEnd(blog)
            lan     = param["lan"]
            start   = param["start"]
            end     = param["end"]

            data = {
               "language"   : lan,
               "start"      : start,
               "end"        : end
            }
            return render(request,'blogger/upload.html', { "data" : data })

    def post(self, request):
        blog = 'blogger'
        if request.is_ajax():
            string = request.body.decode('utf-8')
            parse_str = string.split('=')
            start = parse_str[1].split("&")[0]
            end = parse_str[2].split("&")[0]
            lan = parse_str[3].split("&")[0]

            url = f'https://www.googleapis.com/blogger/v3/blogs/{config.blogger["blog_id"]}/posts?key={config.blogger["api_key"]}'
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
                data = json.dumps({
                    "content":content,
                    "title":title,
                    "labels":tag_list,
                })
                blog_config = Configuration.objects.get(blog_type=blog)
                google_access_token = blog_config.access_token
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
                result = requests.post(
                        url=url,
                        data=data,headers=headers)
                standard = Standard.objects.get(blog_name=blog)
                if result.status_code == 200:
                    print(result)
                    time.sleep(30)
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
                    return HttpResponse("FAILED")
                elif result.status_code == 403:
                    print(result.reason)
                    print(result.text)
                    print(result.status_code)
                    return HttpResponse("FAILED")
                else:
                    print(result.reason)
                    print(result.text)
                    print(result.status_code)
                    return HttpResponse("ELSE")
            return HttpResponse("SUCCESS")
        else:
            return HttpResponse("AJAX_FAILED")
