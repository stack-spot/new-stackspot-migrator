### Requirements:
- Stackspot cli v.4.4+, but not the new Stackspot cli.
- Python v3.9+ (python3 available in terminal)
- PyYAML lib (https://pypi.org/project/PyYAML/)

### Plugin migration:

1- Import stack https://github.com/stack-spot/new-stackspot-migrator

2- Run command `stk run new-stackspot-migrator/plugin-migrator`

3- Inform the complete folder path of the plugin to be migrated. 

The original `plugin.yaml` file will be renamed to `plugin_old.yaml` and a new `plugin.yaml` file will be created.
Also, some documents will be created in the `docs` folder inside the plugin. 
To revert the operation, just delete the `plugin.yaml` file and rename `plugin_old.yaml` back to `plugin.yaml`

