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

    def route_points_closest_to_center(self, bbox_center, routes):
        closest_indices = []
        for route in routes:
            distances = np.linalg.norm(route - bbox_center, axis=1)
            closest_index = np.argmin(distances)
            closest_indices.append(closest_index)

        return closest_indices

    def write_label_locations(self, output_path):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    parser.add_argument("output_path", type=str)
    args = parser.parse_args()

    parsed_routes = parse_routes(args.routes_path)

    sol = Solution(parsed_routes)
    sol.write_label_locations(args.output_path)
