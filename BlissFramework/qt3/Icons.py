from qt import *
import os.path

ICONS_DIR = os.path.join(os.path.dirname(__file__), 'Icons')

def load(iconName):
    """Try to load an icon from file and return the QPixmap object"""
    filename = os.path.join(ICONS_DIR, iconName)

    if not os.path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if os.path.exists(f):
                filename = f
                break
        
    try:
        icon = QPixmap(filename)
    except:
        return QPixmap(os.path.join(ICONS_DIR, 'esrf_logo.png'))
    else:
        if icon.isNull():
            return QPixmap(os.path.join(ICONS_DIR, 'esrf_logo.png'))
        else:
            return icon


def getIconPath(iconName):
    """Return path to an icon"""
    filename = os.path.join(ICONS_DIR, iconName)

    if not os.path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if os.path.exists(f):
                filename = f
                break
    
    if os.path.exists(filename):
        return filename
        

