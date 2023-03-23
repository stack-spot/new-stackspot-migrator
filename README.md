### Requirements:
- Stackspot stkcli v4.x, but not the new Stackspot cli (v5.x).
- Python v3.9+ (python3 or python available in terminal)
- `ruamel.yaml` lib (https://pypi.org/project/ruamel.yaml/)

### Template and Plugin migration:

1- Import stack https://github.com/stack-spot/new-stackspot-migrator

2- Run command `stk run new-stackspot-migrator/plugin-migrator`

3- Inform the complete folder path of the plugin or template to be migrated. In case of a template, it will be converted to a plugin. 

The original resource yaml file (`plugin.yaml` or `template.yaml`) file will be renamed, having the suffix `_old` added, 
and a `plugin.yaml` file will be created. Also, some documents will be created in the `docs` folder inside the resource 
folder. To revert the operation, just delete the `plugin.yaml` file and rename the resource yaml file with `_old` suffix 
back to its original name.

