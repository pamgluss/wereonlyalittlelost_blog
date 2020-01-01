echo "*** Starting build script ***"

HUGO_RELEASE="hugo_0.55.6_Linux-64bit"
AWS_RELEASE="aws-cli-1.14.37"

echo "hugo dir will be /tmp/hugo/"$HUGO_RELEASE

echo "*** Copying hugo to tmp ***"
cp -R /var/task/hugo /tmp/

echo "*** Install hugo from tar.gz ***"
tar -xzf /tmp/hugo/$HUGO_RELEASE.tar.gz

echo "*** Verifying Hugo! ***"
./hugo version

echo "*** Installing AWS CLI ***"
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
unzip awscli-bundle.zip
sudo ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws

echo "*** Building site with Hugo! ***"
./hugo -server

echo "*** Copying Hugo artifacts to AWS S3! ***"
aws s3 sync ./public s3://wereonlyalittlelost.com

echo "*** Build script complete ***"
