import argparse
from typing import List

import numpy as np

from src.plot_routes import parse_routes


def route_bbox(route):
    return (
        np.min(route[:, 0]),
        np.min(route[:, 1]),
        np.max(route[:, 0]),
        np.max(route[:, 1]),
    )


def bbox(routes):
    """
    ToDo: These are all ints, we should use Int specialization
    """
    bbox_routes = route_bbox(routes[0])
    if len(routes) > 1:
        for route in routes:
            bbox_route = route_bbox(route)
            bbox_routes = (
                np.min([bbox_routes[0], bbox_route[0]]),
                np.min([bbox_routes[1], bbox_route[1]]),
                np.max([bbox_routes[2], bbox_route[2]]),
                np.max([bbox_routes[3], bbox_route[3]]),
            )

    return bbox_routes


def create_grid(routes):
    np_routes = []
    # ToDo: We should read each line directly as numpy arrays
    # And then reshape
    for route in routes:
        np_routes.append(np.array(route))

    print(bbox(np_routes))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)
    create_grid(parsed_routes)
