# API Golang

Cette API utilise REDIS 6.


## Build

```bash
go mod download
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .
```

## Configuration
La variable d'environnement suivante est utilisée pour communiquer avec le conteneur REDIS

`REDIS_ADDR` : hostname et port de redis au format HOSTNAME:PORT
`PORT` : port d'écoute de l'API
`HELLO_MSG` : message de démarrage de l'API


## Run

```bash
./app
```
