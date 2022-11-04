import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime
import time
import yaml 
import argparse
import json
import dateutil.parser

seedURL = 'https://aws.amazon.com/ko/blogs/korea'

with open('./conf.yaml', 'r') as f: 
    config = yaml.load(f)

es = Elasticsearch( [config['amazon_es_host']],
    http_auth=(config['user_id'], config['password']),
    scheme="https",
    port=443
)

indexName = config['index']
file = config['archive_file_name_ko']

f = open(file, 'w')


def parse(url, doArchive): 
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
    
    isoPostingTime = article.find('footer').find('time')['datetime']
    print('time : ' + isoPostingTime)
  
    category = ''
    categoryList = []
    try : 
      category_spans = article.find('footer').find('span', {"class", "blog-post-categories"}).find_all('a')
      print(len(category_spans))
      
      categoryList = list(map(lambda x : "'" + x.find('span').get_text() + "'", category_spans))
      print(categoryList)
      category = ','.join(categoryList)
      print('category : ' + category)
    except(AttributeError) as e : 
      pass


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
    
    index = {
      "index" : {
        "_index" : indexName,
        "_id" : doc['title']
      }
    }
    
    print(doc)

    if doArchive : 
      f.write(json.dumps(index) + "\n")
      f.write(json.dumps(doc) + "\n")
    else : 
      res = es.index(index='aws-blog', body=doc, id=title)
      print(res)


parser = argparse.ArgumentParser()
parser.add_argument("--archive", help="archive blog data to file", action="store_true")
args = parser.parse_args()

pageMax = 200

for pageNum in range(1,pageMax): 
  if pageNum < 2 :  
    parse(seedURL, args.archive)
  else : 
    parse(seedURL + '/page/' + str(pageNum), args.archive)
  time.sleep(0.1)
  
f.close()
