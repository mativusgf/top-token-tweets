from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd

def getTopTweets(tokens):
    url = "https://twitter-api47.p.rapidapi.com/v1/search"
    #конструктор запроса
    q = f"-filter:replies ({' OR '.join(tokens)})"
    querystring = {"q":q,"type":"Top"}

    headers = {
        "X-RapidAPI-Key": "d961a1a08bmsh6b594ca9f4d9c05p1b3c49jsn26e719668694",
        "X-RapidAPI-Host": "twitter-api47.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    tweets = []
    # пока есть следующий блок твитов - парсим
    while 'cursor' in response.json():
        for tweet in (response.json()['entries'][1:]):
            #пропускаем рекламный твит
            if 'tweet' in tweet['content']['itemContent']['tweet_results']['result']:
                continue
            else:
                tweetDate = tweet['content']['itemContent']['tweet_results']['result']['legacy']['created_at']
                countCom = tweet['content']['itemContent']['tweet_results']['result']['legacy']['reply_count']
                countRet = tweet['content']['itemContent']['tweet_results']['result']['legacy']['retweet_count']
                countLikes = tweet['content']['itemContent']['tweet_results']['result']['legacy']['favorite_count']
                countViews = tweet['content']['itemContent']['tweet_results']['result']['views']['count']

                author = tweet['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['screen_name']
                countFols = tweet['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['followers_count']
                created = tweet['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['created_at']
                countPosts = tweet['content']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy']['statuses_count']

                tweets.append((tweetDate, countCom, countRet, countLikes, countViews, author, countFols, created, countPosts))
        #параметры для следующего блока твитов
        cursor = response.json()['cursor']
        querystring = {"q": q, "type":"Top", "cursor": cursor}
        response = requests.get(url, headers=headers, params=querystring)
    return tweets[:30]

def getScore(driver, info):
    score = {}
    repeat = set()
    for item in info:
        #если для автора не был получен скор
        if item[5] not in repeat:
            repeat.add(item[5])
            #если скор есть
            try:
                url = f'https://twitterscore.io/twitter/{item[5]}/overview/'
                driver.get(url)
                value = driver.find_element(By.ID, "insideChartCount").text
                rate = driver.find_element(By.CLASS_NAME, "count-wrapper").find_element(By.TAG_NAME, 'p').text
                score[item[5]] = (rate, value)
            #если скора нет
            except:
                value = None
                rate = 'Terrible'
                score[item[5]] = (rate, value)
        else:
            continue

    return score


def fullInfo():
    tokens = ['$' + i.upper() for i in input().split()]
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    data = getTopTweets(tokens)
    scores = getScore(driver, data)
    #объединяем данные по твитам и скоры
    for i, tweet in enumerate(data):
        data[i] = tweet + scores[tweet[5]]
    return data

if __name__ == '__main__':
    d = fullInfo()
    df = pd.DataFrame(d, columns=['Дата создания твита:', 'Кол-во комментов:', 'Кол-во репостов:', 'Кол-во лайков:',
                                  'Кол-во просмотров:', 'Автор:', 'Подписчиков:', 'Акк создан:', 'Общ. кол-во постов:',
                                  'Оценка:', 'Score:'])
    df.to_csv('data.csv')






