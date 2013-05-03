import math
import queue_model


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
    paths = queue_model.QueueModelFactory.get_context().\
            get_preview_image_paths(data_collection.previous_acquisition)

    image_path = queue_model.QueueModelFactory.get_context().\
                 build_image_path(data_collection.previous_acquisition.\
                                  path_template)

    image_path = image_path.replace('%04d', '####')
    image_path =  "<p><h3>Image path: %s</br></h3></p>" % image_path
    
    
    return HEADER + image_path + image_table(paths)
