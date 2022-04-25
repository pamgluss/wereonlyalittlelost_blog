import pytumblr
import sys
from datetime import datetime
import os
from git import Repo
import requests
import json

# # for local testing
# from dotenv import load_dotenv
# from pathlib import Path  # Python 3.6+ only
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

BASE_URL = 'http://wereonlyalittlelost.com/'

# Get the recent changed images from the git commit
repo = Repo(os.getenv('TRAVIS_BUILD_DIR'))

diff = repo.git.diff('HEAD~1..HEAD', name_only=True)
split_lines = diff.splitlines()

# Link to the specific post instead of to the homepage
# So search for .md files and remove any from about/ or README
# then reformat the path to match what you'll see in prod
# To Future Pam, if you're editing multiple .md files under trips at once...... good luck
md_filtered_list = list(filter(lambda x: '.md' in x, split_lines))

for md in md_filtered_list:
    if ('about' in md or md == 'README.md'):
        md_filtered_list.remove(md)

# The run.sh script checks to make sure there's a change to .md but if we *only* change about/README, we should skip posting
if len(md_filtered_list) == 0:
    print('Did not find any md files besides About or README. Exiting early.')
    quit()

url = md_filtered_list[0].replace('content/', '')[0:-3] + "/"

# Let's see if we can get the tags and some content out of the md too
# We're currently doing idiotic things to remove unnecessary characters
f = open(md_filtered_list[0], 'r')
fileString = f.read()

start = fileString.find('tags:')
end = fileString.find('\n', start)
# First we take a slice of the fileString from tags to the line break which will look like `"tags: ['California','United States', 'Hiking', '2021 State Parks']"`
# We only want the array so we replace `tags: ` with nothing
# Tumblr accepts an array of strings for tags so we use eval to convert it from string
tags = eval(fileString[start:end].replace('tags: ', ''))

titleStart = fileString.find('title:')
titleEnd = fileString.find('\n', titleStart) - 1
title = fileString[titleStart:titleEnd].replace('title: "', '')

# Get the first paragraph-ish out of the blog content
contentSplit = fileString.split('---')
blogContent = contentSplit[2]

# Connect to Tumblr Oath client
print('Connecting to Tumblr Oauth client')
client = pytumblr.TumblrRestClient(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    os.getenv('TUMBLR_CONSUMER_SECRET'),
    os.getenv('TUMBLR_TOKEN'),
    os.getenv('TUMBLR_TOKEN_SECRET'),
)

img_filtered_list = list(filter(lambda x: ('.jpg' in x or '.png' in x), split_lines))

if len(img_filtered_list) > 0:
    selected_images = img_filtered_list[0:3]
    tags += ['pictures', 'trip', 'travel', 'adventure']
    client.create_photo(
        'wereonlyalittlelost', 
        state="published",
        tags=tags,
        format="markdown",
        data=selected_images,
        caption=f"## {title} \n {blogContent[:200]}... [Read more]({BASE_URL}{url})"
    )
    print('Uploaded images to Tumblr')
else:
    tags += ['journal', 'trip', 'travel', 'adventure']
    client.create_link(
        'wereonlyalittlelost', 
        state="published", 
        title=title,
        tags=tags,
        url=f"{BASE_URL}{url}",
        description=f"{blogContent[:250]}..."
    )
    print('Uploaded a link to Tumblr')

# Use python Request lib to upload data to Discord/Slack instead of a terminal cURL that depends on the commit message
slackData = json.dumps({ "text": f"{title}: Read more here http://wereonlyalittlelost.com/{url}" })
rS = requests.post(os.getenv('SLACK_WEBHOOK_URL'), data = slackData, headers={'Content-Type': 'application/json'})
if rS.text == "ok":
    print('Successfully uploaded to Slack!')
else:
    print('Something went wrong uploading to Slack')
    print(rS)

# Discord response can be 200-204
data = {'content': f"{title}:\n Read more at http://wereonlyalittlelost.com/{url}"}
rD = requests.post(os.getenv('DISCORD_WEBHOOK_URL'), data = data)
print('Uploaded to Discord!')
