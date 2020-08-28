import yaml
import os
import papermill as pm
import math
import pkg_resources
from jinja2 import Environment, FileSystemLoader
import yaml

from drivers import (
    drive_difference,
    drive_ice_integrals,
    drive_hovm_difference,
    drive_ocean_integrals,
    drive_xmoc,
    drive_amoc_timeseries,
    drive_vertical_profile
)

templates_path = pkg_resources.resource_filename(__name__, f"templates_html")
file_loader = FileSystemLoader(templates_path)
env = Environment(loader=file_loader)

workflow_settings = "short.yml"

with open(workflow_settings) as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)

workflow_name = settings['workflow_name']

input_paths = settings['input_paths']
if "input_names" in settings:
    input_names = settings['input_names']
else:
    input_names = None


def check_input_names(input_names, input_paths):
    if input_names is None:
        input_names = []
        for run in input_paths:
            run = os.path.join(run, "")
            input_names.append(run.split("/")[-2])
    elif len(input_names) != len(input_paths):
        raise ValueError("The size of input_names is not equal to the size of input_paths")
    
    return input_names

input_names = check_input_names(input_names, input_paths)
print(input_names)

ofolder = f"./results/{workflow_name}"

settings["years"] = list(range(settings["start_year"], settings["end_year"] + 1))
settings["input_paths"] = input_paths
settings["input_names"] = input_names
settings["workflow_name"] = workflow_name
settings["workflow_settings"] = workflow_settings
settings["ofolder_notebooks"] = os.path.join(ofolder, "notebooks")
settings["ofolder_figures"] = os.path.join(ofolder, "figures")

if not os.path.exists(ofolder):
    os.makedirs(settings["ofolder_notebooks"])
    os.makedirs(settings["ofolder_figures"])

webpages = {}
webpages["general"] = {}
webpages["general"]["name"] = settings["workflow_name"]
webpages["analyses"] = {}

analyses = {}
analyses['difference'] = drive_difference
analyses['climatology'] = drive_difference
analyses['ice_integrals'] = drive_ice_integrals
analyses['hovm_difference'] = drive_hovm_difference
analyses['hovm_difference_clim'] = drive_hovm_difference
analyses['ocean_integrals'] = drive_ocean_integrals
analyses['xmoc'] = drive_xmoc
analyses['xmoc_difference'] = drive_xmoc
analyses['amoc_timeseries'] = drive_amoc_timeseries
analyses['vertical_profile'] = drive_vertical_profile

for analysis in analyses:
    if analysis in analyses:
        webpage = analyses[analysis](settings, analysis)
        webpages['analyses'][analysis] = webpage


# ofolder = f"{experiment_path}/"
#     if not os.path.exists(ofolder):
#         os.makedirs(ofolder)
#     date = cn["experiments"][experiment_name]["date"]
ofilename = f"{settings['workflow_name']}.html"
opath = os.path.join(ofolder, ofilename)
ofile = open(opath, "w")
template = env.get_template("experiment.html")
#     output = template.render(cn["experiments"][experiment_name])
output = template.render(webpages)
ofile.write(output)
ofile.close()
# print(webpages)
