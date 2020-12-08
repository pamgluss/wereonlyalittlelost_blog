import pytumblr
import sys
from datetime import datetime
import os
from git import Repo

# Get the recent changed images from the git commit
repo = Repo(os.getenv('TRAVIS_BUILD_DIR'))

diff = repo.git.diff('HEAD~1..HEAD', name_only=True)
split_lines = diff.splitlines()

filtered_list = list(filter(lambda x: '.jpg' in x, split_lines))

# Link to the specific post instead of to the homepage
# So search for .md files and remove any from about/ then reformat the path to match what you'll see in prod
# To Future Pam, if you're editing multiple .md files under trips at once...... good luck
md_filtered_list = filtered_list = list(filter(lambda x: '.md' in x, split_lines))

for md in md_filtered_list:
    if ('about' in md):
        md_filtered_list.remove(md)
url = md_filtered_list[0].replace('content/', '')[0:-3] + "/"

# Let's see if we can get the tags and some content out of the md too
f = open(md_filtered_list[0], 'r')
fileString = f.read()
start = fileString.find('tags:')
end = fileString.find('\n', start)
tags = fileString[start:end].replace('tags: ', '')

# Connect to Tumblr Oath cient
client = pytumblr.TumblrRestClient(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    os.getenv('TUMBLR_CONSUMER_SECRET'),
    os.getenv('TUMBLR_TOKEN'),
    os.getenv('TUMBLR_TOKEN_SECRET'),
)

if len(filtered_list) > 0:
    selected_image = filtered_list[0] 
    client.create_photo(
        'wereonlyalittlelost', 
        state="published",
        tags=tags,
        format="markdown",
        data=[selected_image],
        caption='## Blog Posted \n' + sys.argv[1] + url
    )
    print('Uploaded ' + selected_image)
else:
    client.create_link(
        'wereonlyalittlelost', 
        state="published", 
        title='Blog Posted '+datetime.today().strftime('%m-%d-%Y'), 
        url='http://wereonlyalittlelost.com/' + url,
        description=sys.argv[1] + url
    )
    print('Uploaded a link')

