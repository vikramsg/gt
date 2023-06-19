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
        self, line_points, rect_left, rect_top, rect_width, rect_height
    ):
        rect_right = rect_left + rect_width
        rect_bottom = rect_top + rect_height

        x1, y1 = line_points[:-1].T
        x2, y2 = line_points[1:].T

        vertical_mask = np.abs(x1 - x2) < 1e-8
        horizontal_mask = np.abs(y1 - y2) < 1e-8

        # Check for vertical line segments
        if np.any(vertical_mask):
            vertical_segments_mask = np.logical_and(
                rect_left < x1[vertical_mask], rect_right > x1[vertical_mask]
            )
            vertical_segments_mask &= np.logical_and(
                rect_top < np.maximum(y1[vertical_mask], y2[vertical_mask]),
                rect_bottom > np.minimum(y1[vertical_mask], y2[vertical_mask]),
            )
            if np.any(vertical_segments_mask):
                return 1

        # Check for horizontal line segments
        if np.any(horizontal_mask):
            horizontal_segments_mask = np.logical_and(
                rect_top < y1[horizontal_mask], rect_bottom > y1[horizontal_mask]
            )
            horizontal_segments_mask &= np.logical_and(
                rect_left < np.maximum(x1[horizontal_mask], x2[horizontal_mask]),
                rect_right > np.minimum(x1[horizontal_mask], x2[horizontal_mask]),
            )
            if np.any(horizontal_segments_mask):
                return 1

        # Calculate the slope of non-vertical, non-horizontal line segments
        non_vertical_horizontal_mask = np.logical_and(~vertical_mask, ~horizontal_mask)
        slope = (
            y2[non_vertical_horizontal_mask] - y1[non_vertical_horizontal_mask]
        ) / (x2[non_vertical_horizontal_mask] - x1[non_vertical_horizontal_mask])
        intercept = (
            y1[non_vertical_horizontal_mask] - slope * x1[non_vertical_horizontal_mask]
        )

        # Check intersection with left edge of the rectangle
        left_mask = np.logical_and(
            x1[non_vertical_horizontal_mask] < rect_left,
            x2[non_vertical_horizontal_mask] > rect_left,
        )
        left_mask &= np.logical_and(
            rect_top < slope * rect_left + intercept,
            slope * rect_left + intercept < rect_bottom,
        )
        if np.any(left_mask):
            return 1

        # Check intersection with right edge of the rectangle
        right_mask = np.logical_and(
            x1[non_vertical_horizontal_mask] < rect_right,
            x2[non_vertical_horizontal_mask] > rect_right,
        )
        right_mask &= np.logical_and(
            rect_top < slope * rect_right + intercept,
            slope * rect_right + intercept < rect_bottom,
        )
        if np.any(right_mask):
            return 1

        # Check intersection with top edge of the rectangle
        top_mask = np.logical_and(
            y1[non_vertical_horizontal_mask] < rect_top,
            y2[non_vertical_horizontal_mask] > rect_top,
        )
        top_mask &= np.logical_and(
            rect_left < (rect_top - intercept) / slope,
            (rect_top - intercept) / slope < rect_right,
        )
        if np.any(top_mask):
            return 1

        # Check intersection with bottom edge of the rectangle
        bottom_mask = np.logical_and(
            y1[non_vertical_horizontal_mask] < rect_bottom,
            y2[non_vertical_horizontal_mask] > rect_bottom,
        )
        bottom_mask &= np.logical_and(
            rect_left < (rect_bottom - intercept) / slope,
            (rect_bottom - intercept) / slope < rect_right,
        )
        if np.any(bottom_mask):
            return 1

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
        for route in routes:
            if self.line_rectangle_intersection(
                route,
                origin[0],
                origin[1],
                width,
                height,
            ):
                flag = 0
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
        label_dict = {}
        for it, route in enumerate(self.routes):
            closest_point = route[self.closest_indices[it]]
            rectangle_origin = self.get_route_label_origin(closest_point, self.routes)
            label_position = self.get_label_position(closest_point, rectangle_origin)
            label_dict[it] = {
                "point_x": closest_point[0],
                "point_y": closest_point[1],
                "position": label_position,
            }

        with open(output_path, "w") as fp:
            for it in range(len(self.routes)):
                fp.write(
                    f"""{label_dict[it]["point_x"]} {label_dict[it]["point_y"]} {label_dict[it]["position"]}\n"""
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)

    sol = Solution(parsed_routes)
    sol.write_label_locations(args.output_path)
