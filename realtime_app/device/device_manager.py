import logging

import numpy as np

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

BoardShim.disable_board_logger()

log = logging.getLogger(__name__)

# Device name → BoardShim board ID
_NAME_TO_BOARD = {
    "synthetic": BoardIds.SYNTHETIC_BOARD,
    "cyton":     BoardIds.CYTON_BOARD,
}


class DeviceManager:
    """Encapsulates BoardShim hardware I/O.

    View layer calls connect_device / disconnect / start_stream / stop_stream.
    This class handles all BrainFlow calls and writes state to ConfigDevice.
    """

    def __init__(self, config_device=None, config_time_domain=None):
        self._config_device = config_device
        self._config_time_domain = config_time_domain
        self._board_id = -1
        self._board: BoardShim | None = None
        self._streaming = False

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
        if self._config_device is None:
            return
        if self.is_connected:
            return

        board_id = _NAME_TO_BOARD.get(name)
        if board_id is None:
            self._config_device.error_message = f"Unknown device: {name}"
            return

        params = BrainFlowInputParams()
        params.timeout = 1000  # ms, 0 = no timeout
        if port:
            params.serial_port = port
        # params.other_info = str(sampling_rate)

        board = None
        try:
            board = BoardShim(board_id, params)
            board.prepare_session()
        except Exception as e:
            log.exception("Failed to connect to %s", name)
            if board is not None:
                try:
                    board.release_session()
                except Exception:
                    pass
            self._config_device.error_message = str(e)
            return

        self._board = board
        self._board_id = board_id
        self._streaming = False
        self._config_device.is_connected = True
        self._config_device.error_message = ""
        if self._config_time_domain is not None:
            self._config_time_domain.channels = {name: True for name in self.eeg_names}
            log.info("Updated config_time_domain.channels: %s",
                     self._config_time_domain.channels)
        log.info("Connected to %s (board_id=%s, port=%s)", name, board_id, port or "N/A")

    def disconnect(self):
        """Release the board session."""
        if not self.is_connected:
            return
        try:
            if self.is_streaming:
                self._board.stop_stream()
                self._streaming = False
            self._board.release_session()
        except Exception:
            log.exception("Error releasing board session")
        finally:
            self._board = None
            self._board_id = -1
            self._config_device.is_connected = False
            self._config_device.is_streaming = False
            log.info("Disconnected from device")

    def start_stream(self, buffer_size: int | None = None):
        """Start data streaming.

        Args:
            buffer_size: Size of internal ring buffer. None uses BrainFlow default.
        """
        if not self.is_connected:
            return
        if self.is_streaming:
            return
        try:
            if buffer_size is None:
                self._board.start_stream()
            else:
                self._board.start_stream(buffer_size)
            self._streaming = True
            self._config_device.is_streaming = True
            log.info("Stream started")
        except Exception as e:
            log.exception("Failed to start stream")
            self._config_device.error_message = str(e)

    def stop_stream(self):
        """Stop data streaming."""
        if not self.is_connected:
            return
        if not self.is_streaming:
            return
        try:
            self._board.stop_stream()
            self._streaming = False
            self._config_device.is_streaming = False
            log.info("Stream stopped")
        except Exception as e:
            log.exception("Failed to stop stream")
            self._config_device.error_message = str(e)

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

    @property
    def is_streaming(self) -> bool:
        return self._streaming

    # ------------------------------------------------------------------
    # device info
    # ------------------------------------------------------------------
    @property
    def device_name(self) -> str:
        return BoardShim.get_device_name(self._board_id)
    
    @property
    def eeg_channels(self) -> list[str]:
        if self._board is None:
            return []
        return BoardShim.get_eeg_channels(self._board_id)
    
    @property
    def eeg_names(self) -> list[str]:
        if self._board is None:
            return []
        result = BoardShim.get_eeg_names(self._board_id)
        if isinstance(result, list):
            return result
        return result.split(",")

    @property
    def sampling_rate(self) -> int:
        if self._board is None:
            return 0
        return BoardShim.get_sampling_rate(self._board_id)
    
    @property
    def board_descr(self) -> str:
        if self._board is None:
            return ""
        result = BoardShim.get_board_descr(self._board_id)
        result["device_name"] = self.device_name
        return result


    # ------------------------------------------------------------------
    # get data
    # ------------------------------------------------------------------     
    def get_board_data(self) -> np.ndarray:
        if not self.is_connected:
            raise RuntimeError("Device not connected")
        if not self.is_streaming:
            raise RuntimeError("Stream not started")
        return self._board.get_board_data()

    def get_current_board_data(self, num_samples: int = 100) -> np.ndarray:
        if not self.is_connected:
            raise RuntimeError("Device not connected")
        if not self.is_streaming:
            raise RuntimeError("Stream not started")
        return self._board.get_current_board_data(num_samples)
        
