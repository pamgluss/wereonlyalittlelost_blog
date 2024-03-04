# We're Only A Little Lost

Pam's travel blog which used to live here: [link](https://wereonlyalittlelost.tumblr.com/)

Now lives here: [link](http://wereonlyalittlelost.com/)

Hugo is written in Go and converts markdown into HTML pages. I'm using Github Actions to automatically deploy the static build to Github Pages.

## Setup

1. Install brew
2. Install python `brew install python`
3. Install pytumblr and gitpython with pip

## How to Run

1. Install hugo with `brew install hugo`
2. Create a new blog post with `hugo new content/trips/<place>/<post>.md`
3. Run `hugo server` and you'll get a message like `Web Server is available at http://localhost:1313/`
4. Open the localhost url to view the new post

## Contributing

Please don't! But since this is a standard README I will include instructions anyways.

Each trip folder must have an \_index.html file for it to appear on the site. If you are adding to a location that already has a trip, simply create a new md in that folder. `hugo new` will generate the title and date for you.

Anatomy of a blog post:

1. Title: Self explanatory. Required.
2. Date: Also self explanatory. If you want posts to show up in the correct order you'll need to use the correct date format.
3. Tags: These are used both on the website for categorizing posts, but also used when the post is uploaded to Tumblr.
4. Difficulty & Rating: There is some simple logic to show the difficulty and rating in the list view of a trip. These are optional however since they mainly apply to hiking.
5. Draft: Standard hugo param. If true, the blog post will not display on the live site.

Content - go hog wild on content. So far I haven't found a better way to get pictures than putting them in static/ but that's a project I plan to tackle.

As of writing, you cannot update multiple trip md files at once without causing unwanted effects during the social media posting. Use the word `exclude` in your commit message to skip social-media.py.

## Testing

Manually test with `hugo server -D`. For more info see [hugo server](https://gohugo.io/commands/hugo_server/)

I may test social-media.py locally by uncommenting out the lines regarding dotenv and having a .env file locally with the required variables. Run with `python3 social-media.py`
