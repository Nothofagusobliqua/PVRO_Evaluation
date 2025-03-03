import pvlib
import statistics
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import numpy as np
import etapas
import matplotlib.pyplot as plt
# import PV_systems_clear_sky as PVS
import PV_systems_realista as PVS
import red_elec
import battery_bank
import economics as eco

factor_seguridad = 1.1


class PlantaTratamiento(object):
    """
    planta de tratamiento de agua

    run_pta: calcula el total_year_power consumido por la planta de tratamiento, y apartir de esa lista,
            calcula year_energy, months_energy, days_energy, days. Almacena estas cosas en atributos

    run_pta_grid: calcula la energía demandada a la red y con esto calcula el gasto mensual en electricidad

    run_pta_pvs_grid: calcula la energía demandada a la red restando lo generado por el arreglo fotovoltaico,
            luego, calcula el gasto mensual en energía
    """

    def __init__(self, name, location, altitude, tilt, azimuth, tmy, bomba_elevadora=None, coagulacion=None,
                 floculacion1=None,
                 floculacion2=None, floculacion3=None, reverse_osmosis=None, bomba_almacenamiento=None,
                 clorado=None, consumo=None, redelec=None, fact_cap_inst_1=0, fact_cap_inst_2=0,
                 capacidad_instalada1=0, capacidad_instalada2=0, capacidad_instalada_off_grid=0,
                 year_i=0):
        # datos básicos
        self.name = name
        latitude, longitude = location
        self.tilt = tilt
        self.azimuth = azimuth
        self.tmy = tmy
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.year_i = year_i

        # para definir la capacidad instalada fotovoltaica
        self.fact_cap_inst_1 = fact_cap_inst_1
        self.fact_cap_inst_2 = fact_cap_inst_2

        self.capacidad_instalada1 = capacidad_instalada1
        self.capacidad_instalada2 = capacidad_instalada2
        self.capacidad_instalada_off_grid = capacidad_instalada_off_grid

        # etapass
        self.bomba_elevadora = bomba_elevadora
        self.coagulacion = coagulacion
        self.floculacion1 = floculacion1
        self.floculacion2 = floculacion2
        self.floculacion3 = floculacion3
        self.reverse_osmosis = reverse_osmosis
        self.bomba_almacenamiento = bomba_almacenamiento
        self.clorado = clorado

        # cosas
        self.consumo = consumo
        self.redelec = redelec

        # etapas
        self.etapas = []
        etapitas = [bomba_almacenamiento, reverse_osmosis, floculacion3, floculacion2, floculacion1,
                    coagulacion, clorado, bomba_elevadora]
        for i in range(0, len(etapitas)):
            if etapitas[i] is None:
                pass
            else:
                self.etapas.append(etapitas[i])

        # resultados generales
        self.total_year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days = None

        # resultados run_pta_grid (dtg -> demand to grid)
        self.year_energy_dtg_pta_grid = None  # energía que compré
        self.months_energy_dtg_pta_grid = None  # energía que compré
        self.days_energy_dtg_pta_grid = None  # energía que compré
        self.days_dtg_pta_grid = None  # energía que compré

        self.cost_year_energy_pta_grid = None
        self.cost_months_energy_pta_grid = None

        # resultados pta_pvs_grid
        # AUTOGEN
        self.pta_pvs_grid_pv_system = None

        self.year_energy_dtg_pta_pvs_grid = None
        self.months_energy_dtg_pta_pvs_grid = None
        self.days_energy_dtg_pta_pvs_grid = None
        self.days_dtg_pta_pvs_grid = None

        self.cost_year_energy_pta_pvs_grid = None
        self.cost_months_energy_pta_pvs_grid = None

        # resultados pta_pvs_ntbg
        self.pta_pvs_ntbg_pv_system = None

        self.year_energy_dtg_pta_pvs_ntbg = None
        self.months_energy_dtg_pta_pvs_ntbg = None
        self.days_energy_dtg_pta_pvs_ntbg = None
        self.days_dtg_pta_pvs_ntbg = None

        self.year_energy_exce = None
        self.months_energy_exce = None
        self.days_energy_exce = None
        self.days_exce = None

        self.cost_year_energy_pta_pvs_ntbg = None
        self.cost_months_energy_pta_pvs_ntbg = None
        self.valor_inyecciones_no_usado = 0
        self.lista_excedentes_no_usados = None
        self.months_exe_valorizados = None
        self.months_exe_valorizados_disponibles = None
        self.months_monto_inyecciones = None

        # resultados caso pta_off_grid
        # self.pta_off_grid_pv_system = None
        # self.battery_bank = None
        # self.capacidad_banco = None
        # self.banco_DOD = None
        # self.energy_needed = None

        self.baterry_soc_list = None
        self.bat_inyected_power = None
        self.power_to_bat = None
        self.power_to_pta = None

        # off grid 2
        self.c_bat = None
        self.n_paneles = None

        self.off_grid_pv_system = None
        self.banco = None
        self.cost_year_energy_off_grid = None

    def run_pta(self):
        total_year_power_list = []
        for i in range(0, len(self.etapas)):
            if i == 0:
                consumo = self.consumo.consumo_365
            else:
                consumo = self.etapas[i - 1].consumo_con_perdidas
            self.etapas[i].run(consumo)
            total_year_power_list.append(self.etapas[i].year_power)

        self.total_year_power = etapas.suma_elementos_sublistas(total_year_power_list)
        year_energy, months_energy, days_energy, days = etapas.energy(self.total_year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days = days

    def pv_array_sizer_pta_dependent(self, factor_capacidad_instalada):
        power = max(self.total_year_power) * factor_capacidad_instalada
        Vmpo_panel = PVS.module.Vmpo
        Impo_panel = PVS.module.Impo

        Pmpo_panel = Vmpo_panel * Impo_panel
        Vdco_inverter = PVS.inverter.Vdco

        n_serie = round(Vdco_inverter / Vmpo_panel)
        n_paralelo = round((power * 1000) / (n_serie * Pmpo_panel))
        # print(n_serie)
        # print(n_paralelo)
        return n_serie, n_paralelo

    def pv_array_sizer_fixed_capacity(self, capacidad_instalada):
        power = capacidad_instalada  # kW
        Vmpo_panel = PVS.module.Vmpo
        Impo_panel = PVS.module.Impo

        Pmpo_panel = Vmpo_panel * Impo_panel
        Vdco_inverter = PVS.inverter4.Vdco

        n_serie = round(Vdco_inverter / Vmpo_panel)
        n_paralelo = round((power * 1000) / (n_serie * Pmpo_panel))

        return n_serie, n_paralelo

    def create_pvs(self, surface_tilt, surface_azimuth, factor_capacidad_instalada=0, potencia=0):
        modules_per_string = 1
        strings_per_inverter = 1

        if factor_capacidad_instalada != 0 and potencia == 0:
            modules_per_string, strings_per_inverter = self.pv_array_sizer_pta_dependent(factor_capacidad_instalada)
        elif potencia != 0 and factor_capacidad_instalada == 0:
            modules_per_string, strings_per_inverter = self.pv_array_sizer_fixed_capacity(potencia)

        pv_syst = PVS.SolarSystem(latitude=self.latitude, longitude=self.longitude,
                                  altitude=self.altitude, name=self.name,
                                  surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                                  tmy=self.tmy,
                                  modules_per_string=modules_per_string,
                                  strings_per_inverter=strings_per_inverter,
                                  potencia=potencia, year=self.year_i)
        return pv_syst

    def run_pta_grid(self):

        self.year_energy_dtg_pta_grid = self.year_energy
        self.months_energy_dtg_pta_grid = self.months_energy
        self.days_energy_dtg_pta_grid = self.days_energy
        self.days_dtg_pta_grid = self.days

        potencia_contratada = max(self.total_year_power) * factor_seguridad
        c_y_e, c_m_e, v_i_n_u, klklkl, klklkl1, klklkl2 = self.redelec.elec_ex(
            months_energy=self.months_energy_dtg_pta_grid,
            pote_contratada=potencia_contratada,
            months_exedentes=None)

        self.cost_year_energy_pta_grid = c_y_e
        self.cost_months_energy_pta_grid = c_m_e

    def run_pta_pvs_grid(self):
        surface_tilt = self.tilt
        surface_azimuth = self.azimuth
        self.pta_pvs_grid_pv_system = self.create_pvs(surface_tilt,
                                                      surface_azimuth,
                                                      self.fact_cap_inst_1,
                                                      self.capacidad_instalada1)
        self.pta_pvs_grid_pv_system.run()

        power_demand_to_grid = etapas.calc_demand_grid(self.total_year_power, self.pta_pvs_grid_pv_system.year_power_ac)
        year_energy_dtg, months_energy_dtg, days_energy_dtg, days_dtg = etapas.energy(power_demand_to_grid)
        self.year_energy_dtg_pta_pvs_grid = year_energy_dtg
        self.months_energy_dtg_pta_pvs_grid = months_energy_dtg
        self.days_energy_dtg_pta_pvs_grid = days_energy_dtg
        self.days_dtg_pta_pvs_grid = days_dtg

        potencia_contratada = max(self.total_year_power) * factor_seguridad

        c_y_e, c_m_e, v_i_n_u, klklkl, klklkl1, klklkl2 = self.redelec.elec_ex(
            months_energy=self.months_energy_dtg_pta_pvs_grid,
            pote_contratada=potencia_contratada,
            months_exedentes=None)

        self.cost_year_energy_pta_pvs_grid = c_y_e
        self.cost_months_energy_pta_pvs_grid = c_m_e

    def run_pta_pvs_ntbg(self):
        surface_tilt = self.tilt
        surface_azimuth = self.azimuth
        self.pta_pvs_ntbg_pv_system = self.create_pvs(surface_tilt,
                                                      surface_azimuth,
                                                      self.fact_cap_inst_2,
                                                      self.capacidad_instalada2)
        self.pta_pvs_ntbg_pv_system.run()

        power_demand_to_grid, excedentes = etapas.calc_demand_grid_ntbg(self.total_year_power,
                                                                        self.pta_pvs_ntbg_pv_system.year_power_ac)
        # print(f"energia planta pv: {self.pta_pvs_ntbg_pv_system.year_energy_ac}")
        # print(f"energia consumida pta: {self.year_energy}")
        year_energy_dtg, months_energy_dtg, days_energy_dtg, days_dtg = etapas.energy(power_demand_to_grid)
        year_energy_exce, months_energy_exce, days_energy_exce, days_exce = etapas.energy(excedentes)

        self.year_energy_dtg_pta_pvs_ntbg = year_energy_dtg
        self.months_energy_dtg_pta_pvs_ntbg = months_energy_dtg
        self.days_energy_dtg_pta_pvs_ntbg = days_energy_dtg
        self.days_dtg_pta_pvs_ntbg = days_dtg

        self.year_energy_exce = year_energy_exce
        self.months_energy_exce = months_energy_exce
        self.days_energy_exce = days_energy_exce
        self.days_exce = days_exce

        potencia_contratada = max(self.total_year_power) * factor_seguridad

        c_y_e, c_m_e, v_i_n_u, v_i_m, v_i_m_d, m_m_i = self.redelec.elec_ex(
            months_energy=self.months_energy_dtg_pta_pvs_ntbg,
            pote_contratada=potencia_contratada,
            months_exedentes=months_energy_exce,
            valor_inyec_not_used=self.valor_inyecciones_no_usado)

        self.cost_year_energy_pta_pvs_ntbg = c_y_e
        self.cost_months_energy_pta_pvs_ntbg = c_m_e
        self.valor_inyecciones_no_usado = v_i_n_u
        self.months_exe_valorizados = v_i_m
        self.months_exe_valorizados_disponibles = v_i_m_d
        self.months_monto_inyecciones = m_m_i

    # run_pta_off_grid NOOOOOOo
    def run_pta_off_grid(self, dias_autonomia, factor, deep_of_discharge=0.5):
        surface_tilt = self.tilt
        surface_azimuth = self.azimuth

        # 1.- dimencionar banco de baterias
        max_energy = max(self.days_energy)  # kWh
        # print("max_energy: ", max_energy)
        deep_of_discharge = deep_of_discharge
        self.banco_DOD = deep_of_discharge

        energy_need = max_energy * dias_autonomia * (1 / deep_of_discharge)  # kWh
        self.energy_needed = energy_need
        # print("energy_need: ", energy_need)

        charge_nedded = (energy_need / 360)  # kAh
        self.capacidad_banco = charge_nedded
        # print("charge_needed: ", charge_nedded)

        self.battery_bank = battery_bank.BatteryBank(capacidad=charge_nedded)

        # print("capacidad banco kAh: ", charge_nedded)
        # print("max_charge_current kA: ", banco.max_charge_current)

        # 2.- dimencionar pv array
        p_charge_bat = (self.battery_bank.max_charge_current * self.battery_bank.voltaje)  # kW
        p_max = (max(self.total_year_power) + p_charge_bat) * factor  # kW
        # p_max = (max(self.total_year_power)) * factor  # kW
        # p_max = factor  # kW
        # print("p_charge_bat: ", p_charge_bat)
        # print("max(self.total_year_power): ", max(self.total_year_power))
        # print("p_max para pv: ", p_max)

        self.pta_off_grid_pv_system = self.create_pvs(surface_tilt=surface_tilt, surface_azimuth=surface_azimuth,
                                                      potencia=p_max)
        self.pta_off_grid_pv_system.run()

        # 3.- calculos
        pta_power = self.total_year_power
        pv_power = self.pta_off_grid_pv_system.year_power_ac

        self.battery_bank.run_battery(pta_power=pta_power, pv_power=pv_power)

        self.baterry_soc_list = self.battery_bank.list_soc
        self.bat_inyected_power = self.battery_bank.power_desc
        self.power_to_bat = self.battery_bank.power_to_bat
        self.power_to_pta = self.battery_bank.power_to_pta

    def desing_off_grid_system(self):
        dias_autonomia = 2
        factor_crecimiento = 1.2
        max_day_energy = max(self.days_energy) * factor_crecimiento
        horas = self.consumo.hora_f - self.consumo.hora_i
        power_bat = max_day_energy / horas

        dod = 0.5
        effi_bat = 0.95
        effi_inv = 0.85
        volt_bat = 24
        c_kWh = (max_day_energy * dias_autonomia) / (effi_bat * effi_inv * dod)  # kWh
        # print("CAPACIDADDDD", c_kWh)
        E = max(self.days_energy)
        effi_inv = 0.95
        effi_bat = 0.85
        effi_r = 0.215
        Apv = 2.144

        beta = -0.38 / 100

        tem_tmy = self.tmy.temp_air
        p, pp, prom_invierno_temp, ppp = etapas.promedios_estaciones(tem_tmy)
        Tamb = etapas.promedio_lista(prom_invierno_temp)
        # print("Tamb: ", Tamb)

        wind_tmy = self.tmy.wind_speed
        p, pp, prom_invierno_wind, ppp = etapas.promedios_estaciones(wind_tmy)
        Vw = etapas.promedio_lista(prom_invierno_wind)
        # print("Vw: ", Vw)

        test_pv_syst = self.create_pvs(surface_tilt=self.tilt, surface_azimuth=self.azimuth,
                                       potencia=1)
        test_pv_syst.run()
        datos_ = test_pv_syst.modelchain.results.effective_irradiance
        j, jj, prom_invierno_G, jjj = etapas.promedios_estaciones(datos_)
        G = etapas.promedio_lista(prom_invierno_G)
        # print("G: ", G)

        Tnoct = 45
        Tcell = Tamb + (9.5 / (5.7 + 3.8 * Vw)) * ((G * (Tnoct - 20)) / 800)
        Tc = 1 - beta * (Tcell - 25)

        I = sum(prom_invierno_G) / 1000
        # print("I: ", I)

        numero_panles = E / (effi_inv * effi_bat * effi_r * Tc * Apv * I)

        potencia = numero_panles * 0.4

        self.banco = etapas.Banco(capacidad=c_kWh, potencia=power_bat, voltaje=volt_bat)

        self.off_grid_pv_system = self.create_pvs(surface_tilt=self.tilt, surface_azimuth=self.azimuth,
                                                  potencia=potencia)

        self.off_grid_pv_system.run()

    def run_pta_off_grid_2(self):
        capa_bat = self.banco.capacidad
        coma = eco.coma_pv(self.off_grid_pv_system) + eco.coma_bat_2(self.banco)
        self.cost_year_energy_off_grid = coma

    def plot_elec_ex(self, caso):
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo",
                 "Junio", "Julio", "Agosto", "Septiembre",
                 "Octubre", "Noviembre", "Diciembre"]
        meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
                       "JUN", "JUL", "AGO", "SEP",
                       "OCT", "NOV", "DIC"]
        costo_mes = []
        if caso == "pta_grid":
            costo_mes = self.cost_months_energy_pta_grid

        elif caso == "pta_pvs_grid":
            costo_mes = self.cost_months_energy_pta_pvs_grid

        # Gráfico de barras
        fig, ax = plt.subplots()
        ax.bar(x=meses_short, height=costo_mes)
        plt.xlabel('Meses')
        plt.ylabel("Millones de Pesos")
        plt.title('Gasto en electricidad por mes')
        plt.show()

    def plot_comp_elec_ex(self):
        meses = ["Enero", "Febrero", "Marzo",
                 "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre",
                 "Octubre", "Noviembre", "Diciembre"]

        meses_short = ["ENE", "FEB", "MAR", "ABR", "MAY",
                       "JUN", "JUL", "AGO", "SEP",
                       "OCT", "NOV", "DIC"]

        base = []
        autogen = []
        ntbg = []
        for i in range(0, 12):
            base.append(self.cost_months_energy_pta_grid[i] / 1000000)
            autogen.append(self.cost_months_energy_pta_pvs_grid[i] / 1000000)
            ntbg.append(self.cost_months_energy_pta_pvs_ntbg[i] / 1000000)

        plt.figure()
        plt.grid(True)
        plt.plot(meses_short, base, label="Red Eléctrica")
        plt.plot(meses_short, autogen, label="Autogeneración")
        plt.plot(meses_short, ntbg, label="Netbilling")
        plt.xlabel('Meses')
        plt.ylabel("Millones de pesos")
        plt.title('Comparación gasto mensual en energía')
        plt.legend()
        plt.show()

    def plot_pv_gen_dia_x(self, dia, pv_system):
        hora_i = (dia - 1) * 24
        hora_f = hora_i + 24
        t = range(0, 24)
        plt.figure()
        plt.grid(True)
        plt.plot(t, pv_system.year_power_ac[hora_i:hora_f])
        plt.xlabel('Horas')
        plt.ylabel("Potencia [kW]")
        plt.title('Potencia generada por arreglo PV')
        plt.legend()
        plt.show()

    def plot_month_pv_gen(self, pv_system):
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo",
                 "Junio", "Julio", "Agosto", "Septiembre",
                 "Octubre", "Noviembre", "Diciembre"]
        fig, ax = plt.subplots()
        ax.bar(x=meses, height=pv_system.months_energy_ac)
        plt.xlabel('Meses')
        plt.ylabel("Energía [kWh]")
        plt.title('Energía mensual generada por el arreglo fotovoltaico')
        plt.show()

    def plot_dia_x(self, dia):
        hora_i = (dia - 1) * 24
        hora_f = hora_i + 24
        t = range(0, 24)
        plt.figure(figsize=(16, 9))
        plt.grid(True)
        plt.plot(t, self.bomba_elevadora.year_power[hora_i:hora_f], label="Bomba elevadora")
        plt.plot(t, self.bomba_almacenamiento.year_power[hora_i:hora_f], label="Bomba almacenamiento")
        plt.plot(t, self.coagulacion.year_power[hora_i:hora_f], label="Coagulación")
        plt.plot(t, self.floculacion1.year_power[hora_i:hora_f], label="Floculación 1")
        plt.plot(t, self.floculacion2.year_power[hora_i:hora_f], label="Floculación 2")
        # plt.plot(t, self.reverse_osmosis.year_power[hora_i:hora_f], label="Osmosis Inversa")
        plt.plot(t, self.clorado.year_power[hora_i:hora_f], label="Cloración")
        # plt.plot(t, self.total_year_power[hora_i:hora_f], label="Total")
        plt.xlabel('Horas del día')
        plt.ylabel("Potencia consumida [kW]")
        plt.title(f"Resultados día {dia}")
        plt.legend()
        plt.show()

    def avanza_periodo(self):
        self.year_i += 1
