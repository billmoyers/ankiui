# anki #

 collection of utilities for Anki.

## anki-webapp ##

A python tornado based webapp. The @Dockerfile@ currently just builds a tornado image. To deploy the full webapp:

```
cd webapp/
docker build . -t $MYNAME/tornado
docker run -it --rm \
	-v "$(pwd)":/app \
	-w /app \
	-p 8080:8080 \
	--env ANKI_DECK_PATH=/app/data/$MY_ANKI_COLLECTION \
	--env TORNADO_PORT=8080 $MYNAME/tornado \
	/usr/bin/python3 __init__.py
```
