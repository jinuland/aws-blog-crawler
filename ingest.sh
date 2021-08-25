#!/bin/bash
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}


eval $(parse_yaml /home/ec2-user/environment/aws-blog-crawler/conf.yaml)

gunzip -f $archive_file_name.gz

amazon_es_host=$(echo $amazon_es_host | sed -e 's/\/$//')
echo curl -u $user_id:$password -s -H "Content-Type: application/x-ndjson" -XPOST $amazon_es_host:443/_bulk --data-binary "@$archive_file_name"; echo
curl -u $user_id:$password -s -H "Content-Type: application/x-ndjson" -XPOST $amazon_es_host:443/_bulk --data-binary "@$archive_file_name"; echo
