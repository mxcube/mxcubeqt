import math


HEADER = "<p><h1> Data Collection - Result Summary </h1></br></p>"


def image_table(paths):
    COLUMNS = 4
    html_str = "<table border='1'>"
    rows = int(math.ceil(float(len(paths)) / float(COLUMNS)))
    paths.reverse()

    for row_num in range(0, rows):
        html_str += "<tr>"

        for i in range(0, COLUMNS):
            if len(paths):
                path = paths.pop()
                
                img_name = None
                try:
                    img_name = path.split('/')[-1].split('.')[0]
                except:
                    pass

                html_str += "<td alignment='center'><img src='%s'></img><br/>%s</td>" %(path, img_name)
            else:
                if rows > 1:
                    html_str += "<td></td>"

        
        html_str += "</tr>"

    html_str += "</table>"
    paths.reverse()
    
    return html_str
    

def html_report(data_collection):
    paths = data_collection.acquisitions[0].get_preview_image_paths()

    if data_collection.acquisitions[0].acquisition_parameters.shutterless:
        temp [paths[0], paths[-1]]
        paths = temp
    
    image_path = data_collection.acquisitions[0].path_template.get_image_path()

    image_path = image_path.replace('%04d', '####')
    image_path =  "<p><h3>Image path: %s</br></h3></p>" % image_path
    
    
    return HEADER + image_path + image_table(paths)
