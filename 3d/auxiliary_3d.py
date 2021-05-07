def draw_road(ind: Component3D, name: str):
    svg_name = "img/img-" + str(name).zfill(2) + ".svg".format(name)
    # Generating drawing in SVG format
    with open(svg_name, "w") as f:
        x_offset = 8000
        z_offset = 4000
        color = "(250, 216, 22)"
        f.write('<svg width="{0}" height="{1}">\n'.format(16000, 8000))
        f.write('<rect width="{0}" height="{1}" fill="black"/>\n'.format(16000, 8000))
        for ray in ind.original_rays:
            array = ray.ray_array
            alpha = str(round(ray.intensity, 3))
            color = "(250, 216, 22)"
            if ray.road_intersection:
                #print(float(ray.road_intersection[0]), float(ray.road_intersection[1]), float(ray.road_intersection[2]))
                x_int = (float(ray.road_intersection[0]))
                y_int = (float(ray.road_intersection[1]))
                z_int = (float(ray.road_intersection[2]))
                f.write(f"<circle cx = \"{x_int+x_offset}\" cy = \"{z_int+z_offset}\" r = \"40\" style=\"fill:rgb{color};fill-opacity:{alpha};\" />\n")

        f.write('</svg>')
