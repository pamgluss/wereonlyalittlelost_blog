#!/bin/bash
echo "*** Starting build script ***"

HUGO_RELEASE="hugo_0.55.6_Linux-64bit"
AWS_RELEASE="aws-cli-1.14.37"

echo "*** Install Linuxbrew ***"
sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"

test -d ~/.linuxbrew && eval $(~/.linuxbrew/bin/brew shellenv)
test -d /home/linuxbrew/.linuxbrew && eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)
test -r ~/.bash_profile && echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.bash_profile
echo "eval \$($(brew --prefix)/bin/brew shellenv)" >>~/.profile

echo "*** Install hugo from tar.gz ***"
brew install hugo

echo "*** Verifying Hugo! ***"
hugo version

echo "*** Installing AWS CLI ***"
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
unzip awscli-bundle.zip
sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

echo "*** Building site with Hugo! ***"
hugo

echo "*** Copying Hugo artifacts to AWS S3! ***"
aws s3 sync ./public s3://wereonlyalittlelost.com --acl public-read

echo "*** Posting to Slack and Discord...***"
curl -X POST -H 'Content-type: application/json' --data "{'text':'Pam has updated the site with the commit message: ${TRAVIS_COMMIT_MESSAGE}, go check it out! http://wereonlyalittlelost.com/'}" ${SLACK_WEBHOOK_URL}
curl -X POST -H 'Content-type: application/json' --data "{'text':'Pam has updated the site with the commit message: ${TRAVIS_COMMIT_MESSAGE}, go check it out! http://wereonlyalittlelost.com/'}" ${DISCORD_WEBHOOK_URL}

echo "*** Build script complete ***"
