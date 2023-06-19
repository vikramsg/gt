import argparse

import numpy as np

from src.plot_routes import parse_routes


class Solution:
    def __init__(self, routes):
        self.routes = []
        # ToDo: We should read each line directly as numpy arrays
        # And then reshape
        for route in routes:
            self.routes.append(np.array(route))

        self.bbox_center = self.bbox_center()
        self.closest_indices = self.route_points_closest_to_center(
            self.bbox_center, self.routes
        )

        self.cell_width, self.cell_height = None, None
        self.grid_x, self.grid_y = self.create_grid(self.routes)

    def bbox_center(self):
        bbox = self.bbox(self.routes)

        return 0.5 * (bbox[0] + bbox[2]), 0.5 * (bbox[1] + bbox[3])

    def route_points_closest_to_center(self, bbox_center, routes):
        closest_indices = []
        for route in routes:
            distances = np.linalg.norm(route - bbox_center, axis=1)
            closest_index = np.argmin(distances)
            closest_indices.append(closest_index)

        return closest_indices

    def route_bbox(self, route):
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

    def bbox(self, routes):
        """Get bbox of all routes

        Args:
            routes (List of 2D numpy.array): List of all Polylines (each is numpy array)

        Returns:
            bbox: Tuple of size 4, with first 2 coords as left bottom
                and last 2 as right top

        ToDo: These are all ints, we should use Int specialization
        """
        bbox_routes = self.route_bbox(routes[0])
        if len(routes) > 1:
            for route in routes:
                bbox_route = self.route_bbox(route)
                bbox_routes = (
                    np.min([bbox_routes[0], bbox_route[0]]),
                    np.min([bbox_routes[1], bbox_route[1]]),
                    np.max([bbox_routes[2], bbox_route[2]]),
                    np.max([bbox_routes[3], bbox_route[3]]),
                )

        return bbox_routes

    def create_grid(self, routes, label_width=100, label_height=50):
        # ToDo: convert these to a class so that label width, and height are available
        routes_bbox = self.bbox(routes)
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
        self.cell_width = x[1] - x[0]
        self.cell_height = y[1] - y[0]
        return np.meshgrid(x, y)

    def refine_line(self, points, n):
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

    def determine_cell(self, point, cell_size_x, cell_size_y):
        """
        This only works if the grid starts at 0,0
        and has uniform rectangle cells
        This ensures that for each point, we only need to look
        at 1 cell rather than iterate over the whole grid
        """
        # Is going to be slow. Need to speed up with NumPy
        cell_x = np.floor(point[0] / cell_size_x).astype(int)
        cell_y = np.floor(point[1] / cell_size_y).astype(int)
        return cell_x, cell_y

    def inside_cell(self, point, cell_x, cell_y, grid_x, grid_y):
        if (
            point[0] > grid_x[cell_y][cell_x]
            and point[0] < grid_x[cell_y][cell_x + 1]
            and point[1] > grid_y[cell_y][cell_x]
            and point[1] < grid_y[cell_y + 1][cell_x]
        ):
            return 1
        else:
            return 0

    def get_occupancy(self, route, grid_x, grid_y, occupancy):
        cell_width = grid_x[0][1] - grid_x[0][0]
        cell_height = grid_y[1][0] - grid_y[0][0]

        refined_points = self.refine_line(route, 10)
        for point in refined_points:
            cell_x, cell_y = self.determine_cell(point, cell_width, cell_height)

            # IF it is already 1, we want to retain it, so doing an or
            occupancy[cell_y][cell_x] = (
                self.inside_cell(point, cell_x, cell_y, grid_x, grid_y)
                or occupancy[cell_y][cell_x]
            )

        return occupancy

    def get_label_locations(self, np_routes, closest_indices, occupancy):
        label_dict = {}
        for it, route in enumerate(np_routes):
            closest_to_center_index = closest_indices[it]
            # For now, all we will do is fill up the closes non-occupied cell
            route_point = route[closest_to_center_index]
            cell_x, cell_y = self.determine_cell(
                route_point, self.cell_width, self.cell_height
            )
            # ToDo: This does not take aesthetic constraints into mind
            if not occupancy[cell_y][cell_x]:
                label_dict[it] = {
                    "point_x": route_point[0],
                    "point_y": route_point[1],
                    "position": "bottom-right",
                }
                occupancy[cell_y][cell_x] = 1

            elif not occupancy[cell_y][cell_x - 1]:
                label_dict[it] = {
                    "point_x": route_point[0],
                    "point_y": route_point[1],
                    "position": "bottom-left",
                }
                occupancy[cell_y][cell_x - 1] = 1

            elif not occupancy[cell_y - 1][cell_x]:
                label_dict[it] = {
                    "point_x": route_point[0],
                    "point_y": route_point[1],
                    "position": "top-right",
                }
                occupancy[cell_y - 1][cell_x] = 1

            elif not occupancy[cell_y - 1][cell_x - 1]:
                label_dict[it] = {
                    "point_x": route_point[0],
                    "point_y": route_point[1],
                    "position": "top-left",
                }
                occupancy[cell_y - 1][cell_x - 1] = 1
            else:
                raise NotImplementedError("This has not been implemented yet")

        return label_dict

    def write_label_locations(self, output_path):
        # ToDo: We should read each line directly as numpy arrays

        grid_x, grid_y = self.grid_x, self.grid_y

        # A box is defined by x[i], x[i+1], y[i], y[i+1]
        # For this box we determine if there are points or other boxes
        # within this box
        # We only want to put occupancy as 1 if a line is strictly inside a box
        # We cannot iterate over the line, so we refine the line and iterate over the points
        occupancy = np.zeros_like(grid_x)

        # For points in each polyline, iterate over them and set occupancy to 1
        # if the refined version of the lines lies inside a box
        for route in self.routes:
            occupancy = self.get_occupancy(route, grid_x, grid_y, occupancy)

        # Now using occupancy we determine what cells are available close to the mid point
        # We could try reusing the refined points to shift slightly in either direction
        # and determine an empty cell close by
        # For now, we just create a dict for this

        label_dict = self.get_label_locations(
            self.routes, self.closest_indices, occupancy
        )

        with open(output_path, "w") as fp:
            for it in range(len(self.routes)):
                fp.write(
                    f"""{label_dict[it]["point_x"]} {label_dict[it]["point_y"]} {label_dict[it]["position"]}\n"""
                )

        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)

    sol = Solution(parsed_routes)
    sol.write_label_locations(args.output_path)
