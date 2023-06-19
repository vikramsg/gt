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

        # Label width and height
        self.width = 200
        self.height = 100

        # Tolerance for checking overlap
        self.tolerance = 50

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

        # We may have to refine points for a coarse line
        if np.any(
            (line_points[:, 0] < rect_right)
            & (line_points[:, 0] > rect_left)
            & (line_points[:, 1] < rect_bottom)
            & (line_points[:, 1] > rect_top)
        ):
            return 1
        else:
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

    def check_rectangle_overlap(self, rect_left, rect_top, rect_width, rect_height):
        num_rectangles = len(rect_left)
        if num_rectangles == 1:
            return False

        for i in range(num_rectangles):
            left_i = rect_left[i]
            top_i = rect_top[i]
            right_i = left_i + rect_width
            bottom_i = top_i + rect_height

            for j in range(i + 1, num_rectangles):
                left_j = rect_left[j]
                top_j = rect_top[j]
                right_j = left_j + rect_width
                bottom_j = top_j + rect_height

                # Check if rectangles i and j overlap
                if not (
                    left_i > right_j
                    or right_i < left_j
                    or top_i > bottom_j
                    or bottom_i < top_j
                ):
                    return 1

        return 0

    def write_label_locations(self, output_path):
        label_dict = {}
        rect_left = []
        rect_top = []
        for it, route in enumerate(self.routes):
            counter = 0
            while True:
                # Move away from center point if we don't find a match
                closest_point = route[self.closest_indices[it] + counter]
                rectangle_origin = self.get_route_label_origin(
                    closest_point, self.routes
                )

                if rectangle_origin is not None:
                    rect_left.append(rectangle_origin[0] - self.tolerance)
                    rect_top.append(rectangle_origin[1] - self.tolerance)
                    check_overlap = self.check_rectangle_overlap(
                        rect_left,
                        rect_top,
                        self.width + self.tolerance,
                        self.height + self.tolerance,
                    )
                    if check_overlap:
                        rect_left.pop()
                        rect_top.pop()
                    else:
                        break

                if counter > 0:
                    # We want to both try positive and Negative direction
                    closest_point = route[self.closest_indices[it] - counter]
                    rectangle_origin = self.get_route_label_origin(
                        closest_point, self.routes
                    )
                    if rectangle_origin is not None:
                        rect_left.append(rectangle_origin[0] - self.tolerance)
                        rect_top.append(rectangle_origin[1] - self.tolerance)
                        check_overlap = self.check_rectangle_overlap(
                            rect_left,
                            rect_top,
                            self.width + self.tolerance,
                            self.height + self.tolerance,
                        )
                        if check_overlap:
                            rect_left.pop()
                            rect_top.pop()
                        else:
                            break

                counter += 1

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
