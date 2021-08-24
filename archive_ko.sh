#!/bin/bash

pip install -r requirements.txt

python /home/ec2-user/environment/aws-blog-crawler/scripts/aws-crawler-ko.py --archive

gzip -f blog-articles-ko.txt