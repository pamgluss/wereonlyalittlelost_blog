# We're Only A Little Lost

Pam's travel blog which used to live here: [link](https://wereonlyalittlelost.tumblr.com/)

Now lives here: [link](http://wereonlyalittlelost.com/)

Hugo is written in Go and converts markdown into HTML pages. I'm using TravisCI to automatically deploy code to S3 which is set up to be a static website.

# How to Run

1. Install hugo with `brew install hugo`
2. Create a new blog post with `hugo new content/trips/<place>/<post>.md`
3. Run `hugo server` and you'll get a message like `Web Server is available at http://localhost:1313/`
4. Open the localhost url to view the new post
