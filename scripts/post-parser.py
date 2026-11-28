# Script to test the post parsing for social-media.py

import sys
import re

if(len(sys.argv) != 2):
  print("usage: python3 scripts/post-parser.py <path-to-post>")
  exit(1)

blog_post = sys.argv[1]

url = blog_post.replace('content/', '')[0:-3] + "/" # url for linking to from Tumblr/Disc

post_metadata = {
    "url": url,
    "tags": [],
    "title": "",
    "blog_content": "",
    "images": []
}
f = open(blog_post, 'r')
fileString = f.read()

# First we take a slice of the fileString from tags to the line break 
# which will look like `"tags: ['California','United States', 'Hiking', '2021 State Parks']"`
start = fileString.find('tags:')
end = fileString.find('\n', start)

# We only want the array so we replace `tags: ` with nothing
# Tumblr accepts an array of strings for tags so we use eval to convert it from string
tags = eval(fileString[start:end].replace('tags: ', ''))
post_metadata['tags'] = tags

titleStart = fileString.find('title:')
titleEnd = fileString.find('\n', titleStart) - 1
title = fileString[titleStart:titleEnd].replace('title: "', '')
post_metadata['title'] = title

# Get the first paragraph-ish out of the blog content
contentSplit = fileString.split('---')
blogContent = contentSplit[2]
post_metadata['blog_content'] = blogContent

# Get images from post: this can either be a static, local image (less likely)
# or an image already uploaded to r2 by the app (hopefully more likely)
# e.g. `![IMG_4366](https://pub-<hash>.r2.dev/images/IMG_4366.png)`
# google says client.create_photo will accept `source="https://r2.dev"``
r2_urls = re.findall(r"https://pub-[a-z0-9]+\.r2\.dev/[^\s)\"']+", blogContent)

# e.g. `![omakase](/images/new_york/omakase.png)` - captures just the path inside the parens
local_image_paths = re.findall(r"!\[[^\]]*\]\((/images/[^\s)]+)\)", blogContent)

if len(r2_urls) > 0:
    post_metadata['images'] = r2_urls
elif len(local_image_paths) > 0:
  post_metadata['images'] = local_image_paths

print(post_metadata)