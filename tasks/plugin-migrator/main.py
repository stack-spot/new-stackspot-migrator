import os
import shutil
import sys
from enum import Enum

from ruamel.yaml import YAML


class YamlName(Enum):
    TEMPLATE = "template"
    PLUGIN = "plugin"


yaml = YAML()
yaml.preserve_quotes = True


def __get_repository_url(plugin_folder_path):
    config_file_path = plugin_folder_path + os.sep + ".git" + os.sep + "config"
    repo_url = ""
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as input_stream:
            config_file_content = input_stream.readlines()
            for __line in config_file_content:
                if "url" in __line:
                    repo_url = str(__line).split("=", 1)[1].strip()
                    print("Plugin repository found: " + repo_url)

    return repo_url


def __get_yaml_content_from_file(yaml_file_path):
    with open(yaml_file_path, "r") as stream:
        content = yaml.load(stream.read())
    return content


def __write_yaml_content_to_file(yaml_dict, yaml_file_path, sort_keys=False):
    with open(yaml_file_path, "w") as stream:
        yaml.dump(yaml_dict, stream)


# Moves a whole node-value from __old_yaml to the spec node of __new_yaml
def __move_to_spec_node(__old_yaml, __new_yaml, property_name):
    if __old_yaml.get(property_name) is not None:
        __new_yaml["spec"][property_name] = __old_yaml.pop(property_name)


def __is_plugin_folder(folder_path):
    return os.path.exists(folder_path + os.sep + "plugin.yaml")


def __is_template_folder(folder_path):
    return os.path.exists(folder_path + os.sep + "template.yaml")


def __get_yaml_name(folder_path):
    if __is_plugin_folder(folder_path):
        return YamlName.PLUGIN.value
    elif __is_template_folder(folder_path):
        return YamlName.TEMPLATE.value
    else:
        raise Exception(f"No plugin or template files were found in path {folder_path}")


def __get_display_name(yaml_dic):
    __display_name = "display-name"
    if yaml_dic.get(__display_name) is not None:
        return yaml_dic.pop(__display_name)
    __display_name = "displayName"
    if yaml_dic.get(__display_name) is not None:
        return yaml_dic.pop(__display_name)
    return None


def __get_about_node_value(__current_yaml):
    return __current_yaml.pop("about") if __current_yaml.get("about") is not None else "docs/about.md"


def __get_implementation_node_value(__current_yaml):
    return __current_yaml.pop("implementation") if __current_yaml.get(
        "implementation") is not None else "docs/implementation.md"


def __get_usage_node_value(__current_yaml):
    return __current_yaml.pop("usage") if __current_yaml.get(
        "usage") is not None else "docs/usage.md"


def __get_technologies_node_value(__current_yaml):
    return __current_yaml.pop("technologies") if __current_yaml.get(
        "technologies") is not None else ["Api"]


def __get_compatibility_node_value(__current_yaml):
    return __current_yaml.pop("compatibility") if __current_yaml.get(
        "compatibility") is not None else ["python"]


def __get_picture_node_value(__current_yaml):
    return __current_yaml.pop("picture") if __current_yaml.get(
        "picture") is not None else "picture.png"


def convert_to_new_plugin(resource_folder_path):
    yaml_name = __get_yaml_name(resource_folder_path)

    print(f"## A {yaml_name} was detected. Starting migration to the new plugin format...")

    resource_old_yaml_path = resource_folder_path + os.sep + yaml_name + "_old.yaml"
    if os.path.exists(resource_old_yaml_path):
        raise Exception(
            f"Resource already migrated. If you want to rerun the migration process, delete file {yaml_name}.yaml and "
            f"rename {yaml_name}_old.yaml to {yaml_name}.yaml.")

    current_yaml_file_path = resource_folder_path + os.sep + yaml_name + ".yaml"
    current_yaml = __get_yaml_content_from_file(current_yaml_file_path)

    __name_node_value = current_yaml.pop("name")
    if "_" in __name_node_value:
        print("Warning: underscore chars '_' will be replace to '-'")
        __name_node_value = str(__name_node_value).replace("_", "-")

    __display_name_node_value = __get_display_name(current_yaml)
    if __display_name_node_value is None:
        print("Nodes display-name and displayName not found. Using node name...")
        __display_name_node_value = __name_node_value

    # base structure (https://newdocs.stackspot.com/platform-content/studio/plugin/create-plugin/)
    new_yaml = {
        "kind": "plugin",
        "schema-version": "v1",
        "spec": {
            "about": f"{__get_about_node_value(current_yaml)}",
            "requirements": "docs/requirements.md",
            "implementation": f"{__get_implementation_node_value(current_yaml)}",
            "type": "app",
            "release-notes": "docs/release-notes-0.0.1.md",
            "usage": f"{__get_usage_node_value(current_yaml)}",
            "technologies": __get_technologies_node_value(current_yaml),
            "compatibility": __get_compatibility_node_value(current_yaml)
        },
        "metadata": {
            "picture": f"{__get_picture_node_value(current_yaml)}",
            "display-name": f"{__display_name_node_value}",
            "version": "0.0.1",
            "name": f"{__name_node_value}",
            "description": current_yaml.pop("description")
        }
    }

    repository_url = __get_repository_url(resource_folder_path)
    if repository_url is not None and repository_url:
        new_yaml["spec"]["repository"] = repository_url

    # Key 'requirements' now is 'spec.requires'
    if current_yaml.get("requirements") is not None:
        plugin_yaml_part = {"plugin": current_yaml.pop("requirements")}
        new_yaml["spec"]["requires"] = plugin_yaml_part

    __move_to_spec_node(current_yaml, new_yaml, "inputs")
    if current_yaml.get("computedInputs") is not None:
        new_yaml["spec"]["computed-inputs"] = current_yaml.pop("computedInputs")
    else:
        __move_to_spec_node(current_yaml, new_yaml, "computed-inputs")
    __move_to_spec_node(current_yaml, new_yaml, "global-computed-inputs")
    __move_to_spec_node(current_yaml, new_yaml, "hooks")

    print(f"The following content was not converted in {yaml_name}.yaml: " + str(current_yaml))
    print(f"Backup: renaming {yaml_name}.yaml to {yaml_name}_old.yaml...")
    os.rename(current_yaml_file_path, resource_old_yaml_path)

    print(f"Creating a new plugin.yaml file...")
    __write_yaml_content_to_file(new_yaml, resource_folder_path + os.sep + "plugin.yaml")

    print("Copying release notes and requirements doc files to docs folder...")
    docs_folder_path = resource_folder_path + os.sep + "docs" + os.sep
    if not os.path.exists(docs_folder_path):
        print(f"Creating 'docs' folder in {resource_folder_path}")
        os.mkdir(docs_folder_path)

    this_script_folder_path = sys.path[0] + os.sep
    release_notes_filename = "release-notes-0.0.1.md"
    requirements_filename = "requirements.md"
    shutil.copy(this_script_folder_path + release_notes_filename,
                docs_folder_path + release_notes_filename)
    shutil.copy(this_script_folder_path + requirements_filename,
                docs_folder_path + requirements_filename)

    print("Done!")


convert_to_new_plugin(str(sys.argv[1]).strip())
