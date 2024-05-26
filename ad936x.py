# Analog Devices AD936x transceiver

import iio
import numpy as np

import compat as cl
if cl._is_libiio_v1():
    from compat import compat_libiio_v1_rx as crx
    from compat import compat_libiio_v1_tx as ctx
else:
    from compat import compat_libiio_v0_rx as crx
    from compat import compat_libiio_v0_tx as ctx

from abc import ABCMeta, abstractmethod
from attribute import attribute


class ad936x(crx, ctx, attribute, metaclass=ABCMeta):
    """AD936x transceiver"""

    _rx_channel_names = ["voltage0", "voltage1"]
    _tx_channel_names = ["voltage0", "voltage1"]
    _control_device_name = "ad9361-phy"
    _rx_data_device_name = "cf-ad9361-lpc"
    _tx_data_device_name = "cf-ad9361-dds-core-lpc"
    _device_name = ""

    @abstractmethod
    def _rx_init_channels(self):
        """Init RX channels"""
        raise NotImplementedError
    
    @abstractmethod
    def _tx_init_channels(self):
        """Init TX channels"""
        raise NotImplementedError

    @abstractmethod
    def _rx_buffered_data(self):
        """Read data from RX buffer"""
        raise NotImplementedError
    
    @abstractmethod
    def _tx_buffer_push(self, data):
        """Push data to TX buffer
        
        data: bytearray
        """
        raise NotImplementedError

    @property
    def rx_buffer_size(self):
        """rx_buffer_size: Size of receive buffer in samples"""
        return self._rx_buffer_size

    @rx_buffer_size.setter
    def rx_buffer_size(self, value):
        self._rx_buffer_size = value

    @property
    def gain_control_mode(self):
        """gain_control_mode: Mode of receive path AGC. Options are:
        slow_attack, fast_attack, manual"""
        return self._get_iio_attr_str("voltage0", "gain_control_mode", False)

    @gain_control_mode.setter
    def gain_control_mode(self, value):
        self._set_iio_attr("voltage0", "gain_control_mode", False, value)

    @property
    def rx_hardwaregain(self):
        """rx_hardwaregain: Gain applied to RX path. Only applicable when
        gain_control_mode is set to 'manual'"""
        return self._get_iio_attr("voltage0", "hardwaregain", False)

    @rx_hardwaregain.setter
    def rx_hardwaregain(self, value):
        if self.gain_control_mode == "manual":
            self._set_iio_attr_float("voltage0", "hardwaregain", False, value)

    @property
    def tx_hardwaregain(self):
        """tx_hardwaregain: Attenuation applied to TX path"""
        return self._get_iio_attr("voltage0", "hardwaregain", True)

    @tx_hardwaregain.setter
    def tx_hardwaregain(self, value):
        self._set_iio_attr_float("voltage0", "hardwaregain", True, value)
    
    @property
    def rx_rf_bandwidth(self):
        """rx_rf_bandwidth: Bandwidth of front-end analog filter of RX path"""
        return self._get_iio_attr("voltage0", "rf_bandwidth", False)

    @rx_rf_bandwidth.setter
    def rx_rf_bandwidth(self, value):
        self._set_iio_attr_int("voltage0", "rf_bandwidth", False, value)

    @property
    def tx_rf_bandwidth(self):
        """tx_rf_bandwidth: Bandwidth of front-end analog filter of TX path"""
        return self._get_iio_attr("voltage0", "rf_bandwidth", True)

    @tx_rf_bandwidth.setter
    def tx_rf_bandwidth(self, value):
        self._set_iio_attr_int("voltage0", "rf_bandwidth", True, value)
    
    @property
    def sample_rate(self):
        """sample_rate: Sample rate RX and TX paths in samples per second"""
        return self._get_iio_attr("voltage0", "sampling_frequency", False)

    @sample_rate.setter
    def sample_rate(self, rate):
        if rate < 521e3:
            raise ValueError(
                "Error: Does not currently support sample rates below 521e3"
            )

        # The following was converted from ad9361_set_bb_rate() in libad9361-iio
        # fmt: off
        if (rate <= 20000000):
            dec = 4
            fir = [
                -15, -27, -23, -6, 17, 33, 31, 9, -23, -47, -45, -13, 34, 69,
                67, 21, -49, -102, -99, -32, 69, 146, 143, 48, -96, -204, -200,
                -69, 129, 278, 275, 97, -170, -372, -371, -135, 222, 494, 497,
                187, -288, -654, -665, -258, 376, 875, 902, 363, -500, -1201,
                -1265, -530, 699, 1748, 1906, 845, -1089, -2922, -3424, -1697,
                2326, 7714, 12821, 15921, 15921, 12821, 7714, 2326, -1697,
                -3424, -2922, -1089, 845, 1906, 1748, 699, -530, -1265, -1201,
                -500, 363, 902, 875, 376, -258, -665, -654, -288, 187, 497,
                494, 222, -135, -371, -372, -170, 97, 275, 278, 129, -69, -200,
                -204, -96, 48, 143, 146, 69, -32, -99, -102, -49, 21, 67, 69,
                34, -13, -45, -47, -23, 9, 31, 33, 17, -6, -23, -27, -15
            ]
            taps = 128
        elif (rate <= 40000000):
            dec = 2
            fir = [
                -0, 0, 1, -0, -2, 0, 3, -0, -5, 0, 8, -0, -11, 0, 17, -0, -24,
                0, 33, -0, -45, 0, 61, -0, -80, 0, 104, -0, -134, 0, 169, -0,
                -213, 0, 264, -0, -327, 0, 401, -0, -489, 0, 595, -0, -724, 0,
                880, -0, -1075, 0, 1323, -0, -1652, 0, 2114, -0, -2819, 0,
                4056, -0, -6883, 0, 20837, 32767, 20837, 0, -6883, -0, 4056, 0,
                -2819, -0, 2114, 0, -1652, -0, 1323, 0, -1075, -0, 880, 0,
                -724, -0, 595, 0, -489, -0, 401, 0, -327, -0, 264, 0, -213, -0,
                169, 0, -134, -0, 104, 0, -80, -0, 61, 0, -45, -0, 33, 0, -24,
                -0, 17, 0, -11, -0, 8, 0, -5, -0, 3, 0, -2, -0, 1, 0, -0, 0
            ]
            taps = 128
        elif (rate <= 53333333):
            dec = 2
            fir = [
                -4, 0, 8, -0, -14, 0, 23, -0, -36, 0, 52, -0, -75, 0, 104, -0,
                -140, 0, 186, -0, -243, 0, 314, -0, -400, 0, 505, -0, -634, 0,
                793, -0, -993, 0, 1247, -0, -1585, 0, 2056, -0, -2773, 0, 4022,
                -0, -6862, 0, 20830, 32767, 20830, 0, -6862, -0, 4022, 0,
                -2773, -0, 2056, 0, -1585, -0, 1247, 0, -993, -0, 793, 0, -634,
                -0, 505, 0, -400, -0, 314, 0, -243, -0, 186, 0, -140, -0, 104,
                0, -75, -0, 52, 0, -36, -0, 23, 0, -14, -0, 8, 0, -4, 0
            ]
            taps = 96
        else:
            dec = 2
            fir = [
                -58, 0, 83, -0, -127, 0, 185, -0, -262, 0, 361, -0, -488, 0,
                648, -0, -853, 0, 1117, -0, -1466, 0, 1954, -0, -2689, 0, 3960,
                -0, -6825, 0, 20818, 32767, 20818, 0, -6825, -0, 3960, 0,
                -2689, -0, 1954, 0, -1466, -0, 1117, 0, -853, -0, 648, 0, -488,
                -0, 361, 0, -262, -0, 185, 0, -127, -0, 83, 0, -58, 0
            ]
            taps = 64
        # fmt: on
        current_rate = self._get_iio_attr("voltage0", "sampling_frequency", False)

        if self._get_iio_attr("out", "voltage_filter_fir_en", False):
            if current_rate <= (25000000 // 12):
                self._set_iio_attr("voltage0", "sampling_frequency", False, 3000000)
            self._set_iio_attr("out", "voltage_filter_fir_en", False, 0)

        # Assemble FIR filter config string
        fir_config_string = ""
        fir_config_string += "RX 3 GAIN -6 DEC " + str(dec) + "\n"
        fir_config_string += "TX 3 GAIN 0 INT " + str(dec) + "\n"
        for i in range(taps):
            fir_config_string += str(fir[i]) + "," + str(fir[i]) + "\n"
        fir_config_string += "\n"
        self._set_iio_dev_attr_str("filter_fir_config", fir_config_string)

        if rate <= (25000000 // 12):
            readbuf = self._get_iio_dev_attr_str("tx_path_rates")
            dacrate = int(readbuf.split(" ")[1].split(":")[1])
            txrate = int(readbuf.split(" ")[5].split(":")[1])
            max_rate = (dacrate // txrate) * 16
            if max_rate < taps:
                self._set_iio_attr("voltage0", "sampling_frequency", False, 3000000)
            self._set_iio_attr("out", "voltage_filter_fir_en", False, 1)
            self._set_iio_attr("voltage0", "sampling_frequency", False, rate)
        else:
            self._set_iio_attr("voltage0", "sampling_frequency", False, rate)
            self._set_iio_attr("out", "voltage_filter_fir_en", False, 1)
    
    @property
    def rx_lo(self):
        """rx_lo: Carrier frequency of RX path"""
        return self._get_iio_attr("altvoltage0", "frequency", True)

    @rx_lo.setter
    def rx_lo(self, value):
        self._set_iio_attr_int("altvoltage0", "frequency", True, value)

    @property
    def tx_lo(self):
        """tx_lo: Carrier frequency of TX path"""
        return self._get_iio_attr("altvoltage1", "frequency", True)

    @tx_lo.setter
    def tx_lo(self, value):
        self._set_iio_attr_int("altvoltage1", "frequency", True, value)

    def __init__(self, uri=""):
        if self._ctx:
            return
        
        self.uri = uri

        try:
            if self.uri == "":
                if not self._ctx and self._uri_auto != "":
                    self._ctx = iio.Context(self._uri_auto)
                if not self._ctx:
                    raise Exception("No device found")
            else:
                self._ctx = iio.Context(self.uri)
        except BaseException:
            raise Exception("No device found")
        
        self._rxadc = self._ctx.find_device(self._rx_data_device_name)
        if not self._rxadc:
            raise Exception(f"No device found with name {self._rx_data_device_name}")
        
        self._rx_init_channels()
        self._tx_init_channels()

        self.rx_buffer_size = 1024

        self.rx_data = []
        self.tx_data = []

    def tx_only(self):
        """Transmit data"""
        pass

    def rx_only(self, get=False):
        """Recive data"""

        if get:
            return self.rx_data
        
        data = self._rx_buffered_data()

        if len(data) % 2 != 0:
            raise Exception(
                "Complex data must have an even number of component channels"
            )
        
        self.rx_data = [data[i] + 1j * data[i + 1] for i in range(0, len(data), 2)]

        # Don't return list if a single channel
        if len(self.rx_data == 2):
            self.rx_data = self.rx_data[0]
        
        return self.rx_data

    def tx_rx_sync(self):
        """Sync start transmit and recive"""
        pass
