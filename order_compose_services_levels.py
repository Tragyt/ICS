#!/usr/bin/env python3

import yaml
import argparse

from pathlib import Path
from collections import OrderedDict

class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

properties_order = ["version", "name", "include",
                    "services", "networks", "volumes", "secrets", "configs"]
fields_order = ["image", "build", "container_name", "depends_on", "volumes", "volumes_from", "configs", "secrets", "environment", "env_file", "ports", "networks",
                "network_mode", "extra_hosts", "command", "entrypoint", "working_dir", "restart", "healthcheck", "logging", "labels", "user", "isolation", "pull_policy","cap_add", "dns"]


def sort_properties(e: tuple):
    key = e[0]
    if key not in properties_order:
        return len(properties_order)
    return properties_order.index(e[0])


def sort_fileds(e: tuple):
    key = e[0]
    if key not in fields_order:
        return len(fields_order)
    return fields_order.index(e[0])


def sort_compose_file(file: Path):
    if not file.exists():
        print("file non trovato")
        return

    with file.open("r") as f:
        data = yaml.safe_load(f)
    data = (dict)(OrderedDict(sorted(data.items(), key=sort_properties)))

    for service in data["services"]:
        services = data["services"]
        data["services"] = (dict)(OrderedDict(
            sorted(services.items(), key=lambda item: item[0])))

        fields = data["services"][service]
        data["services"][service] = (dict)(OrderedDict(
            sorted(fields.items(), key=sort_fileds)))

    with file.open("w") as f:
        yaml.dump(data, f, sort_keys=False, Dumper=IndentDumper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort docker-compose services fields")
    parser.add_argument("file", help="docker-compose file path")
    args = parser.parse_args()

    sort_compose_file(Path(args.file))
