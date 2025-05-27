docker build -t trend:latest .

docker run -d -p 3030:3030 --name trend-container trend:latest
