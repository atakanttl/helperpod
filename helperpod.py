#!/usr/bin/env python3

"""CLI application to run a Kubernetes utility pod with pre-installed tools."""

import json
import os
import sys
import time

import fire
from docker import client as dockerclient
from kubernetes import client as kubeclient
from kubernetes import config as kubeconfig


def print_paths():
    """Print the file paths"""

    print("Script directory:", script_dir)
    print("Dockerfile path:", dockerfile_path)
    print("Config path:", configfile_path)


def build_image():
    """Build the helperpod image"""

    docker_client = dockerclient.from_env()

    for line in docker_client.api.build(
        path=script_dir,
        dockerfile=dockerfile_path,
        tag=IMAGE_NAME + ":" + IMAGE_VERSION,
        rm=True,
        decode=True,
        platform="linux/amd64",
    ):
        print(*line.values())


def push_image():
    """Push the helperpod image to the configured registry"""

    docker_client = dockerclient.from_env()
    image = docker_client.images.get(IMAGE_NAME + ":" + IMAGE_VERSION)
    image.tag(FULL_REPOSITORY, tag=IMAGE_VERSION)

    for line in docker_client.api.push(
        repository=FULL_REPOSITORY, tag=IMAGE_VERSION, stream=True, decode=True
    ):
        print(*line.values())


def config_init():
    """Initialize config.json with default values"""

    # Defaults
    init_conf = {}
    init_conf["registry"] = "docker.io"
    init_conf["username"] = ""
    init_conf["repository"] = "helperpod"
    init_conf["tag"] = "vanilla"

    with open(configfile_path, "w", encoding="utf-8") as init_configfile:
        json.dump(init_conf, init_configfile, indent=4)


def config_set_registry(registry: str):
    """Set the container registry"""

    conf["registry"] = registry

    with open(configfile_path, "w", encoding="utf-8") as new_configfile:
        json.dump(conf, new_configfile, indent=4)


def config_set_username(username: str):
    """Set the container registry username"""

    conf["username"] = username

    with open(configfile_path, "w", encoding="utf-8") as new_configfile:
        json.dump(conf, new_configfile, indent=4)


def config_set_repository(repository: str):
    """Set the image repository"""

    conf["repository"] = repository

    with open(configfile_path, "w", encoding="utf-8") as new_configfile:
        json.dump(conf, new_configfile, indent=4)


def config_set_tag(tag: str):
    """Set the image tag"""

    conf["tag"] = tag

    with open(configfile_path, "w", encoding="utf-8") as new_configfile:
        json.dump(conf, new_configfile, indent=4)


def config_get():
    """Load the current configuration"""

    with open(configfile_path, "r", encoding="utf-8") as configfile:
        config_contents = json.load(configfile)
    return config_contents


def config_show():
    """Show the current configuration"""

    print(json.dumps(config_get(), indent=4))


def kubernetes_run(namespace=None):
    """Run a Kubernetes pod using helperpod image"""

    kubeconfig.load_kube_config()
    k8s_apps_v1 = kubeclient.CoreV1Api()

    # Minikube connection might fail if set to "True"
    kubeclient.Configuration().assert_hostname = False

    if namespace is None:
        context = kubeconfig.list_kube_config_contexts()[1]["context"]
        try:
            namespace = context["namespace"]
        except KeyError:
            print(
                "Cannot fetch current namespace from kubeconfig. Switching to default namespace."
            )
            namespace = "default"

    resp = None
    try:
        resp = k8s_apps_v1.read_namespaced_pod(name=POD_NAME, namespace=namespace)
    except kubeclient.ApiException as err:
        if err.status != 404:
            print(f"Unknown error: {err}")
            sys.exit(1)

    if not resp:
        print(f"Pod {POD_NAME} does not exist. Creating it...")
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": POD_NAME},
            "spec": {
                "containers": [
                    {
                        "image": FULL_REPOSITORY + ":" + IMAGE_VERSION,
                        "name": POD_NAME,
                        "imagePullPolicy": "Always",
                    }
                ],
                "terminationGracePeriodSeconds": 0,
            },
        }
        resp = k8s_apps_v1.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        print(
            f"Pod created. Name: '{resp.metadata.name}', Status: '{resp.status.phase}'"
        )

        timeout_counter = 0
        while True:
            resp = k8s_apps_v1.read_namespaced_pod(name=POD_NAME, namespace=namespace)
            if resp.status.phase != "Pending":
                break
            time.sleep(1)
            if timeout_counter == 15:
                print("Timeout exceeded. Quitting.")
                sys.exit(1)
            timeout_counter += 1
        print(f"Done. Run `kubectl exec -it {POD_NAME} -- bash` to get inside the pod.")
    else:
        print(f"Pod {POD_NAME} exists. Nothing to do.")


def kubernetes_remove(namespace=None):
    """Remove the helperpod"""

    kubeconfig.load_kube_config()
    k8s_apps_v1 = kubeclient.CoreV1Api()

    # Minikube connection might fail if set to "True"
    kubeclient.Configuration().assert_hostname = False

    if namespace is None:
        context = kubeconfig.list_kube_config_contexts()[1]["context"]
        try:
            namespace = context["namespace"]
        except KeyError:
            print(
                "Cannot fetch current namespace from kubeconfig. Switching to default namespace."
            )
            namespace = "default"

    resp = None
    try:
        resp = k8s_apps_v1.read_namespaced_pod(name=POD_NAME, namespace=namespace)
    except kubeclient.ApiException as err:
        if err.status != 404:
            print(f"Unknown error: {err}")
            sys.exit(1)

    if resp:
        resp = k8s_apps_v1.delete_namespaced_pod(name=POD_NAME, namespace=namespace)
        print(f"Pod {POD_NAME} is deleted.")
    else:
        print(f"Pod {POD_NAME} does not exist. Nothing to do.")


script_dir = os.path.dirname(os.path.realpath(__file__))
dockerfile_path = os.path.join(script_dir, "Dockerfile")
configfile_path = os.path.join(script_dir, "config.json")

if not os.path.exists(configfile_path):
    print("config.json cannot be found. Initializing a new config file.")
    config_init()
    print("Current defaults:")
    config_show()
    print(
        "Run `helperpod config set username <USERNAME>` at minimum for proper configuration. "
        "Quitting."
    )
    sys.exit(0)


conf = config_get()

POD_NAME = "helperpod"
REGISTRY = conf["registry"]
USERNAME = conf["username"]
IMAGE_NAME = conf["repository"]
IMAGE_VERSION = conf["tag"]
FULL_REPOSITORY = REGISTRY + "/" + USERNAME + "/" + IMAGE_NAME


if __name__ == "__main__":
    fire.Fire(
        {
            "build": build_image,
            "push": push_image,
            "config": {
                "init": config_init,
                "set": {
                    "registry": config_set_registry,
                    "username": config_set_username,
                    "repository": config_set_repository,
                    "tag": config_set_tag,
                },
                "show": config_show,
            },
            "run": kubernetes_run,
            "rm": kubernetes_remove,
            "paths": print_paths,
        }
    )
