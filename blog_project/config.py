import requests, datetime
#from utils import Authenication

#a = Authenication()
#access_token = a.GetAccessToken()
    # 'w1231': {
    #     'blog_name': 'w1231',
    #     'access_token': "b550da77e9cdda1443c145984bd5bb63_863cba21ecfbd37ce5d49304235282e0",
    #     'url': "http://w1231.tistory.com",
    #     'app_id': "63e010c2651512925f0cfd172c6131d4",
    #     'secret_key': "63e010c2651512925f0cfd172c6131d42fcb73d3080737ba91cb9470ac99cd340a149e4d",
    # },

tistory = {
    'blog_name': 'guseowhtjs',
    'access_token': "c6f22f58a3dc2c98af11a402a916e117_84e59548c3374903f4588381ed281a93",
    'call_back_url': "http://guseowhtjs.tistory.com",
    'app_id': "fa57afdc25e4a1d151dae4641b6b34d1",
    'secret_key': "fa57afdc25e4a1d151dae4641b6b34d1293de6fc7d90bc2336c51e8827a9cf347de891c4"
}

blogger = {
    "api_key"   : "AIzaSyDJ8WkMsbsXRo2w1l-XX-fMeEAxvzv9VaQ",
    "url"       : "https://stackovertherainbow.blogspot.com",
    "blog_id"   : "6437626316895731650",
    "access_token" : "ya29.a0ARrdaM90GEWl1XGLk61_C3Ju0uRyX8MYIxKkWZ3gS-sTnmOGKx2ogjrqD4sz1sv0U9WnIkAkgtFLzBJoUvUkOCKTAsnVqfYYdcHbbaqQc-fPGtakW2Zct_QvD-68LnGD0dW1aDi0xETLqdH0VFxYedhcre3GgQ",
    "refresh_token" : "1//0diUMg8QMN1QaCgYIARAAGA0SNwF-L9IrsSwXc5LMGxyJamQdddaFwJbo-uwoH-ApjDPPe3xMeQUF32AOV4UAr0_x6u-aRqkU2Vw"
}

naver = {
    "client_id"     : "yxY8ZfqI3j8YQCu3zOKx",
    "client_secret" : "ZWKOQZhlcT",
    "redirect_url"  : "http://guseowhtjs.tistory.com",
    "access_token"  : "AAAAOmWvt_BhHeRtzKpDqrwcLN5ik_cNDKYwlUiY0UjW6zSRPFIioj5iwv4bUtl5degJbiApQpMv1CJO0bOovrwN1WM",
    "refresh_token" : "AWBs9zTT0CcrL86xbXcdNqhCcxUccxYishmCty5FnvnylYa6ndd9HisyrjUHyBUKTCjPv0KFW0Fzip4tHPmsEaKC9jtcFrZASfisTXbEqO0go6nkr18ledaipwipdm30DkaYI1",
    "token_type"    : "bearer"
}

def code_url_return():
    app_id = tistory['app_id']
    url    = tistory['url']
    get_code = f'https://www.tistory.com/oauth/authorize?client_id={app_id}&redirect_uri={url}&response_type=code'
    return get_code

def token_url_return(code):
    app_id = tistory['app_id']
    url    = tistory['url']
    secret_key = tistory['secret_key']
    get_access_token = f'https://www.tistory.com/oauth/access_token?client_id={app_id}&client_secret={secret_key}\
        &redirect_uri={url}\
            &code={code}\
                &grant_type=authorization_code'
    result = requests.get(get_access_token)
    access_token = result.text.split('=')[1]
    tistory['access_token'] = access_token

    print(result.text)
    return access_token

def html_decode(s):
    """
    Returns the ASCII decoded version of the given HTML string. This does
    NOT remove normal HTML tags like <p>.
    """
    htmlCodes = (
            ("'", '&#39;'),
            ('"', '&quot;'),
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('&', '&amp;')
        )
    for code in htmlCodes:
        s = s.replace(code[1], code[0])
    return s
code = '4/0AX4XfWhXO-3myFCESY0YfJqs7UmcpdVH27-ibSWSsMP0TQnw2jPeeWXSnTui_yIXMwfZRg'

def GoogleAccessToken():
    import json
    with open('./credentials.json','r') as f:
        json_data = json.load(f)
    credential  = json_data['web']
    client_id   = credential['client_id']
    auth_uri    = credential['auth_uri']
    client_secret = credential['client_secret']
    redirect_uri= 'https://stackovertherainbow.blogspot.com'
    scope       = 'https://www.googleapis.com/auth/blogger'
    data = {
        'client_id':client_id,
        'response_type':'code',
        'access_type':'offline',
        'include_granted_scopes':'true',
        'scope' : scope,
        'redirect_url':redirect_uri,
        'client_secret':client_secret
    }
    result = requests.post(url=auth_uri, data=data)
    print(result.status_code)
    print(result.reason)
    print(result.url)
    print(result.headers)
    print(result.cookies)

def GetCategoryList(blog):
    access_token = configs[blog]['access_token']
    blog_name = 'guseowhtjs'
    url = f"https://www.tistory.com/apis/category/list?access_token={access_token}&output=json&blogName={blog_name}"
    result = requests.get(url)
    print(result.text)

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    from google.cloud import translate_v2 as translate
    import six
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/youngbinha/Downloads/genuine-space-325914-7c3cda2f3c4f.json"
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)
    return result
    print(u"Text: {}".format(result["input"]))
    print(u"Translation: {}".format(result["translatedText"]))
    print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

def papago(target, text):
    import six
    client_id = naver["client_id"]
    client_secret = naver["client_secret"]
    url = "https://openapi.naver.com/v1/papago/n2mt"

    headers = {
        "X-Naver-Client-Id":client_id,
        "X-Naver-Client-Secret":client_secret,
        "User-Agent": "curl/7.49.1",
        "Accept" : "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Content-Length": "51"
        }
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    data = {
        "source":"en",
        "target":target,
        "text":text
    }
    result = requests.post(url,data=data, headers=headers)
    if result.status_code == 200:
        translated_text = result.json()["message"]["result"]["translatedText"]
        return translated_text
    else:
        print(result.text)
        return "Failed"
