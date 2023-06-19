# Run: python plot_routes.py routes.txt labels.txt
import argparse
import matplotlib.pyplot


def parse_routes(path):
    parsed_routes = []
    with open(path) as file:
        lines = [line.strip() for line in file.readlines()]

        for line in lines:
            line_coords = [int(i) for i in line.split()]
            line_coords = [([line_coords[i], line_coords[i + 1]]) for i in range(0, len(line_coords), 2)]
            parsed_routes.append(line_coords)

    return parsed_routes


def parse_labels(path, zoom):
    parsed_labels = []
    with open(path) as file:
        lines = [line.strip() for line in file.readlines()]

        for line in lines:
            label_info = line.split()
            x = float(label_info[0])
            y = float(label_info[1])
            orient = label_info[2]
            parsed_labels.append(get_label(x, y, orient, 100 * zoom, 50 * zoom))

    return parsed_labels


def get_label(x, y, orient, width=100, height=50):
    if orient == 'bottom-right':
        return [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)]
    elif orient == 'bottom-left':
        return [(x, y), (x, y + height), (x - width, y + height), (x - width, y), (x, y)]
    elif orient == 'top-left':
        return [(x, y), (x - width, y), (x - width, y - height), (x, y - height), (x, y)]
    elif orient == 'top-right':
        return [(x, y), (x, y - height), (x + width, y - height), (x + width, y), (x, y)]
    else:
        raise Exception(f'Invalid label orientation of: {orient}')


def display_results(routes_path, labels_path, zoom_levels):
    for zoom_level in zoom_levels:
        routes = parse_routes(routes_path)
        labels = parse_labels(labels_path, zoom=zoom_level)

        f, ax = matplotlib.pyplot.subplots()

        # Margins should be at least 0.05 to avoid tight fit at level 1.
        ax.margins(max(0.05, (zoom_level - 1) / 2), max(0.05, (zoom_level - 1) / 2))

        for route in routes:
            matplotlib.pyplot.plot(*zip(*route), '-')

        for label in labels:
            matplotlib.pyplot.plot(*zip(*label), 'k-')

        matplotlib.pyplot.title(f'Results at zoom level {zoom_level}')
        matplotlib.pyplot.gca().invert_yaxis()
        matplotlib.pyplot.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("routes_path", type=str)
    parser.add_argument("labels_path", type=str)
    args = parser.parse_args()

    display_results(args.routes_path, args.labels_path, [1, 2, 4])
