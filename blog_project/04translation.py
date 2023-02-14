from utils import Authentication as auth

from config import *

target_language = 'ko'
questions = Question.objects.all()

for idx ,question in enumerate(questions[824:]):
    eng_question = question.original_question
    eng_title    = question.original_title

    kor_question = auth.translate_text(target_language, eng_question)
    kor_title    = auth.translate_text(target_language, eng_title)
    
    question.translated_question    = kor_question["translatedText"]
    question.translated_title       = html_decode(kor_title["translatedText"])
    print(idx)
    print(question.translated_title)
    question.save()

    answers = question.answer_set.all()
    count = 0
    for answer in answers:
        eng_answer = answer.original_answer
        kor_answer = auth.translate_text(target_language, eng_answer)

        answer.translated_answer = kor_answer["translatedText"]
        answer.save()
        count+=1
    print(str(count) + ' Answer done ' )
    tags = question.tag_set.all()
    count = 0
    for tag in tags:
        eng_tag = tag.tag
        kor_tag = auth.translate_text(target_language, eng_tag)
        Tag.objects.create(question=question, tag=kor_tag["translatedText"])
        count+=1
    print(str(count) + ' Tag done')
    print(str(idx) + "번째 끝 ")