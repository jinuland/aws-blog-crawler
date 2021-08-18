import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime
import time
import yaml 

seedURL = 'https://aws.amazon.com/blogs/aws'

with open('./conf.yaml', 'r') as f: 
    config = yaml.load(f)

es = Elasticsearch( [config['amazon_es_host']],
    http_auth=(config['user_id'], config['password']),
    scheme="https",
    port=443
)


def parse(url) : 
  print('try fetch : ' + url)
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  articles = soup.find_all('article')
  for article in articles:

    title = article.find('h2').get_text()
    print('title is : ' +  title)
    
    url = article.find('h2').find('a')['href']
    print("url is : " + url)

    author = article.find('footer').find('span', {"property" : "author"}).get_text()
    print('author : ' + author)
    postingTime = article.find('footer').find('time').get_text()
    isoPostingTime = datetime.strptime(postingTime, '%d %b %Y').isoformat()
    print('time : ' + isoPostingTime)
  
    category_spans = article.find('footer').find('span', {"class", "blog-post-categories"}).find_all('a')
    print(len(category_spans))
    categoryList = map(lambda x : "'" + x.find('span').get_text() + "'", category_spans)
    category = ','.join(categoryList)
    print('category : ' + category)

    body = article.find('section').get_text()
    print('body : ' + body) 
    
    doc = { 
      'title': title,
      'author': author,
      'date': isoPostingTime,
      'category': categoryList,
      'body': body,
      'url' : url
        # TODO: write code...
    }
    
    print(doc)

    res = es.index(index='aws-blog', body=doc, id=title)
    print(res)


pageMax = 100

for pageNum in range(1,pageMax): 
  if pageNum < 2 :  
    parse(seedURL)
  else : 
    parse(seedURL + '/page/' + str(pageNum))
  time.sleep(10)
