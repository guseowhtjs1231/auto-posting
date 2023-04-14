from django.db import models
import datetime, pytz

class Question(models.Model):
    question_endpoint   = models.CharField(max_length=1000)
    original_question   = models.TextField(null=True)
    original_title      = models.CharField(max_length=200, null=True)
    translated_title    = models.CharField(max_length=200, null=True)
    translated_question = models.TextField(null=True)
    questioner          = models.CharField(max_length=50, null=True)
    asked_at            = models.DateTimeField(null=True)
    created_at          = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True, auto_now_add=False)
    
    class Meta:
        db_table = 'questions'

class Tag(models.Model):
    tag         = models.CharField(max_length=50)
    question    = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    created_at  = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'tags'

class Answer(models.Model):
    question            = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    answerer            = models.CharField(max_length=50, null=True)
    original_answer     = models.TextField(null=True)
    translated_answer   = models.TextField(null=True)
    created_at      = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'answers'

class Standard(models.Model):
    blog_name       = models.CharField(max_length=20)
    limit           = models.IntegerField()
    last_finish_ko  = models.IntegerField()
    last_finish_en  = models.IntegerField()
    today_did       = models.IntegerField()
    day_history     = models.DateTimeField(null=True, default=datetime.datetime(2021,10,4,12,12,12,200000,tzinfo=pytz.UTC))
    created_at      = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        db_table = 'standards'

class Configuration(models.Model):
    blog_type       = models.CharField(max_length=50)
    blog_name       = models.CharField(max_length=100, null=True)
    call_back_url   = models.URLField(null=True)
    url             = models.URLField(null=True)
    app_id          = models.CharField(max_length=200, null=True)
    blog_id         = models.CharField(max_length=100, null=True)
    secret_key      = models.CharField(max_length=200, null=True)
    client_secret   = models.CharField(max_length=200, null=True)
    token_type      = models.CharField(max_length=20, null=True)
    client_id       = models.CharField(max_length=100, null=True)
    access_token    = models.CharField(max_length=200, null=True)
    refresh_token   = models.CharField(max_length=200, null=True)
    api_key         = models.CharField(max_length=200, null=True)

    class Meta:
        db_table = 'configurations'

class Credential(models.Model):
    loginid = models.CharField(max_length=255)
    pw_value = models.CharField(max_length=255)
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'credentials'

