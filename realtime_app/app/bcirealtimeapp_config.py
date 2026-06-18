# Configuration file for BCIRealtimeApp.

c = get_config()  # noqa

#------------------------------------------------------------------------------
# BCIRealtimeApp configuration
#------------------------------------------------------------------------------
c.BCIRealtimeApp.description = 'BCIRealtimeApp application for real-time brain-computer interface.'
c.BCIRealtimeApp.log_datefmt = '%Y-%m-%d %H:%M:%S'
c.BCIRealtimeApp.log_format = '[%(name)s]%(highlevel)s %(message)s'
c.BCIRealtimeApp.log_level = 30
c.BCIRealtimeApp.logging_config = {}
c.BCIRealtimeApp.name = 'BCIRealtimeApp'
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
c.ConfigDevice.name = 'cyton'
c.ConfigDevice.port = '/dev/cu.usbmodem12201'
c.ConfigDevice.sampling_rate = 250

#------------------------------------------------------------------------------
# ConfigFilter configuration
#------------------------------------------------------------------------------
c.ConfigFilter.enable = True
c.ConfigFilter.highpass = 5.0
c.ConfigFilter.lowpass = 45.0
c.ConfigFilter.noise_type = 50.0

#------------------------------------------------------------------------------
# ConfigDetrend configuration
#------------------------------------------------------------------------------
c.ConfigDetrend.enable = True

#------------------------------------------------------------------------------
# ConfigFreqsDomain configuration
#------------------------------------------------------------------------------
c.ConfigFreqsDomain.channels = ['CH1']
c.ConfigFreqsDomain.freqs_range = [0.0, 125.0]
c.ConfigFreqsDomain.overlap_ratio = 0.5
c.ConfigFreqsDomain.seconds = 5
c.ConfigFreqsDomain.window_type = 'hann'

#------------------------------------------------------------------------------
# ConfigTimeDomain configuration
#------------------------------------------------------------------------------
c.ConfigTimeDomain.amplitude = 870.0
c.ConfigTimeDomain.interval = 50.0
c.ConfigTimeDomain.seconds = 5

#------------------------------------------------------------------------------
# ConfigRecorder configuration
#------------------------------------------------------------------------------
c.ConfigRecorder.record_processed = False
c.ConfigRecorder.record_raw = False

