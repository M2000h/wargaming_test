# Rock Paper Scissors
[![python](https://img.shields.io/badge/Python-3.9-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org) 

![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

[![python](https://github.com/pallets/flask-website/blob/master/flask_website/static/badges/powered-by-flask-s.png?raw=true)](https://flask.palletsprojects.com/en/3.0.x/) 

## Build
```docker build . -t wtest```

## Run
Run with open port:

```docker run -d --restart=always -p 5000:5000 --name wtest wtest```

Or via docker network:

```docker run -d --restart=always --network your_network --name wtest wtest```

## Tests

```pytest tests```
