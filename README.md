# fdiag
FESOM2 diagnostics suite

Command line utility that will run a set of diagnostics for FESOM2 runs.

## Installation
### Requirements
* You should have [pyfesom2](https://github.com/FESOM/pyfesom2) installed already. 
* In addition you should also have [papermill](https://papermill.readthedocs.io/en/latest/).
* For `enso_eof` diagnostic to work, you need also [eofs](https://ajdawson.github.io/eofs/latest/)

### Installation
 
Currently only installation from source with pip is supported. You have to clone the repository:

```bash
git clone https://github.com/FESOM/fdiag.git
```

And install it with pip:

```bash
cd fdiag
pip install -e .
```


Alternatively, you can directly install everything via (but some users reported problems with this one):

```bash
pip install git+https://github.com/FESOM/fdiag.git
```

Note that this may require the `--user` flag if you don't have root privileges. 



## Usage

After installation you should have `fdiag` utility available as a command line programm. As an argument you should provide path to the yaml workflow file. Examples of the workflows are located in `workflows` folder. For example:

```bash
fdiag ./worflows/short.yml
```

You should modify the worflow file to make it work with your data. Workflow file consist of general part, where settings for all diagnostics are defined, and separate settings for each of the diagnostics. As a result you should get html and pdf files, that contain results of the diagnostic runs. They will be placed in the `results` folder.

### Options

* `-d` you can provide one or several diagnostics that will be run, skipping all other diagnostics from the worflow file.
* `-n` pfd output will not be generated.

## Available diagnostics

All available diagnostics with some possible options are shown in the example file `workflows/long_test.yml`

* `variable`- plot map with spatial distribution of the variable at particular depth.
* `difference` plot map with spatial distribution of differences between two runs at particular depth
* `difference_np` and `difference_sp` - same as `difference`, but allow to define this diagnostic for different regions in one workflow, usually (but non nesesarely) for Northern and Southern stereographic projections. 
* `climatology` - plot map with spatial distribution of differences between variable and climatology. Climatology should be defined on the same mesh as the data.
* `climatology_np` and `climatology_np` same as `climatology`, but allow to define this diagnostic for different regions in one workflow, usually (but non nesesarely) for Northern and Southern stereographic projections. 
* `ice_integrals` - time series of sea ice area and volume for each time step as well as for March and September.
* `hovm_difference` - hovmöller diagram for differences between runs, with time on X-axis and depth on Y-asis.
* `hovm_difference_clim` - hovmöller diagram for differences between each run and climatology, with time on X-axis and depth on Y-asis.
* `ocean_integrals` - time series of variable mean value between (or at) some depth(s).
* `xmoc` - MOC fro different regions. Calculations are based on w.
* `xmoc_difference` - difference in MOC between runs.
* `amoc_timeseries` - timeseries of AMOC at arbitrary latitudes.
* `vertical_profile_diff` - difference between mean vertical profiles for variable between runs.
* `vertical_profile_diff_clim` - difference between mean vertical profiles for variable between each run and climatology.
