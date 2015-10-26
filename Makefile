ZIPFILE := $(PWD)/dist/rssreader.zip

push: $(ZIPFILE)
	aws s3 cp dist/rssreader.zip s3://johanwiren-lambda/rssfeedkindle/

$(ZIPFILE): rssreader.py dist virtualenv
	rm -f dist/rssreader.zip
	zip dist/rssreader.zip rssreader.py
	cd virtualenv/lib/python2.7/site-packages/; zip -r $(ZIPFILE) -r .

dist:
	mkdir dist

