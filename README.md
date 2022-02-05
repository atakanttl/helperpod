# Helperpod

Helperpod is a CLI tool to run a Kubernetes utility pod with pre-installed tools that can be used for debugging/testing purposes inside a Kubernetes cluster.

## Pre-requisites

- Docker (For building and pushing the image)
- kubectl (Or the kubeconfig file either located in default `~/.kube/config` path, or an environment variable named `KUBECONFIG` pointed to a specific config file path)

## Usage

- Install the required libraries

```bash
python3 -m pip install --user -r requirements.txt
```

- Configure container registry information, this can be either done via manually editing the `config.json` file or via the CLI itself.

```bash
# Initialize the configuration file with default values
./helperpod.py config init

# Set the container registry username at minimum for proper configuration
# You should be logged with this user via `docker login` before pushing the image to the registry
./helperpod.py config set username <USERNAME>

# Set the container registry, e.g. "docker.io", "quay.io"
./helperpod.py config set registry <REGISTRY_NAME>

# Set the container image repository 
./helperpod.py config set repository <REPOSITORY_NAME>

# Set the image tag
./helperpod.py config set tag <TAG_NAME>

# Show the current configurations
./helperpod.py config show
```

- Build the container image (requires Docker engine to be running)

```bash
./helperpod.py build
```

- Push the container image to container registry (requires Docker engine to be running)

```bash
# Image will be pushed to <REGISTRY_NAME>/<USERNAME>/<REPOSITORY_NAME>:<TAG_NAME>
# e.g. docker.io/atakantatli/helperpod:vanilla
./helperpod.py push
```

- Run the helperpod inside Kubernetes

```bash
# Defaults to current namespace
./helperpod.py run

# Run in another namespace
./helperpod.py --namespace <NAMESPACE>

# Shorthand:
./helperpod.py -n <NAMESPACE>
```

- Delete the helperpod

```bash
# Defaults to current namespace
./helperpod rm

# Delete from another namespace
./helperpod rm --namespace <NAMESPACE>
```
