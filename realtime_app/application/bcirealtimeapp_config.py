# Configuration file for BCIRealtimeApp.

c = get_config()  # noqa

#------------------------------------------------------------------------------
# ConfigTheme configuration
#------------------------------------------------------------------------------
c.ConfigTheme.theme = 'Fusion'

#------------------------------------------------------------------------------
# ConfigDevice configuration
#------------------------------------------------------------------------------
c.ConfigDevice.name = 'synthetic'
c.ConfigDevice.port = ''
c.ConfigDevice.sampling_rate = 250

#------------------------------------------------------------------------------
# ConfigFilter configuration
#------------------------------------------------------------------------------
c.ConfigFilter.highpass = 0.5
c.ConfigFilter.highpass_enable = True
c.ConfigFilter.lowpass = 45.0
c.ConfigFilter.lowpass_enable = True
c.ConfigFilter.notch_enable = True
c.ConfigFilter.notch_freq = 50.0

#------------------------------------------------------------------------------
# ConfigDetrend configuration
#------------------------------------------------------------------------------
c.ConfigDetrend.enable = True

#------------------------------------------------------------------------------
# ConfigFreqsDomain configuration
#------------------------------------------------------------------------------
c.ConfigFreqsDomain.channels = ['CH1']
c.ConfigFreqsDomain.freqs_range = [0.0, 60.0]
c.ConfigFreqsDomain.overlap_ratio = 0.5
c.ConfigFreqsDomain.seconds = 5
c.ConfigFreqsDomain.window_type = 'hann'

#------------------------------------------------------------------------------
# ConfigTimeDomain configuration
#------------------------------------------------------------------------------
c.ConfigTimeDomain.amplitude = 1000.0
c.ConfigTimeDomain.channels = ['CH1', 'CH2', 'CH3', 'CH4', 'CH5']
c.ConfigTimeDomain.interval = 50.0
c.ConfigTimeDomain.seconds = 5

#------------------------------------------------------------------------------
# ConfigRecorder configuration
#------------------------------------------------------------------------------
c.ConfigRecorder.record_processed = False
c.ConfigRecorder.record_raw = False

