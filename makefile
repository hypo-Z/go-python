package:
	pip install requests --target resources/core/site-packages/

offline:
    pip download -r resources/core/requirements.txt -d ./resources/core/site-packages --platform win_amd64 --python-version 3.11 --only-binary :all:

build:
	go build -o myapp.exe
