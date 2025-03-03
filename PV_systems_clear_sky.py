import pvlib

from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import etapas

# base de datos de modulos (paneles)
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
# sandia_modules = pvlib.pvsystem.retrieve_sam('cecmod')

# base de datos de inversores
cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')

# modulos
# module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
module = sandia_modules['SunPower_128_Cell_Module__2009__E__']  # 400 W

# inversores
inverter = cec_inverters['ABB__TRIO_60_0_TL_OUTD_US_480__480V_']  # 60 kW

inverter1 = cec_inverters['ABB__PVI_3_0_OUTD_S_US__208V_']  # 3 kW
inverter2 = cec_inverters['ABB__PVI_5000_OUTD_S_US_Z__240V_']  # 5 kW
inverter3 = cec_inverters['Yaskawa_Solectria_Solar__PVI_50_kW_480__480V_']  # 50 kW
inverter4 = cec_inverters['ABB__PVI_CENTRAL_300_US__480V_']  # 300 kW

temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']


def pd_to_list_float(pd_array):
    lista = []
    for i in range(0, 8760):
        n = pd_array.iloc[i]
        flt = float(n) / 1000
        lista.append(flt)
    return lista


class SolarSystem(object):
    """

    """

    def __init__(self,  latitude, longitude, altitude, name,
                 surface_tilt, surface_azimuth,
                 modules_per_string=1, strings_per_inverter=1,
                 tz="America/Santiago",
                 module_parameters=module, inverter_parameters=inverter4,
                 temperature_model_parameters=temperature_parameters, potencia=0):
        self.potencia = potencia
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.name = name
        self.tz = tz
        self.location = Location(latitude=self.latitude, longitude=self.longitude,
                                 tz=self.tz, altitude=self.altitude, name=self.name)
        self.surface_tilt = surface_tilt
        self.surface_azimuth = surface_azimuth
        self.module_parameters = module_parameters
        self.inverter_parameters = inverter_parameters
        self.temperature_model_parameters = temperature_model_parameters
        self.temperature_parameters = temperature_parameters
        self.modules_per_string = modules_per_string
        self.strings_per_inverter = strings_per_inverter

        self.system = PVSystem(surface_tilt=self.surface_tilt,
                               surface_azimuth=self.surface_azimuth,
                               module_parameters=self.module_parameters,
                               inverter_parameters=self.inverter_parameters,
                               temperature_model_parameters=self.temperature_parameters,
                               modules_per_string=self.modules_per_string,
                               strings_per_inverter=self.strings_per_inverter)

        self.modelchain = ModelChain(self.system, self.location)

        self.year_power_dc = None
        self.year_energy_dc = None
        self.months_energy_dc = None
        self.days_energy_dc = None
        self.days_power_dc = None

        self.year_power_ac = None
        self.year_energy_ac = None
        self.months_energy_ac = None
        self.days_energy_ac = None
        self.days_power_ac = None

    def run(self):
        timeses = pd.date_range(start='2021-01-01 00:00', end='2021-12-31 23:00', freq='1h', tz=self.location.tz)
        clear_sky = self.location.get_clearsky(timeses)
        self.modelchain.run_model(clear_sky)


        power = pd_to_list_float(self.modelchain.results.ac)

        power_corregido = []
        for i in range(0, 8760):
            if power[i] < 0:
                power_corregido.append(0)
            else:
                power_corregido.append(power[i] * 0.78)
        self.year_power_ac = power_corregido
        year_energy_ac, months_energy_ac, days_energy_ac, days_ac = etapas.energy(self.year_power_ac)
        self.year_energy_ac = year_energy_ac
        self.months_energy_ac = months_energy_ac
        self.days_energy_ac = days_energy_ac
        self.days_power_ac = days_ac
