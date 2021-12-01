#!/bin/bash
set -e
echo "*** Starting build script ***"
echo "*** Verifying Hugo! ***"
hugo version

echo "*** Installing AWS CLI ***"
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q awscliv2.zip
sudo ./aws/install

aws --version

echo "*** Building site with Hugo! ***"
hugo

echo "*** Copying Hugo artifacts to AWS S3! ***"
aws s3 sync ./public s3://wereonlyalittlelost.com --acl public-read

echo "*** Checking to see if I've created a new blog post... ***"

DIFF=$(git diff HEAD~1..HEAD --name-only)

# To post to social media we expect a) a valid md file (a trip post)
# and b) no exclude keyword in the commit message
if [[ "$DIFF" == *".md"* ]] && [[ "${TRAVIS_COMMIT_MESSAGE}" != *"exclude"* ]]; 
then
    echo "*** Installing pyTumblr and gitPython ***"
    pip install pytumblr
    pip install gitpython
    
    echo "*** Posting to Slack, Discord and Tumblr... ***"
    python social-media.py
else
    echo "** Skipping posting to social media! ***"
fi

echo "*** Build script complete ***"
