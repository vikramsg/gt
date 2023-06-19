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
        self.width = 100
        self.height = 50

    def _route_bbox(self, route):
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

    def _bbox(self, routes):
        """Get bbox of all routes

        Args:
            routes (List of 2D numpy.array): List of all Polylines (each is numpy array)

        Returns:
            bbox: Tuple of size 4, with first 2 coords as left bottom
                and last 2 as right top

        ToDo: These are all ints, we should use Int specialization
        """
        bbox_routes = self._route_bbox(routes[0])
        if len(routes) > 1:
            for route in routes:
                bbox_route = self._route_bbox(route)
                bbox_routes = (
                    np.min([bbox_routes[0], bbox_route[0]]),
                    np.min([bbox_routes[1], bbox_route[1]]),
                    np.max([bbox_routes[2], bbox_route[2]]),
                    np.max([bbox_routes[3], bbox_route[3]]),
                )

        return bbox_routes

    def bbox_center(self):
        bbox = self._bbox(self.routes)

        return 0.5 * (bbox[0] + bbox[2]), 0.5 * (bbox[1] + bbox[3])

    def line_rectangle_intersection(
        self, x1, y1, x2, y2, rect_left, rect_top, rect_width, rect_height
    ):
        rect_right = rect_left + rect_width
        rect_bottom = rect_top + rect_height

        if x1 == x2:
            if rect_left < x1 < rect_right or rect_left < x2 < rect_right:
                if (
                    y1 < rect_bottom < y2
                    or y2 < rect_bottom < y1
                    or y1 < rect_top < y2
                    or y2 < rect_top < y1
                ):
                    return 1

        else:
            # Calculate the slope of the line segment
            m = (y2 - y1) / (x2 - x1)

            # Calculate the y-intercept of the line segment
            b = y1 - m * x1

            # Check intersection with left edge of the rectangle
            if x1 <= rect_left <= x2 or x2 <= rect_left <= x1:
                y = m * rect_left + b
                if rect_top < y < rect_bottom:
                    return 1

            # Check intersection with right edge of the rectangle
            if x1 <= rect_right <= x2 or x2 <= rect_right <= x1:
                y = m * rect_right + b
                if rect_top < y < rect_bottom:
                    return 1

            # Check intersection with top edge of the rectangle
            if y1 <= rect_top <= y2 or y2 <= rect_top <= y1:
                if m != 0:
                    x = (rect_top - b) / m
                    if rect_left < x < rect_right:
                        return 1

            # Check intersection with bottom edge of the rectangle
            if y1 <= rect_bottom <= y2 or y2 <= rect_bottom <= y1:
                if m != 0:
                    x = (rect_bottom - b) / m
                    if rect_left < x < rect_right:
                        return 1

            # No intersection
            return 0

    def route_points_closest_to_center(self, bbox_center, routes):
        closest_indices = []
        for route in routes:
            distances = np.linalg.norm(route - bbox_center, axis=1)
            closest_index = np.argmin(distances)
            closest_indices.append(closest_index)

        return closest_indices

    def routes_rectangle_intersection_at_point(self, routes, origin, width, height):
        flag = 1
        while flag:
            counter = 0
            route = routes[counter]
            for it, point in enumerate(route[:-1]):
                if self.line_rectangle_intersection(
                    point[0],
                    point[1],
                    route[it + 1][0],
                    route[it + 1][1],
                    origin[0],
                    origin[1],
                    width,
                    height,
                ):
                    flag = 0
                    break
            counter += 1
            if counter >= len(routes):
                break
        return flag

    def find_intersection_with_4_rectangles_at_point(
        self, origin, width, height, routes
    ):
        if self.routes_rectangle_intersection_at_point(
            routes, (origin[0] - width, origin[1] - height), width, height
        ):
            return (origin[0] - width, origin[1] - height)
        if self.routes_rectangle_intersection_at_point(
            routes, (origin[0], origin[1] - height), width, height
        ):
            return (origin[0], origin[1] - height)
        if self.routes_rectangle_intersection_at_point(
            routes, (origin[0] - width, origin[1]), width, height
        ):
            return (origin[0] - width, origin[1])
        if self.routes_rectangle_intersection_at_point(routes, origin, width, height):
            return origin

        # Return None if there is an intersection
        return None

    def get_route_label_origin(self, point, routes):
        return self.find_intersection_with_4_rectangles_at_point(
            point, self.width, self.height, routes
        )

    def get_label_position(self, route_point, rectangle_point):
        if route_point[0] > rectangle_point[0]:
            suffix = "left"
        else:
            suffix = "right"
        if route_point[1] > rectangle_point[1]:
            prefix = "top"
        else:
            prefix = "bottom"

        return f"{prefix}-{suffix}"

    def write_label_locations(self, output_path):
        for it, route in enumerate(self.routes):
            closest_point = route[self.closest_indices[it]]
            rectangle_origin = self.get_route_label_origin(closest_point, self.routes)
            print(self.get_label_position(closest_point, rectangle_origin))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)

    sol = Solution(parsed_routes)
    sol.write_label_locations(args.output_path)
