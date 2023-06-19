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
    # ToDo: convert these to a class so that label width, and height are available
    routes_bbox = bbox(routes)
    # Extend the bbox by width and height on both sides
    routes_bbox = (
        routes_bbox[0] - label_width,
        routes_bbox[1] - label_height,
        routes_bbox[2] + label_width,
        routes_bbox[3] + label_height,
    )

    # Grid always starts from 0 and we assume for now
    # That 0 - label_widt and 0-label_height will be available
    bbox_width = routes_bbox[2] - 0
    bbox_height = routes_bbox[3] - 0

    num_x_cells = np.ceil(bbox_width / label_width)
    num_y_cells = np.ceil(bbox_height / label_height)

    x = np.arange(
        0,
        # FIXME: The 0.1 is because arange does not stop at stop
        routes_bbox[0] + num_x_cells * label_width + 0.1 * label_width,
        label_width,
    )
    y = np.arange(
        0,
        # FIXME: The 0.1 is because arange does not stop at stop
        routes_bbox[1] + num_y_cells * label_height + 0.1 * label_height,
        label_height,
    )
    return np.meshgrid(x, y)


def refine_line(points, n):
    """
    Refine a route by n number of points which is tunable
    """
    refined_points = []
    # ToDo: This is a python for loop and can be made faster using numpy
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        x = np.linspace(x1, x2, n)
        y = np.linspace(y1, y2, n)
        refined_points.extend(zip(x, y))
    refined_points = np.array(refined_points)
    return refined_points


def determine_cell(point, cell_size_x, cell_size_y):
    # Is going to be slow. Need to speed up with NumPy
    cell_x = np.floor(point[0] / cell_size_x).astype(int)
    cell_y = np.floor(point[1] / cell_size_y).astype(int)
    return cell_x, cell_y


def inside_cell(point, cell_x, cell_y, grid_x, grid_y):
    if (
        point[0] > grid_x[cell_y][cell_x]
        and point[0] < grid_x[cell_y][cell_x + 1]
        and point[1] > grid_y[cell_y][cell_x]
        and point[1] < grid_y[cell_y + 1][cell_x]
    ):
        return 1
    else:
        return 0


def get_occupancy(route, grid_x, grid_y, occupancy):
    cell_width = grid_x[0][1] - grid_x[0][0]
    cell_height = grid_y[1][0] - grid_y[0][0]

    refined_points = refine_line(route, 10)
    for point in refined_points:
        cell_x, cell_y = determine_cell(point, cell_width, cell_height)

        # IF it is already 1, we want to retain it, so doing an or
        occupancy[cell_y][cell_x] = (
            inside_cell(point, cell_x, cell_y, grid_x, grid_y)
            or occupancy[cell_y][cell_x]
        )

    return occupancy


def set_occupancy(routes):
    np_routes = []
    # ToDo: We should read each line directly as numpy arrays
    # And then reshape
    for route in routes:
        np_routes.append(np.array(route))

    grid_x, grid_y = create_grid(np_routes)

    # A box is defined by x[i], x[i+1], y[i], y[i+1]
    # For this box we determine if there are points or other boxes
    # within this box
    # We only want to put occupancy as 1 if a line is strictly inside a box
    # We cannot iterate over the line, so we refine the line and iterate over the points:w

    occupancy = np.zeros_like(grid_x)

    # For points in each polyline, iterate over them and set occupancy to 1
    # if they or their mid-point lies inside a box
    # We can refine this with more resolution later

    for route in np_routes:
        occupancy = get_occupancy(route, grid_x, grid_y, occupancy)

    print(occupancy)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)

    set_occupancy(parsed_routes)
