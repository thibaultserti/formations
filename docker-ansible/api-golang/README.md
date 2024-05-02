# API Golang

Cette API utilise REDIS 6.


## Build

```bash
go build main.go
```

## Configuration
La variable d'environnement suivante est utilisée pour communiquer avec le conteneur REDIS

`REDIS_ADDR` : hostname et portde redis au format HOSTNAME:PORT

## Run

```bash
./api-golang
```
