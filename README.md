## Acknowledgements
An acknowledgement is in place for the dash example library. Although most of the code was written by ourselves, 
the dash-opiod-epidemic (https://dash.gallery/dash-opioid-epidemic/) example from the library itself served as a basis 
for this project.


## Install
Using pip and an instance of python 3.7 or 3.8, installing is as easy as running
```
pip install -r ./requirements.txt
```

## Running
Running can simply be done by running the `app.py` file.
```
python ./app.py
```


## Structure
The left_side_plots.py file is the implementation of the choropleth map, the right_side_plots.py contains the
implementation of the right side graphs, the right_side_tabs.py contains the implementation of the Select Districts
and General Info tabs on the right side. App.py ties everything together.