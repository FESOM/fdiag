import yaml
import os
import papermill as pm
import math
import pkg_resources

templates_nb_path = pkg_resources.resource_filename(__name__, f"templates")
print(templates_nb_path)
def define_rowscol(settings, reduce=0):
    number_paths = len(settings["input_paths"]) - reduce
    columns = settings["columns"]
    if number_paths < columns:
        ncol = number_paths
    else:
        ncol = columns
    nrows = math.ceil(number_paths / columns)
    return [nrows, ncol]


def create_current_params(settings, years_short=False):
    current_params = {}
    for key, value in settings.items():
        if isinstance(value, dict):
            pass
        else:
            current_params[key] = value
    if years_short:
        if 'years_short' in settings:
            current_params['years'] = settings['years_short']
    
    return current_params


def fill_input(current_params, settings, fill_type = "climatology", years_short=True):
    if fill_type == "climatology":
        current_params["input_paths"] = settings["input_paths"][:]
        current_params["input_names"] = settings["input_names"][:]
        current_params["reference_path"] = settings["climatology_path"]
        current_params["reference_name"] = "clim"
        current_params["reference_years"] = settings["climatology_year"]
    elif fill_type == "reference":
        current_params["input_paths"] = settings["input_paths"][1:]
        current_params["input_names"] = settings["input_names"][1:]
        current_params["reference_path"] = settings["input_paths"][0]
        current_params["reference_name"] = settings["input_names"][0]
        if ('years_short' in settings) & (years_short == True):
            current_params["reference_years"] = settings["years_short"]
        else:
            current_params["reference_years"] = settings["years"]
    # elif fill_type == "pure":
    #     current_params["input_paths"] = settings["input_paths"][:]
    #     current_params["input_names"] = settings["input_names"][:]
    #     current_params["reference_path"] = settings["climatology_path"]
    #     current_params["reference_name"] = "clim"
    #     current_params["reference_years"] = settings["climatology_year"]
    else:
        raise ValueError(f'Unknown fill_type {fill_type}')
    return current_params


def check_num_paths(settings, min_number=2):
    number_paths = len(settings["input_paths"])
    if number_paths < min_number:
        raise ValueError(
            f"You specified only {number_paths} path(s), analysis require at least {min_number}"
        )

def drive_variable(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    check_num_paths(settings, min_number=1)
    current_params = fill_input(current_params, settings, fill_type = "climatology")
    webpage = {}
    image_count = 0
    for variable in driver_settings:
        for depth in driver_settings[variable]["depths"]:
            current_params["variable"] = variable
            current_params["depth"] = depth
            current_params.update(driver_settings[variable])
            del current_params["depths"]

            current_params["rowscol"] = define_rowscol(settings, reduce=0)

            ofile = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.png"
            ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.ipynb"
            current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)
            pm.execute_notebook(
                f"{templates_nb_path}/variable.ipynb",
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


def drive_difference(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    if 'climatology' not in analysis_name:
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = "reference")
    else:
        check_num_paths(settings, min_number=1)
        current_params = fill_input(current_params, settings, fill_type = "climatology")
    webpage = {}
    image_count = 0
    for variable in driver_settings:
        for depth in driver_settings[variable]["depths"]:
            current_params["variable"] = variable
            current_params["depth"] = depth
            current_params.update(driver_settings[variable])
            del current_params["depths"]

            if 'climatology' not in analysis_name:
                current_params["rowscol"] = define_rowscol(settings, reduce=1)
            else:
                current_params["rowscol"] = define_rowscol(settings, reduce=0)

            ofile = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.png"
            ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{variable}_{depth}.ipynb"
            current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)
            pm.execute_notebook(
                f"{templates_nb_path}/difference.ipynb",
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

def drive_ice_integrals(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    current_params.update(driver_settings)

    ofile = f"{settings['workflow_name']}_{analysis_name}"
    ofile_nb = f"{settings['workflow_name']}_{analysis_name}.ipynb"
    current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

    pm.execute_notebook(
                f"{templates_nb_path}/{analysis_name}.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
    ice_analyses = ['icearea', "icearea_march",
                "icearea_september", "iceext", "iceext_march", "iceext_september", 'icevol',
               'icevol_march', "icevol_september"]

    hemisphere = current_params['hemisphere']
    webpage = {}
    image_count = 0
    for variable in ice_analyses:
        webpage[f'image_{image_count}'] = {}
        webpage[f'image_{image_count}']['name'] = f"{variable}"
        webpage[f'image_{image_count}']['path'] = os.path.join('./figures/', ofile+f"_{hemisphere}_{variable}.png")
        webpage[f'image_{image_count}']['path_nb'] = os.path.join('./notebooks/', ofile_nb)
        webpage[f'image_{image_count}']['short_name'] = f"{settings['workflow_name']}_{analysis_name}_{hemisphere}_{variable}"
        image_count = image_count+1
    return webpage

def drive_ice_integrals_combined_nocomparison(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    current_params.update(driver_settings)

    ofile = f"{settings['workflow_name']}_{analysis_name}"
    ofile_nb = f"{settings['workflow_name']}_{analysis_name}.ipynb"
    current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

    pm.execute_notebook(
                f"{templates_nb_path}/{analysis_name}.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
    ice_analyses = ['icearea', "iceext", 'icevol']

    webpage = {}
    image_count = 0
    for variable in ice_analyses:
        webpage[f'image_{image_count}'] = {}
        webpage[f'image_{image_count}']['name'] = f"{variable}"
        webpage[f'image_{image_count}']['path'] = os.path.join('./figures/', ofile+f"_{variable}_combined.png")
        webpage[f'image_{image_count}']['path_nb'] = os.path.join('./notebooks/', ofile_nb)
        webpage[f'image_{image_count}']['short_name'] = f"{settings['workflow_name']}_{analysis_name}_{variable}"
        image_count = image_count+1
    return webpage

def drive_hovm_difference(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    if analysis_name != 'hovm_difference_clim':
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = 'reference')
    else:
        check_num_paths(settings, min_number=1)
        current_params = fill_input(current_params, settings, fill_type = 'climatology')
    webpage = {}
    image_count = 0
    for region_name, region in driver_settings.items():
        for variable_name, variable in region.items():

            current_params["region"] = region_name
            current_params["variable"] = variable_name
            current_params.update(variable)
            region_name_underscore = region_name.replace(' ', '_')

            ofile = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}.png"
            ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}.ipynb"
            current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

            pm.execute_notebook(
                f"{templates_nb_path}/hovm_difference.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
            webpage[f"image_{image_count}"] = {}
            webpage[f"image_{image_count}"][
                "name"
            ] = f"{variable_name.capitalize()} for {region_name}"
            webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
            webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
            webpage[f"image_{image_count}"][
                "short_name"
            ] = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}"
            image_count += 1
    return webpage

def drive_ocean_integrals(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)

    check_num_paths(settings, min_number=1)
    # current_params = fill_input(current_params, settings, fill_type = 'pure')
    webpage = {}
    image_count = 0
    for region_name, region in driver_settings.items():
        for variable_name, variable in region.items():
            for uplow in variable['uplows']:

                current_params["region"] = region_name
                current_params["variable"] = variable_name
                current_params['uplow'] = uplow

                if 'figsize_small' in settings:
                    current_params['figsize'] = settings['figsize_small']

                current_params.update(variable)
                region_name_underscore = region_name.replace(' ', '_')

                ofile = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}.png"
                ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}.ipynb"
                current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

                pm.execute_notebook(
                    f"{templates_nb_path}/{analysis_name}.ipynb",
                    os.path.join(settings['ofolder_notebooks'], ofile_nb),
                    parameters=current_params,
                    nest_asyncio=True,
                )

                webpage[f"image_{image_count}"] = {}
                webpage[f"image_{image_count}"][
                    "name"
                ] = f"{variable_name.capitalize()} for {region_name} {uplow[0]}-{uplow[1]}m"
                webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
                webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
                webpage[f"image_{image_count}"][
                    "short_name"
                ] = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}"
                image_count += 1
    return webpage

def drive_xmoc(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    if analysis_name == 'xmoc_difference':
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = 'reference')

    check_num_paths(settings, min_number=1)
    webpage = {}
    image_count = 0
    for region_name, region in driver_settings.items():

        current_params["region"] = region_name

        current_params.update(region)
        region_name_underscore = region_name.replace(' ', '_')

        ofile = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}.png"
        ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}.ipynb"
        current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

        pm.execute_notebook(
            f"{templates_nb_path}/{analysis_name}.ipynb",
            os.path.join(settings['ofolder_notebooks'], ofile_nb),
            parameters=current_params,
            nest_asyncio=True,
        )

        webpage[f"image_{image_count}"] = {}
        webpage[f"image_{image_count}"][
            "name"
        ] = f"MOC for {region_name}"
        webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
        webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
        webpage[f"image_{image_count}"][
            "short_name"
        ] = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}"
        image_count += 1
    return webpage

def drive_amoc_timeseries(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    
    if 'figsize_small' in settings:
        current_params['figsize'] = settings['figsize_small']
    
    current_params.update(driver_settings)
    ofile = f"{settings['workflow_name']}_{analysis_name}"
    ofile_nb = f"{settings['workflow_name']}_{analysis_name}.ipynb"
    current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

    pm.execute_notebook(
                f"{templates_nb_path}/{analysis_name}.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )

    webpage = {}
    image_count = 0
    for latitude in driver_settings['latitudes']:
        webpage[f'image_{image_count}'] = {}
        webpage[f'image_{image_count}']['name'] = f"AMOC at {latitude}"
        webpage[f'image_{image_count}']['path'] = os.path.join('./figures/', ofile+f"_{latitude}.png")
        webpage[f'image_{image_count}']['path_nb'] = os.path.join('./notebooks/', ofile_nb)
        webpage[f'image_{image_count}']['short_name'] = f"{settings['workflow_name']}_{analysis_name}_{latitude}"
        image_count = image_count+1

    return webpage

def drive_vertical_profile(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    if analysis_name != 'vertical_profile_diff_clim':
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = 'reference')
    else:
        check_num_paths(settings, min_number=1)
        current_params = fill_input(current_params, settings, fill_type = 'climatology')
    

    webpage = {}
    image_count = 0
    for variable_name, variable in driver_settings.items():
        current_params["variable"] = variable_name
        current_params.update(variable)

        ofile = f"{settings['workflow_name']}_{analysis_name}_{variable_name}"
        ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{variable_name}.ipynb"
        current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

        pm.execute_notebook(
            f"{templates_nb_path}/vertical_profile_difference.ipynb",
            os.path.join(settings['ofolder_notebooks'], ofile_nb),
            parameters=current_params,
            nest_asyncio=True,
        )
        webpage[f"image_{image_count}"] = {}
        webpage[f"image_{image_count}"][
            "name"
        ] = f"{variable_name.capitalize()} difference"
        webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile+"_difference.png")
        webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
        webpage[f"image_{image_count}"][
            "short_name"
        ] = f"{settings['workflow_name']}_{analysis_name}_{variable_name}_difference"
        image_count += 1

        webpage[f"image_{image_count}"] = {}
        webpage[f"image_{image_count}"][
            "name"
        ] = f"{variable_name.capitalize()} absolite values"
        webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile+"_absolute.png")
        webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
        webpage[f"image_{image_count}"][
            "short_name"
        ] = f"{settings['workflow_name']}_{analysis_name}_{variable_name}_absolute"
        image_count += 1

    return webpage

def drive_ocean_integrals_difference(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    if analysis_name != 'ocean_integrals_difference_clim':
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = 'reference')
    else:
        check_num_paths(settings, min_number=1)
        current_params = fill_input(current_params, settings, fill_type = 'climatology')
    # current_params = fill_input(current_params, settings, fill_type = 'pure')
    webpage = {}
    image_count = 0
    for region_name, region in driver_settings.items():
        for variable_name, variable in region.items():
            for uplow in variable['uplows']:

                current_params["region"] = region_name
                current_params["variable"] = variable_name
                current_params['uplow'] = uplow

                if 'figsize_small' in settings:
                    current_params['figsize'] = settings['figsize_small']

                current_params.update(variable)
                region_name_underscore = region_name.replace(' ', '_')

                ofile = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}.png"
                ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}.ipynb"
                current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

                pm.execute_notebook(
                    f"{templates_nb_path}/ocean_integrals_difference.ipynb",
                    os.path.join(settings['ofolder_notebooks'], ofile_nb),
                    parameters=current_params,
                    nest_asyncio=True,
                )

                webpage[f"image_{image_count}"] = {}
                webpage[f"image_{image_count}"][
                    "name"
                ] = f"{variable_name.capitalize()} for {region_name} {uplow[0]}-{uplow[1]}m"
                webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
                webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
                webpage[f"image_{image_count}"][
                    "short_name"
                ] = f"{settings['workflow_name']}_{analysis_name}_{region_name_underscore}_{variable_name}_{uplow[0]}_{uplow[1]}"
                image_count += 1
    return webpage


def drive_transect_difference(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    if analysis_name != 'transect_difference_clim':
        check_num_paths(settings, min_number=2)
        current_params = fill_input(current_params, settings, fill_type = 'reference')
    else:
        check_num_paths(settings, min_number=1)
        current_params = fill_input(current_params, settings, fill_type = 'climatology')
    webpage = {}
    image_count = 0
    for transect_name, transect in driver_settings.items():
        # for variable_name, variable in region.items():

        current_params["transect_name"] = transect_name
        variable_name = transect['variable']
        current_params["variable"] = variable_name
        current_params.update(transect)
        transect_name_underscore = transect_name.replace(' ', '_')

        ofile = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}.png"
        ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}.ipynb"
        current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

        pm.execute_notebook(
            f"{templates_nb_path}/transect_difference.ipynb",
            os.path.join(settings['ofolder_notebooks'], ofile_nb),
            parameters=current_params,
            nest_asyncio=True,
        )
        webpage[f"image_{image_count}"] = {}
        webpage[f"image_{image_count}"][
            "name"
        ] = f"{variable_name.capitalize()} for {transect_name}"
        webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
        webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
        webpage[f"image_{image_count}"][
            "short_name"
        ] = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}"
        image_count += 1
    return webpage

def drive_transect(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings, years_short=True)
    check_num_paths(settings, min_number=1)
    current_params = fill_input(current_params, settings, fill_type = 'climatology')
    webpage = {}
    image_count = 0
    for transect_name, transect in driver_settings.items():
        # for variable_name, variable in region.items():

        current_params["transect_name"] = transect_name
        variable_name = transect['variable']
        current_params["variable"] = variable_name
        current_params.update(transect)
        transect_name_underscore = transect_name.replace(' ', '_')

        ofile = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}.png"
        ofile_nb = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}.ipynb"
        current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

        pm.execute_notebook(
            f"{templates_nb_path}/transect.ipynb",
            os.path.join(settings['ofolder_notebooks'], ofile_nb),
            parameters=current_params,
            nest_asyncio=True,
        )
        webpage[f"image_{image_count}"] = {}
        webpage[f"image_{image_count}"][
            "name"
        ] = f"{variable_name.capitalize()} for {transect_name}"
        webpage[f"image_{image_count}"]["path"] = os.path.join('./figures/', ofile)
        webpage[f"image_{image_count}"]["path_nb"] = os.path.join('./notebooks/', ofile_nb)
        webpage[f"image_{image_count}"][
            "short_name"
        ] = f"{settings['workflow_name']}_{analysis_name}_{transect_name_underscore}_{variable_name}"
        image_count += 1
    return webpage

def drive_enso_eof(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    current_params.update(driver_settings)

    ofile = f"{settings['workflow_name']}_{analysis_name}"
    ofile_nb = f"{settings['workflow_name']}_{analysis_name}.ipynb"
    current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

    pm.execute_notebook(
                f"{templates_nb_path}/{analysis_name}.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
    enso_eof_analyses = ['enso_eof_map', "enso_eof_pc1", "enso_eof_psd"]

    webpage = {}
    image_count = 0
    for variable in enso_eof_analyses:
        webpage[f'image_{image_count}'] = {}
        webpage[f'image_{image_count}']['name'] = f"{variable}"
        webpage[f'image_{image_count}']['path'] = os.path.join('./figures/', ofile+f"_{variable}.png")
        webpage[f'image_{image_count}']['path_nb'] = os.path.join('./notebooks/', ofile_nb)
        webpage[f'image_{image_count}']['short_name'] = f"{settings['workflow_name']}_{analysis_name}_{variable}"
        image_count = image_count+1
    return webpage


def drive_enso_box(settings, analysis_name):
    driver_settings = settings[analysis_name].copy()
    current_params = create_current_params(settings)
    check_num_paths(settings, min_number=1)
    current_params.update(driver_settings)

    ofile = f"{settings['workflow_name']}_{analysis_name}"
    ofile_nb = f"{settings['workflow_name']}_{analysis_name}.ipynb"
    current_params["ofile"] = os.path.join(settings['ofolder_figures'], ofile)

    pm.execute_notebook(
                f"{templates_nb_path}/{analysis_name}.ipynb",
                os.path.join(settings['ofolder_notebooks'], ofile_nb),
                parameters=current_params,
                nest_asyncio=True,
            )
    enso_eof_analyses = ['enso_box_map','enso_box_index', "enso_box_psd"]

    webpage = {}
    image_count = 0
    for variable in enso_eof_analyses:
        webpage[f'image_{image_count}'] = {}
        webpage[f'image_{image_count}']['name'] = f"{variable}"
        webpage[f'image_{image_count}']['path'] = os.path.join('./figures/', ofile+f"_{variable}.png")
        webpage[f'image_{image_count}']['path_nb'] = os.path.join('./notebooks/', ofile_nb)
        webpage[f'image_{image_count}']['short_name'] = f"{settings['workflow_name']}_{analysis_name}_{variable}"
        image_count = image_count+1
    return webpage
