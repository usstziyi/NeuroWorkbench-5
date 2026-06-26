from traitlets.config import Configurable
from traitlets import Bool, Unicode

class ConfigRecorder(Configurable):
    """Recorder configuration."""
    # 是否启用记录器
    enable = Bool(False, help="Enable recorder.").tag(config=True)
    # 记录文件保存目录
    recordings_dir = Unicode("./recordings", help="Directory to save recordings.").tag(config=True)
    # 文件名前缀
    prefix = Unicode("recording", help="Prefix for recording files.").tag(config=True)
    # 主设备
    master_device = Unicode("cyton", help="Master device for recording.").tag(config=True)
    # 日期格式年_月_日_时_分_秒
    date_format = Unicode("%Y_%m_%d_%H_%M_%S", help="Date format for recording files.").tag(config=True)
    # 后缀名csv
    suffix = Unicode("csv", help="Suffix for recording files.").tag(config=True)
