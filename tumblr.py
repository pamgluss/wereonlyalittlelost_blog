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
        tags=["pictures", "adventure", sys.argv[1]],
        format="markdown",
        data=[selected_image],
        caption='## Blog Posted '+datetime.today().strftime('%m-%d-%Y') + '\n' + sys.argv[1]
    )
    print('Uploaded ' + selected_image)
else:
    client.create_link(
        'wereonlyalittlelost', 
        state="published", 
        title='Blog Posted '+datetime.today().strftime('%m-%d-%Y'), 
        url='http://wereonlyalittlelost.com/',
        description=sys.argv[1]
    )
    print('Uploaded a link')



