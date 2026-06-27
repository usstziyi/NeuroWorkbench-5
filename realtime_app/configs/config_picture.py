from traitlets.config import Configurable
from traitlets import Bool, Unicode

class ConfigPicture(Configurable):
    trigger = Bool(False, help="Export picture").tag(config=True)
    export_pic_dir = Unicode("./outputs", help="Export picture directory").tag(config=True)
    date_format = Unicode("%Y_%m_%d_%H_%M_%S", help="Date format").tag(config=True)
    suffix = Unicode(".svg", help="Export suffix").tag(config=True)
