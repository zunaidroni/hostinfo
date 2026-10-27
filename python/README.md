# hostinfo Python

A Python port of the hostinfo test application.

## Run and test

The server entry point is `hostinfo_server.py`. Start it on the default port
9898, or pass a different port as an argument:

```sh
python3 hostinfo_server.py
python3 hostinfo_server.py 8080
```

Run the offline unit tests from this directory with:

```sh
python3 -m unittest discover -v
```


## Build Instructions

A [Dockerfile](./Dockerfile) is included in this repo to create a container.


### Docker

Use `docker build` on the included Dockerfile with tag `docker.io/rxmllc/hostinfo/vN-python`.

For Multiarch:

Make sure you provide DockerHub credentials to your container engine with the `login` command.
- `sudo docker login': sudo docker login docker.io -u #<your username>`
- Install Buildx: `sudo apt install -y docker-buildx-plugin`
- Init Buildx: `sudo docker buildx create --use`
- Build multiarch: `sudo docker buildx build --sbom=true --provenance=true --no-cache --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -t docker.io/rxmllc/hostinfo:v1-python --push .`
  - If you intend to use `docker.io`, make sure you did the `docker login` command with `docker.io` as the target registry

An alternative Dockerfile is available if you prefer to install `python` in a bare Alpine container to further reduce bloat (and exclude things like `pip`). 

To build the alternative Dockerfile, invoke it during your build: `sudo docker buildx build -f Dockerfile-alpine --sbom=true --provenance=true --no-cache --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -t docker.io/rxmllc/hostinfo:python-alpine --push .`


### Podman

On Debian/Ubuntu using `podman`: 

`podman build --platform linux/arm/v7,linux/arm64/v8,linux/amd64 -t hostinfo:v1-python`