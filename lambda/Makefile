ZIPFILE := $(PWD)/dist/rssreader.zip

$(ZIPFILE): rssreader.py dist virtualenv requirements.txt
	rm -f dist/rssreader.zip
	zip dist/rssreader.zip rssreader.py
	cd virtualenv/lib/python2.7/site-packages/; zip -r $(ZIPFILE) -r .

push: $(ZIPFILE)
	aws s3 cp dist/rssreader.zip s3://johanwiren-lambda/rssfeedkindle/

dist:
	mkdir dist

