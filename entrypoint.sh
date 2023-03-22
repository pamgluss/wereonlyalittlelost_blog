#!/bin/bash
set -e
echo "*** Starting build script ***"

echo "*** Checking to see if I've created a new blog post... ***"

DIFF=$(git diff HEAD~1..HEAD --name-only)

# To post to social media we expect a) a valid md file (a trip post)
# and b) no exclude keyword in the commit message
if [[ "$DIFF" == *".md"* ]] && [[ "${COMMIT_MESSAGE}" != *"exclude"* ]]; 
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
