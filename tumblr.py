import pytumblr
import sys
from datetime import datetime

client = pytumblr.TumblrRestClient(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    os.getenv('TUMBLR_CONSUMER_SECRET'),
    os.getenv('TUMBLR_TOKEN'),
    os.getenv('TUMBLR_TOKEN_SECRET'),
)

client.create_text(
    'wereonlyalittlelost', 
    state="published", 
    slug="testing-text-posts", 
    title='New Post '+datetime.today().strftime('%m-%d-%Y'), 
    body=sys.argv[1]
)
