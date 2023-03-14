import os
import shutil
import sys

import yaml


def __get_yaml_content_from_file(yaml_file_path):
    with open(yaml_file_path, "r") as stream:
        try:
            content = yaml.safe_load(stream.read())
        except yaml.YAMLError as exception:
            print(exception)
    return content


def __write_yaml_content_to_file(yaml_dict, yaml_file_path, sort_keys=False):
    with open(yaml_file_path, "w") as stream:
        try:
            yaml.dump(yaml_dict, stream, default_flow_style=False, sort_keys=sort_keys)
        except yaml.YAMLError as exception:
            print(exception)


# Moves a whole property-value from __old_yaml to the spec property of __new_yaml
def __move_to_spec_property(__old_yaml, __new_yaml, property_name):
    if __old_yaml.get(property_name) is not None:
        __new_yaml["spec"][property_name] = __old_yaml.pop(property_name)


def do_conversion(plugin_folder_path):
    plugin_old_yaml_file_path = plugin_folder_path + os.sep + "plugin_old.yaml"
    if os.path.exists(plugin_old_yaml_file_path):
        raise Exception(
            "Plugin already converted. If you want to rerun the conversion process, delete file plugin.yaml and rename "
            "plugin_old.yaml to plugin.yaml.")

    plugin_yaml_file_path = plugin_folder_path + os.sep + "plugin.yaml"
    current_yaml = __get_yaml_content_from_file(plugin_yaml_file_path)

    # base structure (https://newdocs.stackspot.com/platform-content/studio/plugin/create-plugin/)
    new_yaml = {
        "kind": "plugin",
        "schema-version": "v1",
        "spec": {
            "about": current_yaml.pop("about"),
            "requirements": "docs/requirements.md",
            "repository": "PENDING",
            "implementation": current_yaml.pop("implementation"),
            "type": "app",
            "release-notes": "docs/release-notes-0.0.1.md",
            "usage": current_yaml.pop("usage"),
            "technologies": current_yaml.pop("technologies"),
            "compatibility": current_yaml.pop("compatibility")
        },
        "metadata": {
            "picture": current_yaml.pop("picture"),
            "display-name": current_yaml.pop("display-name") if current_yaml.get(
                "display-name") is not None else current_yaml.pop("displayName"),
            "version": "0.0.1",
            "name": current_yaml.pop("name"),
            "description": current_yaml.pop("description")
        }
    }

    # Key 'requirements' now is 'spec.requires'
    if current_yaml.get("requirements") is not None:
        new_yaml["spec"]["requires"] = current_yaml.pop("requirements")

    __move_to_spec_property(current_yaml, new_yaml, "inputs")
    __move_to_spec_property(current_yaml, new_yaml, "computed-inputs")
    __move_to_spec_property(current_yaml, new_yaml, "global-computed-inputs")
    __move_to_spec_property(current_yaml, new_yaml, "hooks")

    print("The following content was not converted in plugin.yaml: " + str(current_yaml))
    print("Renaming plugin.yaml to plugin_old.yaml...")
    os.rename(plugin_yaml_file_path, plugin_old_yaml_file_path)

    print("Updating plugin.yaml with the new content...")
    __write_yaml_content_to_file(new_yaml, plugin_yaml_file_path)

    print("Copying release notes and requirements doc files to docs folder")
    script_folder_path = sys.path[0] + os.sep
    plugin_docs_folder_path = plugin_folder_path + os.sep + "docs" + os.sep
    release_notes_filename = "release-notes-0.0.1.md"
    requirements_filename = "requirements.md"
    shutil.copy(script_folder_path + release_notes_filename,
                plugin_docs_folder_path + release_notes_filename)
    shutil.copy(script_folder_path + requirements_filename,
                plugin_docs_folder_path + requirements_filename)


do_conversion(str(sys.argv[1]).strip())
