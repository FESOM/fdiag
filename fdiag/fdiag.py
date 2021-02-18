import yaml
import os
import papermill as pm
import math
import pkg_resources
from jinja2 import Environment, FileSystemLoader
import yaml
import argparse
import json
import glob
import shutil


from fdiag.drivers import (
    drive_variable,
    drive_difference,
    drive_ice_integrals,
    drive_hovm_difference,
    drive_ocean_integrals,
    drive_xmoc,
    drive_amoc_timeseries,
    drive_vertical_profile,
    drive_ocean_integrals_difference,
    drive_transect_difference,
    drive_transect
)

templates_path = pkg_resources.resource_filename(__name__, f"templates_html")
file_loader = FileSystemLoader(templates_path)
env = Environment(loader=file_loader)


def check_input_names(input_names, input_paths):
    if input_names is None:
        input_names = []
        for run in input_paths:
            run = os.path.join(run, "")
            input_names.append(run.split("/")[-2])
    elif len(input_names) != len(input_paths):
        raise ValueError(
            "The size of input_names is not equal to the size of input_paths"
        )

    return input_names

class cd:
    """Context manager for changing the current working directory.

    https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def render_main_page():
    experiment_paths = glob.glob(f"./results/*")
    experiment_paths.sort()

    experiment_names = []
    for experiment in experiment_paths:
        experiment_names.append(os.path.basename(experiment))
        
    cn = {}
    cn["title"] = "FESOM2 diagnostics"
    cn["experiments"] = {}

    for experiment_name, experiment_path in zip(experiment_names, experiment_paths):
        cn["experiments"][experiment_name] = {}
        cn["experiments"][experiment_name]['experiment_path'] = experiment_path
        
    ofile = open("index.html", "w")
    template = env.get_template("index.html")
    output = template.render(cn)
    ofile.write(output)
    ofile.close()
    shutil.copy(os.path.join(templates_path, 'fesom2_logo.png'), './')


def render_latex(settings, ofolder):
    templates_path = pkg_resources.resource_filename(__name__, f"templates_latex")
    latex_jinja_env = Environment(
        block_start_string="\BLOCK{",
        block_end_string="}",
        variable_start_string="\VAR{",
        variable_end_string="}",
        comment_start_string="\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=FileSystemLoader(templates_path),
    )
    template = latex_jinja_env.get_template('experiment.tex')
    ofilename_latex = f"{settings['workflow_name']}.tex"
    opath_latex = os.path.join(ofolder, ofilename_latex)

    ofilename_webpages = f"{settings['workflow_name']}.json"
    opath_webpages = os.path.join(ofolder, ofilename_webpages)
    with open(opath_webpages) as json_file:
        webpages = json.load(json_file)
            
    output = template.render(webpages)
    ofile = open(opath_latex, "w")
    ofile.write(output)
    ofile.close()
    with cd(ofolder):
        os.system(f'pdflatex -interaction=nonstopmode {ofilename_latex}')


def fdiag():
    parser = argparse.ArgumentParser(prog="fdiag", description="Run FESOM diagnostics")
    parser.add_argument("workflow_settings", help="Name of the diagnostic workflow")

    parser.add_argument(
        "--diagnostics",
        "-d",
        nargs="+",
        help="Run only particilar diagnostics from the yml file.",
    )
    parser.add_argument(
        "--nopdf",
        "-n",
        action='store_true',
        help="If present, no pdf will be generated."
    )
    # parser.add_argument(
    #     "--newbin",
    #     "-n",
    #     action="store_true",
    #     help="If present separate bin directory will be created.",
    # )
    # parser.add_argument(
    #     "--forcing",
    #     "-f",
    #     type=str,
    #     help="Option to change forcing indicated in the experiment setup.",
    # )

    args = parser.parse_args()
    if args.diagnostics:
        print(f"Only those diagnostics will be run: {args.diagnostics}")

    workflow_settings = args.workflow_settings

    with open(workflow_settings) as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    workflow_name = settings["workflow_name"]

    input_paths = settings["input_paths"]
    if "input_names" in settings:
        input_names = settings["input_names"]
    else:
        input_names = None

    input_names = check_input_names(input_names, input_paths)
    print(f"The names of runs to be processed are:{input_names}")

    ofolder = f"./results/{workflow_name}"

    settings["years"] = list(range(settings["start_year"], settings["end_year"] + 1))
    if "start_year_short" in settings:
        settings["years_short"] = list(
            range(settings["start_year_short"], settings["end_year_short"] + 1)
        )
    settings["input_paths"] = input_paths
    settings["input_names"] = input_names
    settings["workflow_name"] = workflow_name
    settings["workflow_settings"] = workflow_settings
    settings["ofolder_notebooks"] = os.path.join(ofolder, "notebooks")
    settings["ofolder_figures"] = os.path.join(ofolder, "figures")

    if not os.path.exists(ofolder):
        os.makedirs(settings["ofolder_notebooks"])
        os.makedirs(settings["ofolder_figures"])

    ofilename_webpages = f"{settings['workflow_name']}.json"
    opath_webpages = os.path.join(ofolder, ofilename_webpages)

    if os.path.exists(opath_webpages):
        with open(opath_webpages) as json_file:
            webpages = json.load(json_file)
            print(f"Data on previous runs exist in {opath_webpages}, \n")
            print("they will be used to generate output for diagnostics you do not run this time.")
    else:
        webpages = {}
        webpages["analyses"] = {}

    webpages["general"] = {}
    webpages["general"]["name"] = settings["workflow_name"]

    analyses = {}
    analyses["variable"] = drive_variable
    analyses["difference"] = drive_difference
    analyses["difference_np"] = drive_difference
    analyses["difference_sp"] = drive_difference
    analyses["climatology"] = drive_difference
    analyses["climatology_np"] = drive_difference
    analyses["climatology_sp"] = drive_difference
    analyses["ice_integrals"] = drive_ice_integrals
    analyses["hovm_difference"] = drive_hovm_difference
    analyses["hovm_difference_clim"] = drive_hovm_difference
    analyses["ocean_integrals"] = drive_ocean_integrals
    analyses["xmoc"] = drive_xmoc
    analyses["xmoc_difference"] = drive_xmoc
    analyses["amoc_timeseries"] = drive_amoc_timeseries
    analyses["vertical_profile_diff"] = drive_vertical_profile
    analyses["vertical_profile_diff_clim"] = drive_vertical_profile
    analyses["ocean_integrals_difference"] = drive_ocean_integrals_difference
    analyses["ocean_integrals_difference_clim"] = drive_ocean_integrals_difference
    analyses["transect_difference"] = drive_transect_difference
    analyses["transect_difference_clim"] = drive_transect_difference
    analyses["transect"] = drive_transect

    # loop over all analyses
    for analysis in analyses:
        # check if analysis is in input yaml
        if analysis in settings:
            # if no specific analysis are selected with -d option, just run
            if args.diagnostics is None:
                print(f"!!! Performing {analysis} !!!")
                webpage = analyses[analysis](settings, analysis)
                webpages["analyses"][analysis] = webpage
            # else just perform those selected with -d
            else:
                if analysis in args.diagnostics:
                    print(f"!!! Performing {analysis} !!!")
                    webpage = analyses[analysis](settings, analysis)
                    webpages["analyses"][analysis] = webpage

            with open(opath_webpages, "w") as fp:
                json.dump(webpages, fp)

    ofilename = f"{settings['workflow_name']}.html"
    opath = os.path.join(ofolder, ofilename)
    ofile = open(opath, "w")
    template = env.get_template("experiment.html")
    output = template.render(webpages)
    ofile.write(output)
    ofile.close()

    render_main_page()
    if args.nopdf is False:
        render_latex(settings, ofolder)
    


if __name__ == "__main__":
    # args = parser.parse_args()
    # args.func(args)
    fdiag()
