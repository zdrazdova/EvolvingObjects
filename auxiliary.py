from sympy.geometry import Line, Ray, Point, Segment

from custom_classes import Environment, Component

def print_ray(ray: Ray):
    x1 = round(float(ray.p1.x),2)
    y1 = round(float(ray.p1.y),2)
    x2 = round(float(ray.p2.x),2)
    y2 = round(float(ray.p2.y),2)
    print("Ray ", "X: ", x1,"Y: ", y1, " - ", "X: ", x2,"Y: ", y2)


def print_point(point: Point):
    x = round(float(point.x),2)
    y = round(float(point.y),2)
    print("X: ", x,"Y: ", y)


def print_point_array(points: [Point]):
    outcome = "[ "
    for point in points:
        x = str(round(float(point.x),2))
        y = str(round(float(point.y),2))
        outcome += "(" + x + ", " + y + "), "
    outcome += "]"
    print(outcome)


def draw(ind: Component, name: str, env: Environment):
    svg_name = "img/img-" + str(name).zfill(2) + ".svg".format(name)
    # Generating drawing in SVG format
    with open(svg_name, "w") as f:
        x_offset = 1000
        if (env.road_start < 0):
            x_offset += abs(env.road_start)
        y_offset = 1000
        f.write(
            '<svg width="{0}" height="{1}">'.format(env.road_end + x_offset + 1000, abs(env.road_depth) + 2000))
        f.write('<rect width="{0}" height="{1}" fill="black"/>'.format(env.road_end + x_offset + 1000,
                                                                       abs(env.road_depth) + 2000))
        # f.write('<rect x="950" y="950" width="100" height="4070" fill="gray"/>') #stožár
        # f.write('<rect x="100" y="950" width="900" height="70" fill="gray"/>') # výložník + lampa

        for ray in []:
            r = ray.ray
            alpha = str(round(ray.intensity, 3))
            color = "(250, 216, 22)"
            f.write(
                '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                        float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color, alpha))

        for ray in ind.original_rays:
            array = ray.ray_array
            alpha = str(round(ray.intensity, 3))
            color = "(250, 216, 22)"
            for r in array[:-1]:
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                    .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                            float(r.points[1].x) + x_offset, - float(r.points[1].y) + y_offset, color, alpha))
            r = array[-1]
            intersection = env.road.intersection(r)
            if intersection:
                intersection = intersection[0]
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>\n'
                        .format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(intersection.x) + x_offset, - float(intersection.y) + y_offset,
                                color, alpha))
            else:
                x_diff = float(r.points[1].x - r.points[0].x) * 50
                y_diff = float(r.points[1].y - r.points[0].y) * 50
                f.write(
                    '<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:rgb{4};stroke-opacity:{5};stroke-width:10"/>'
                    '\n'.format(float(r.points[0].x) + x_offset, - float(r.points[0].y) + y_offset,
                                float(r.points[0].x) + x_offset + x_diff,
                                -float(r.points[0].y) + y_offset - y_diff,
                                color, alpha))

        f.write('<rect x="{0}" y="{1}" width="{2}" height="50" fill="gray"/>'
                .format(env.road.p1.x + x_offset, -env.road.p1.y + y_offset,
                        (env.road.p2.x - env.road.p1.x)))  # road

        left_border = env.road_start
        segments_size = env.road_length / env.road_sections

        for segment in range(env.road_sections):
            alpha = str(round(ind.segments_intensity[segment], 3))
            color = "(250, 6, 22)"

            f.write('<rect x="{0}" y="{1}" width="{2}" height="50" style="fill:rgb{3};fill-opacity:{4};"/>'
                    .format(left_border + x_offset, -env.road.p1.y + y_offset,
                            (segments_size), color, alpha))
            left_border += segments_size

        # Base
        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
            ind.base.p1.x + x_offset, -ind.base.p1.y + y_offset,
            ind.base.p2.x + x_offset, -ind.base.p2.y + y_offset))

        # pravá laple
        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
            ind.base.p2.x + x_offset, -ind.base.p2.y + y_offset,
            float(ind.right_segment.p2.x) + x_offset, float(-ind.right_segment.p2.y) + y_offset))

        # levá laple
        f.write('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="stroke:gray;stroke-width:40"/>'.format(
            ind.base.p1.x + x_offset, -ind.base.p1.y + y_offset,
            float(ind.left_segment.p2.x) + x_offset, float(-ind.left_segment.p2.y) + y_offset))

        f.write('</svg>')
