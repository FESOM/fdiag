import yaml
import os
import papermill as pm
import math


def define_rowscol(settings, reduce=0):
    number_paths = len(settings["input_paths"]) - reduce
    columns = settings["columns"]

    if number_paths < columns:
        ncol = number_paths
    else:
        ncol = columns
    nrows = math.ceil(number_paths / columns)
    return [nrows, ncol]


def create_current_params(settings):
    current_params = {}
    for key, value in settings.items():
        if isinstance(value, dict):
            pass
        else:
            current_params[key] = value
    return current_params


def fill_input(current_params, settings, climatology=True):
    if climatology:
        current_params["input_paths"] = settings["input_paths"][1:]
        current_params["input_names"] = settings["input_names"][1:]
        current_params["reference_path"] = settings["climatology_path"]
        current_params["reference_name"] = "clim"
        current_params["reference_years"] = settings["climatology_year"]
    else:
        current_params["input_paths"] = settings["input_paths"][1:]
        current_params["input_names"] = settings["input_names"][1:]
        current_params["reference_path"] = settings["input_paths"][0]
        current_params["reference_name"] = settings["input_names"][0]
        current_params["reference_years"] = settings["years"]
    return current_params


def check_num_paths(settings, min_number=2):
    number_paths = len(settings["input_paths"])
    if number_paths < min_number:
        raise ValueError(
            "You specified `difference` analysis, but provide only one path"
        )


def drive_difference(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    check_num_paths(settings)
    current_params = create_current_params(settings)
    current_params = fill_input(current_params, settings, climatology=False)
    webpage = {}
    image_count = 0
    for variable in driver_settings:
        for depth in driver_settings[variable]["depths"]:
            current_params["variable"] = variable
            current_params["depth"] = depth
            current_params.update(driver_settings[variable])
            del current_params["depths"]

            current_params["rowscol"] = define_rowscol(settings, reduce=1)

            ofile = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.png"
            ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.ipynb"
            current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

            pm.execute_notebook(
                "./templates/difference.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
            webpage[f"image_{image_count}"] = {}
            webpage[f"image_{image_count}"][
                "name"
            ] = f"{variable.capitalize()} at {depth} m"
            webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
            webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
            webpage[f"image_{image_count}"][
                "short_name"
            ] = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}"
            image_count += 1
    return webpage


