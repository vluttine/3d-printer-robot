from xml.dom import minidom
from svg.path import parse_path


def parse_svg(filename):
    #filename = "./piirros2.svg"
    doc = minidom.parse(filename)  # parseString also exists
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]

    pth = str(path_strings[0])

    path1 = parse_path(pth)

    coord = []
    for i in range(0, 501, 1):
        j = float(i) / 500
        coord.append((path1.point(j).real, path1.point(j).imag))

    #for pair in coord:
        #print pair

    return coord

if __name__ == "__main__":
    points = parse_svg("./piirros2.svg")
    #for pair in points:
    #    print(pair)
        #print(pair[0])
    print points
    #print(points[0])
