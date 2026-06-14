from traitlets.config import Configurable
from traitlets import Int

class ConfigRecorder(Configurable):
    """Recorder configuration."""
    record_raw = Bool(True, help="Record raw signal.").tag(config=True)
    record_processed = Bool(True, help="Record processed signal.").tag(config=True)
