ZIPFILE := $(PWD)/dist/rssreader.zip
S3_BUCKET := "johanwiren-lambda"
S3_KEY := "rssfeedkindle/rssreader.zip"
LAMBDA_FUNCTION_NAME := "rssfeedkindle-lambdaFunction-8TIMDLIRJHA"

.PHONY: all s3push lambda cf
all: .semaphores s3push cf lambda
s3push: .semaphores/s3push
lambda: .semaphores/lambda
cf: .semaphores/cf

.semaphores:
	mkdir $@

$(ZIPFILE): rssreader.py dist virtualenv requirements.txt
	rm -f dist/rssreader.zip
	zip dist/rssreader.zip rssreader.py
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
