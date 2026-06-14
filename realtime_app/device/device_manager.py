import logging

from PySide6.QtCore import QObject, Signal

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams

log = logging.getLogger(__name__)

# Device name → BoardShim board ID
_NAME_TO_BOARD = {
    "synthetic": brainflow.board_shim.BoardIds.SYNTHETIC_BOARD,
    "cyton":     brainflow.board_shim.BoardIds.CYTON_BOARD,
}


class DeviceManager(QObject):
    """Encapsulates BoardShim hardware I/O behind Qt signals.

    View layer calls connect_device / disconnect / start_stream / stop_stream.
    This class handles all BrainFlow calls and emits status signals.
    """

    connected = Signal(int)       # board_id
    disconnected = Signal()
    error_occurred = Signal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._board_id = -1
        self._board: BoardShim | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def connect_device(self, name: str, port: str = "", sampling_rate: int = 250):
        """Connect to the device specified by *name* (e.g. 'synthetic', 'cyton').

        Args:
            name: Device name matching a key in _NAME_TO_BOARD.
            port: Serial port string (empty for synthetic board).
            sampling_rate: Desired sampling rate in Hz.
        """
        board_id = _NAME_TO_BOARD.get(name)
        if board_id is None:
            self.error_occurred.emit(f"Unknown device: {name}")
            return

        params = BrainFlowInputParams()
        if port:
            params.serial_port = port
        # params.other_info = str(sampling_rate)

        try:
            self._board = BoardShim(board_id, params)
            self._board.prepare_session()
            self._board_id = board_id
            log.info("Connected to %s (board_id=%s, port=%s)", name, board_id, port or "N/A")
            self.connected.emit(board_id)
        except Exception as e:
            log.exception("Failed to connect to %s", name)
            self._board = None
            self.error_occurred.emit(str(e))

    def disconnect(self):
        """Release the board session."""
        if self._board is not None:
            try:
                self._board.release_session()
            except Exception:
                log.exception("Error releasing board session")
            finally:
                self._board = None
                self._board_id = -1
                self.disconnected.emit()
                log.info("Disconnected from device")

    def start_stream(self):
        """Start data streaming."""
        if self._board is not None:
            try:
                self._board.start_stream()
                log.info("Stream started")
            except Exception as e:
                log.exception("Failed to start stream")
                self.error_occurred.emit(str(e))

    def stop_stream(self):
        """Stop data streaming."""
        if self._board is not None:
            try:
                self._board.stop_stream()
                log.info("Stream stopped")
            except Exception as e:
                log.exception("Failed to stop stream")
                self.error_occurred.emit(str(e))

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def board(self) -> BoardShim | None:
        return self._board

    @property
    def board_id(self) -> int:
        return self._board_id

    @property
    def is_connected(self) -> bool:
        return self._board is not None
