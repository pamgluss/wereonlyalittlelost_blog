import pytumblr
import sys
from datetime import datetime
import os

client = pytumblr.TumblrRestClient(
    os.getenv('TUMBLR_CONSUMER_KEY'),
    os.getenv('TUMBLR_CONSUMER_SECRET'),
    os.getenv('TUMBLR_TOKEN'),
    os.getenv('TUMBLR_TOKEN_SECRET'),
)

client.create_link(
    'wereonlyalittlelost', 
    state="published", 
    title='New Post '+datetime.today().strftime('%m-%d-%Y'), 
    url='http://wereonlyalittlelost.com/'
    description=sys.argv[1]
)
