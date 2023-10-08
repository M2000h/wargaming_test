docker build . -t wtest

docker run -d --restart=always -p 5000:5000 --name wtest wtest

docker run -d --restart=always --network main_network --name wtest wtest