from django.shortcuts import render, redirect
from blog.models import *
from django.views import View

class MainView(View):
    def get(self, request):
        code = request.GET.get("code", None)

        if code is not None:
            return redirect(f'blog/blogger?code={code}')
        questions   = Question.objects.all()
        answers     = Answer.objects.all()
        tags        = Tag.objects.all()
        eng_post = questions.filter(original_title__isnull=False).count()
        kor_post = questions.filter(translated_title__isnull=False).count()
        tistory_ko = Standard.objects.get(blog_name="tistory").last_finish_ko
        tistory_en = Standard.objects.get(blog_name="tistory").last_finish_en
        blogger_ko = Standard.objects.get(blog_name="blogger").last_finish_ko
        blogger_en = Standard.objects.get(blog_name="blogger").last_finish_en

        data = {
            "total_available_post" : eng_post + kor_post,
            "tistory" : {
                "ko" : tistory_ko,
                "en" : tistory_en,
                "total" : tistory_en + tistory_ko
            },
            "blogger" : {
                "ko" : blogger_ko,
                "en" : blogger_en,
                "total" : blogger_ko + blogger_en
            },
            "total_posted" : tistory_en + tistory_ko + blogger_ko + blogger_en,
            "total_translated" : kor_post,
            "total_original" : eng_post,
            "total_endpoint" : questions.count(),
            "total_tag"   : tags.count(),
            "total_answer" : answers.count()
        }

        return render(request, 'index.html',{'data':data})