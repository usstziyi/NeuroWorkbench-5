import logging

import numpy as np

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

BoardShim.disable_board_logger()

# Device name → BoardShim board ID
_NAME_TO_BOARD = {
    "synthetic": BoardIds.SYNTHETIC_BOARD,
    "cyton":     BoardIds.CYTON_BOARD,
}


class DeviceManager:
    """Encapsulates BoardShim hardware I/O.

    View layer calls connect / disconnect / start_stream / stop_stream.
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

    def connect(self, name: str, port: str = "", sampling_rate: int = 250):
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
            print(f"[dm]Failed to connect to {name}: {e}")
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
        self._config_device.device_info = self.board_descr

        if self._config_time_domain is not None:
            self._config_time_domain.channels = {name: True for name in self.eeg_names}
        print(f"[dm]Connected to {name} with port {port}")

    def disconnect(self):
        """Release the board session."""
        if not self.is_connected:
            return
        try:
            self.stop_stream()
            self._board.release_session()
        except Exception:
            print("[dm]Failed to releasing board session")
        finally:
            self._board = None
            self._board_id = -1
            self._config_device.is_connected = False
            self._config_device.is_streaming = False
            self._config_device.device_info = {}
            print("[dm]Disconnected from device")

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
            print("[dm]Stream started")
        except Exception as e:
            print(f"[dm]Failed to start stream: {e}")
            self._config_device.error_message = str(e)

    def stop_stream(self):
        """Stop data streaming."""
        if not self.is_connected:
            return
        if not self.is_streaming:
            return
        try:
            self._streaming = False
            self._config_device.is_streaming = False
            self._board.stop_stream()
            print("[dm]Stream stopped")
        except Exception as e:
            print(f"[dm]Failed to stop stream: {e}")
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
        """获取上次调用以来累积的所有新数据，并推进已读游标。

        消费式读取：只推进内部已读游标，不删除数据。数据仍在环形缓冲区中，
        get_current_board_data 依然能读到。两者操作独立指针，可安全并发调用。
        非阻塞，仅做内存拷贝。

        Returns:
            numpy 数组，形状为 (通道数, 数据点数)。无新数据时返回空数组。
        """
        if not self.is_connected:
            raise RuntimeError("Device not connected")
        if not self.is_streaming:
            raise RuntimeError("Stream not started")
        return self._board.get_board_data()

    def get_current_board_data(self, num_samples: int = 100) -> np.ndarray:
        """获取环形缓冲区尾部最近 num_samples 个样本，不清空缓冲区。

        窥视式读取：直接定位环尾倒数 n 个，不看已读游标。与 get_board_data
        操作独立指针，可安全并发调用。非阻塞，仅做内存拷贝。

        Args:
            num_samples: 要获取的样本数。

        Returns:
            numpy 数组，形状为 (通道数, 数据点数)。缓冲区数据不足时返回实际有的量。
        """
        if not self.is_connected:
            raise RuntimeError("Device not connected")
        if not self.is_streaming:
            raise RuntimeError("Stream not started")
        return self._board.get_current_board_data(num_samples)

    def peek_seconds(self, seconds: float) -> np.ndarray:
        """获取缓冲区中最近 seconds 秒的板载数据，不清空缓冲区。

        窥视式读取（基于 get_current_board_data），可重复调用获取同一窗口。

        Args:
            seconds: 要获取的时间窗口长度（秒）。
        """
        n = int(seconds * self.sampling_rate)
        return self.get_current_board_data(n)

