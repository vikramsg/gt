import argparse

import numpy as np

from src.plot_routes import parse_routes


def route_bbox(route):
    """For a single polyline return bounding box

    Args:
        route (2D numpy.array): Polyline as numpy array

    Returns:
        bbox: Tuple of size 4, with first 2 coords as left bottom
            and last 2 as right top
    """
    return (
        np.min(route[:, 0]),
        np.min(route[:, 1]),
        np.max(route[:, 0]),
        np.max(route[:, 1]),
    )


def bbox(routes):
    """Get bbox of all routes

    Args:
        routes (List of 2D numpy.array): List of all Polylines (each is numpy array)

    Returns:
        bbox: Tuple of size 4, with first 2 coords as left bottom
            and last 2 as right top

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


def create_grid(routes, label_width=100, label_height=50):
    np_routes = []
    # ToDo: We should read each line directly as numpy arrays
    # And then reshape
    for route in routes:
        np_routes.append(np.array(route))

    routes_bbox = bbox(np_routes)
    # Extend the bbox by width and height on both sides
    routes_bbox = (
        routes_bbox[0] - label_width,
        routes_bbox[1] - label_height,
        routes_bbox[2] + label_width,
        routes_bbox[3] + label_height,
    )

    bbox_width = routes_bbox[2] - routes_bbox[0]
    bbox_height = routes_bbox[3] - routes_bbox[1]

    num_x_cells = np.ceil(bbox_width / label_width)
    num_y_cells = np.ceil(bbox_height / label_height)

    x = np.arange(
        routes_bbox[0],
        # FIXME: The 0.1 is because arange does not stop at stop
        routes_bbox[0] + num_x_cells * label_width + 0.1 * label_width,
        label_width,
    )
    y = np.arange(
        routes_bbox[1],
        # FIXME: The 0.1 is because arange does not stop at stop
        routes_bbox[1] + num_y_cells * label_height + 0.1 * label_height,
        label_height,
    )
    return np.meshgrid(x, y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)
    grid_x, grid_y = create_grid(parsed_routes)
    print(grid_x)
    print(grid_y)
