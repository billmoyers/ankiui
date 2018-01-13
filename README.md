# ankiui #

A collection of utilities for Anki.

## anki-webapp ##

A python tornado based webapp. The `Dockerfile` currently just builds a tornado image. To deploy the full webapp:

1. Copy your anki collection to the `data/` dir.
2. Run the following commands to generate and deploy for development via docker, subtituting where appropriate.
```
cd webapp/
docker build . -t $MYNAME/tornado
docker run -it --rm \
	-v "$(pwd)":/app \
	-w /app \
	-p 8080:8080 \
	--env ANKI_DECK_PATH=/app/data/$MY_ANKI_COLLECTION \
	--env TORNADO_PORT=8080 \
	--env ANKI_WEBAPP_THEME=basic \
	$MYNAME/tornado \
	/usr/bin/python3 __init__.py
```
