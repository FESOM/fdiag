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

workflow_name = "test"

workflow_settings = "compare_two_CORE_ollie.yml"


input_paths = [
    "/Users/nkolduno/PYTHON/DATA/output_7_8/",
    "/Users/nkolduno/PYTHON/DATA/output_7_10",
]

input_names = None

if input_names is None:
    input_names = []
    for run in input_paths:
        run = os.path.join(run, "")
        input_names.append(run.split("/")[-2])
elif len(input_names) != len(input_paths):
    raise ValueError("The size of input_names is not equal to the size of input_paths")


with open(workflow_settings) as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)

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

if 'difference' in settings:
    webpage = drive_difference(settings, 'difference')
    webpages['analyses']['difference'] = webpage

if 'climatology' in settings:
    webpage = drive_difference(settings, 'climatology')
    webpages['analyses']['climatology'] = webpage

if 'ice_integrals' in settings:
    webpage = drive_ice_integrals(settings, 'ice_integrals')
    webpages['analyses']['ice_integrals'] = webpage

if 'hovm_difference' in settings:
    webpage = drive_hovm_difference (settings, 'hovm_difference')
    webpages['analyses']['hovm_difference'] = webpage

if 'hovm_difference_clim' in settings:
    webpage = drive_hovm_difference (settings, 'hovm_difference_clim')
    webpages['analyses']['hovm_difference_clim'] = webpage

if "ocean_integrals" in settings:
    webpage = drive_ocean_integrals(settings, "ocean_integrals")
    webpages["analyses"]["ocean_integrals"] = webpage

if "xmoc" in settings:
    webpage = drive_xmoc(settings, "xmoc")
    webpages["analyses"]["xmoc"] = webpage

if "xmoc_difference" in settings:
    webpage = drive_xmoc(settings, "xmoc_difference")
    webpages["analyses"]["xmoc_difference"] = webpage

if "amoc_timeseries" in settings:
    webpage = drive_amoc_timeseries(settings, "amoc_timeseries")
    webpages["analyses"]["amoc_timeseries"] = webpage

if "vertical_profile" in settings:
    webpage = drive_vertical_profile(settings, "vertical_profile")
    webpages["analyses"]["vertical_profile"] = webpage


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
