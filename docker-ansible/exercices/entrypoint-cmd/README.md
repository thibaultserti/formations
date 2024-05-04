# ENTRYPOINT

```bash
docker build -t entrypoint-demo:entrypoint .
docker run entrypoint-demo:entrypoint
docker run entrypoint-demo:entrypoint -alh
```

# CMD

```bash
docker build -t entrypoint-demo:cmd .
docker run entrypoint-demo:cmd
docker run entrypoint-demo:cmd -alh
```

# ENTRYPOINT + CMD

```bash
docker build -t entrypoint-demo:entrypoint-cmd .
docker run entrypoint-demo:entrypoint-cmd
docker run entrypoint-demo:entrypoint-cmd -p --full-time
```