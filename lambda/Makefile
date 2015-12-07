ZIPFILE := $(PWD)/dist/rssreader.zip
STACK_NAME := rssfeedkindle
S3_BUCKET := johanwiren-lambda
S3_KEY := $(STACK_NAME)/rssreader.zip
LAMBDA_FUNCTION_NAME = $(shell aws cloudformation list-stack-resources --stack-name $(STACK_NAME) | jq '.StackResourceSummaries[] | select(.LogicalResourceId == "lambdaFunction").PhysicalResourceId')
DYNAMODB_TABLE_NAME = $(shell aws cloudformation list-stack-resources --stack-name $(STACK_NAME) | jq '.StackResourceSummaries[] | select(.LogicalResourceId == "dynamoDbTable").PhysicalResourceId')

.PHONY: all s3push lambda cf
all: .semaphores s3push cf lambda
s3push: .semaphores/s3push
lambda: .semaphores/lambda
cf: .semaphores/cf
virtualenv: virtualenv/lib/python2.7/site-packages

.semaphores:
	mkdir $@

awsresources.py:
	echo dynamodb_table = \"$(DYNAMODB_TABLE_NAME)\" > $@

virtualenv/bin/pip:
	virtualenv virtualenv

virtualenv/lib/python2.7/site-packages: virtualenv/bin/pip requirements.txt
	virtualenv/bin/pip install -r requirements.txt --upgrade

$(ZIPFILE): rssreader.py awsresources.py dist virtualenv requirements.txt
	rm -f dist/rssreader.zip
	zip dist/rssreader.zip rssreader.py awsresources.py
	cd virtualenv/lib/python2.7/site-packages/; zip -r $(ZIPFILE) -r .

.semaphores/lambda: .semaphores/s3push
	aws lambda update-function-code --s3-bucket $(S3_BUCKET) --s3-key $(S3_KEY) --function-name $(LAMBDA_FUNCTION_NAME)
	touch $@

.semaphores/s3push: $(ZIPFILE)
	aws s3 cp dist/rssreader.zip s3://johanwiren-lambda/rssfeedkindle/
	touch $@

dist:
	mkdir dist

.semaphores/cf: cf/template.json
	aws cloudformation update-stack --stack-name rssfeedkindle --template-body file://./cf/template.json --capabilities CAPABILITY_IAM --region eu-west-1
	touch $@
