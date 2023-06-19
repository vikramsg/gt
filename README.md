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


## Algorithm

1. We first determine the bounding box and then divide the grid into cells
2. We set an occupancy inside the cells if points in the route pass through them
3. Then we try to find empty cells close to the center of the grid
4. If they exist, then we set that to be the required location
5. If not, we find the closest empty cell and set that. 


### Enhancements
1. There are bugs with the current approach which seems to not show the correct occupancy
2. We can get rid of a lot of for loops and use vectorization
3. To find aesthetically pleasing locations, we want to make sure that the cell lines don't have multiple overlaps with the route