import pytumblr
import sys
from datetime import datetime
import os
from git import Repo
import requests
import json
import re

# # for local testing
# from dotenv import load_dotenv
# from pathlib import Path  # Python 3.6+ only
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

BASE_URL = 'http://wereonlyalittlelost.com/'
UTM_STRING = '?utm_source='

# Get the recent changed images from the git commit
repo = Repo(os.getenv('TRAVIS_BUILD_DIR'))

diff = repo.git.diff('HEAD~1..HEAD', name_only=True)
split_lines = diff.splitlines()

# Link to the specific post instead of to the homepage
# So search for .md files and remove any from about/ or README
# then reformat the path to match what you'll see in prod
md_filtered_list = list(filter(lambda x: '.md' in x, split_lines))

for md in md_filtered_list:
    if ('about' in md or md == 'README.md'):
        md_filtered_list.remove(md)

# The run.sh script checks to make sure there's a change to .md but if we *only* change about/README, we should skip posting
if len(md_filtered_list) == 0:
    print('Did not find any md files besides About or README. Exiting early.')
    quit()

new_posts = []
for blog_post in md_filtered_list:
    url = blog_post.replace('content/', '')[0:-3] + "/" # url for linking to from Tumblr/Disc

    post_metadata = {
        "url": url,
        "tags": [],
        "title": "",
        "blog_content": "",
        "local_images": [],
        "r2_images": [],
        "has_images": False
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
        post_metadata['r2_images'] = r2_urls
        post_metadata['has_images'] = True
    elif len(local_image_paths) > 0:
        post_metadata['local_images'] = ['static' + path for path in local_image_paths]
        post_metadata['has_images'] = True

    new_posts.append(post_metadata)

# Connect to Tumblr Oath client
print('Connecting to Tumblr Oauth client')
client = pytumblr.TumblrRestClient(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    os.getenv('TUMBLR_CONSUMER_SECRET'),
    os.getenv('TUMBLR_TOKEN'),
    os.getenv('TUMBLR_TOKEN_SECRET'),
)

# Allows me to add multiple posts at once, i dunno why I thought this would be hard before
# TODO: pytumblr can only use 1 source image in the case of r2. If we want to attach multiple images again, 
# we'll need to download the images with fetch, then upload them
for post in new_posts:
    tumblr_url = f"{BASE_URL}{post['url']}{UTM_STRING}tumblr"

    if post['has_images']:
        post['tags'] += ['pictures', 'trip', 'travel', 'adventure', 'blog']

        if len(post['r2_images']) > 0:
            client.create_photo(
                'wereonlyalittlelost',
                state="published",
                tags=post['tags'],
                format="markdown",
                source=post['r2_images'][0],
                caption=f"## {post['title']} \n {post['blog_content'][:200]}... [Read more]({tumblr_url})"
            )
        else:
            client.create_photo(
                'wereonlyalittlelost',
                state="published",
                tags=post['tags'],
                format="markdown",
                data=post['local_images'][0:3],
                caption=f"## {post['title']} \n {post['blog_content'][:200]}... [Read more]({tumblr_url})"
            )

        print('Uploaded images to Tumblr')
    else:
        post['tags'] += ['journal', 'trip', 'travel', 'adventure', 'blog']
        client.create_link(
            'wereonlyalittlelost',
            state="published",
            title=post['title'],
            tags=post['tags'],
            url=tumblr_url,
            description=f"{post['blog_content'][:250]}..."
        )
        print('Uploaded a link to Tumblr')

    # Discord response can be 200-204
    data = {'content': f"{post['title']}:\n Read more at {BASE_URL}{post['url']}{UTM_STRING}discord"}
    rD = requests.post(os.getenv('DISCORD_WEBHOOK_URL'), data = data)
    print('Uploaded to Discord!')
