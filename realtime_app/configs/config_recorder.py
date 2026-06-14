from traitlets.config import Configurable
from traitlets import Bool

class ConfigRecorder(Configurable):
    """Recorder configuration."""
    record_raw = Bool(False, help="Record raw signal.").tag(config=True)
    record_processed = Bool(False, help="Record processed signal.").tag(config=True)
