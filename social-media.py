from requests_oauthlib import OAuth1Session
import sys
from datetime import datetime
import os
from git import Repo
import requests
import json
import re
import mimetypes

# # for local testing
# from dotenv import load_dotenv
# from pathlib import Path  # Python 3.6+ only
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

BASE_URL = 'http://wereonlyalittlelost.com/'
UTM_STRING = '?utm_source='
TUMBLR_POSTS_URL = 'https://api.tumblr.com/v2/blog/wereonlyalittlelost/posts'

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

# Connect to Tumblr with OAuth 1.0a
print('Connecting to Tumblr Oauth client')
tumblr = OAuth1Session(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    client_secret=os.getenv('TUMBLR_CONSUMER_SECRET'),
    resource_owner_key=os.getenv('TUMBLR_TOKEN'),
    resource_owner_secret=os.getenv('TUMBLR_TOKEN_SECRET'),
)

# Allows me to add multiple posts at once, i dunno why I thought this would be hard before
# Posts are built from NPF blocks: https://www.tumblr.com/docs/npf
for post in new_posts:
    tumblr_url = f"{BASE_URL}{post['url']}{UTM_STRING}tumblr"
    content = []
    uploads = {} # local image files, keyed by the identifier used in their image block

    if post['has_images']:
        post['tags'] += ['pictures', 'trip', 'travel', 'adventure', 'blog']
        content.append({'type': 'text', 'subtype': 'heading1', 'text': post['title']})

        if len(post['r2_images']) > 0:
            # r2 images are already hosted so Tumblr can fetch them by url
            for image_url in post['r2_images'][0:3]:
                content.append({'type': 'image', 'media': [{'url': image_url}]})
        else:
            # local images get uploaded alongside the post, matched up by identifier
            for i, image_path in enumerate(post['local_images'][0:3]):
                identifier = f"image-{i}"
                mime_type = mimetypes.guess_type(image_path)[0]
                content.append({'type': 'image', 'media': [{'type': mime_type, 'identifier': identifier}]})
                uploads[identifier] = (os.path.basename(image_path), open(image_path, 'rb'), mime_type)

        # Excerpt with "Read more" linked to the post. Formatting offsets are character positions in the text
        read_more = 'Read more'
        text = f"{post['blog_content'][:200].strip()}... {read_more}"
        content.append({
            'type': 'text',
            'text': text,
            'formatting': [{'start': len(text) - len(read_more), 'end': len(text), 'type': 'link', 'url': tumblr_url}]
        })
    else:
        post['tags'] += ['journal', 'trip', 'travel', 'adventure', 'blog']
        content.append({
            'type': 'link',
            'url': tumblr_url,
            'title': post['title'],
            'description': f"{post['blog_content'][:250].strip()}..."
        })

    # NPF wants tags as a comma separated string instead of an array
    body = {'content': content, 'state': 'published', 'tags': ','.join(post['tags'])}

    if len(uploads) > 0:
        # multipart: the post itself goes in a part named `json`, followed by one part per image
        tumblr_res = tumblr.post(TUMBLR_POSTS_URL, files={'json': (None, json.dumps(body), 'application/json'), **uploads})
    else:
        tumblr_res = tumblr.post(TUMBLR_POSTS_URL, json=body)

    if tumblr_res.status_code == 201:
        print('Uploaded images to Tumblr' if post['has_images'] else 'Uploaded a link to Tumblr')
    else:
        print(f"Tumblr upload failed: {tumblr_res.status_code} {tumblr_res.text}")

    # Discord response can be 200-204
    data = {'content': f"{post['title']}:\n Read more at {BASE_URL}{post['url']}{UTM_STRING}discord"}
    rD = requests.post(os.getenv('DISCORD_WEBHOOK_URL'), data = data)
    print('Uploaded to Discord!')
