## Install

The project uses Poetry, a package and virtual environment manager for Python.  
Installation instructions for poetry are [here](https://python-poetry.org/docs/). 
A TLDR is to do 

```
curl -sSL https://install.python-poetry.org | python3 - --version 1.4.2
```

and then add `$HOME/.local/bin` to the Path. 
```
export PATH="$HOME/.poetry/bin:$PATH"
```

Check for installation using `poetry --version` and make sure it shows `1.4.2`.

Once you have Poetry setup, you can simply go to the root of the directory and do

```
make install
```


## Run

The input and output files have to be provided, for eg. in the following manner. 
```
make run ROUTE_FILE=basic_test_routes.txt OUTPUT_FILE=labels_out.txt
make run ROUTE_FILE=zurich_bern_routes.txt OUTPUT_FILE=labels_zurich_bern.txt
```


## Development notes

1. There are multiple polylines in a file
2. Each polyline can have potentially thousands of points, so NumPy is probably the correct way to store them
3. However, DS will also depend on algorithm


## Algorithm notes

### Requirements

1. Each polyline is a separate route
2. Hard requirement
    a. With choices of top-left, top-right, bottom-left, bottom-right, mark labels
    b. Is it one label. Doing one label is sufficient?
    c. Input is only through stdin?
    d. Will the input be valid?
3. Soft Requirements
4. Labels to be placed at arbitrary points, but they must be placed at points to distinguish between routes. 
5. Labels as close to center of overall bounding box as possible
6. To start with assume labels are of size 100x50, and they should not cover any routes. But ideally this should be at any zoom level.