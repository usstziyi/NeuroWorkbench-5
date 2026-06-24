# Configuration file for EEG脑机接口信号实时采集分析软件系统.

c = get_config()  # noqa

#------------------------------------------------------------------------------
# BCIRealtimeApp configuration
#------------------------------------------------------------------------------
c.BCIRealtimeApp.description = 'BCIRealtimeApp application for real-time brain-computer interface.'
c.BCIRealtimeApp.log_datefmt = '%Y-%m-%d %H:%M:%S'
c.BCIRealtimeApp.log_format = '[%(name)s]%(highlevel)s %(message)s'
c.BCIRealtimeApp.log_level = 30
c.BCIRealtimeApp.logging_config = {}
c.BCIRealtimeApp.name = 'EEG脑机接口信号实时采集分析软件系统'
c.BCIRealtimeApp.show_config = False
c.BCIRealtimeApp.show_config_json = False
c.BCIRealtimeApp.version = '0.1.0'

#------------------------------------------------------------------------------
# ConfigTheme configuration
#------------------------------------------------------------------------------
c.ConfigTheme.color_mode = 'System'
c.ConfigTheme.theme = 'Fusion'

#------------------------------------------------------------------------------
# ConfigDevice configuration
#------------------------------------------------------------------------------
c.ConfigDevice.name = 'synthetic'
c.ConfigDevice.port = ''

#------------------------------------------------------------------------------
# ConfigFetcher configuration
#------------------------------------------------------------------------------
c.ConfigFetcher.mode = 'full'

#------------------------------------------------------------------------------
# ConfigFilter configuration
#------------------------------------------------------------------------------
c.ConfigFilter.enable = True
c.ConfigFilter.filter_order = 4
c.ConfigFilter.filter_type = 'butterworth'
c.ConfigFilter.highpass = 5.0
c.ConfigFilter.lowpass = 45.0
c.ConfigFilter.method = 'filter_sosfilt_scipy'
c.ConfigFilter.noise_freqs = 50
c.ConfigFilter.notch_order = 2

#------------------------------------------------------------------------------
# ConfigDetrend configuration
#------------------------------------------------------------------------------
c.ConfigDetrend.detrend_type = 'constant'
c.ConfigDetrend.enable = True
c.ConfigDetrend.method = 'detrend_numpy'

#------------------------------------------------------------------------------
# ConfigFFT configuration
#------------------------------------------------------------------------------
c.ConfigFFT.channels = {'Fp1': True, 'Fp2': True, 'C3': True, 'C4': True, 'P7': True, 'P8': True, 'O1': True, 'O2': True}
c.ConfigFFT.db = True
c.ConfigFFT.enable = True
c.ConfigFFT.method = 'fft_brainflow'
c.ConfigFFT.nfft = 512
c.ConfigFFT.smooth_factor = 0.92
c.ConfigFFT.window_type = 'Hamming'

#------------------------------------------------------------------------------
# ConfigViewFreqs configuration
#------------------------------------------------------------------------------
c.ConfigViewFreqs.freqs_range = [0.0, 60.0]
c.ConfigViewFreqs.type = 'FFT_DB'
c.ConfigViewFreqs.y_max = 40.0
c.ConfigViewFreqs.y_min = -66.0

#------------------------------------------------------------------------------
# ConfigViewTime configuration
#------------------------------------------------------------------------------
c.ConfigViewTime.amplitude = 1000.0
c.ConfigViewTime.interval = 50.0
c.ConfigViewTime.seconds = 5

#------------------------------------------------------------------------------
# ConfigRecorder configuration
#------------------------------------------------------------------------------
c.ConfigRecorder.record_processed = False
c.ConfigRecorder.record_raw = False

#------------------------------------------------------------------------------
# ConfigPSD configuration
#------------------------------------------------------------------------------
c.ConfigPSD.cut_seconds = 3
c.ConfigPSD.db = False
c.ConfigPSD.enable = False
c.ConfigPSD.method = 'psd_welch_scipy'
c.ConfigPSD.nperseg = 512
c.ConfigPSD.overlap_ratio = 0.5
c.ConfigPSD.window_type = 'Hann'

#------------------------------------------------------------------------------
# ConfigSpectrogram configuration
#------------------------------------------------------------------------------
c.ConfigSpectrogram.enable = False
c.ConfigSpectrogram.method = 'spectrogram_brainflow'

