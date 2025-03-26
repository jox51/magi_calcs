Running this app

poetry run uvicorn api:app --reload

kill python process in case of long running api call

pkill -9 -f python
