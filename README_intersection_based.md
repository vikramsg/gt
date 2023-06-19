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
make run_intersection_based ROUTE_FILE=zurich_bern_routes.txt OUTPUT_FILE=labels_zurich_bern.txt
```


## Algorithm

1. We first find the point on a route nearest to bbox center
2. Then we try to put a rectangle on the 4 sides of this point and test for intersection
3. If no intersection found, we put a label there
4. If intersection if found, either with route or other rectangles, we shift the point, trying both left and right side

### Enhancements
1. To find aesthetically pleasing locations, we would need to have tolerance with the routes as well
2. Read file directly into NumPy and then reshape