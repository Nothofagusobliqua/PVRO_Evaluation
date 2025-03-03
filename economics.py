import etapas
import pandas as pd
import planta as pta
import matplotlib.pyplot as plt
import PV_systems_realista as PVS

Vmpo_panel = PVS.module.Vmpo
Impo_panel = PVS.module.Impo

Pmpo_panel = Vmpo_panel * Impo_panel

dolar_a_clp = 850

# datos NREl PV 2020
'''modulo_pw = 0.41 * dolar_a_clp
inverter_pw = 0.12 * dolar_a_clp
electrical_bos = 0.11 * dolar_a_clp
structural_boss = 0.13 * dolar_a_clp
ile = 0.15 * dolar_a_clp'''

# datos NREl PV 2022
modulo_pw = 0.4 * dolar_a_clp
inverter_pw = 0.05 * dolar_a_clp
electrical_bos = 0.27 * dolar_a_clp
structural_boss = 0.13 * dolar_a_clp
ile = 0.15 * dolar_a_clp
suma_pv_install_ENREL = (modulo_pw + inverter_pw + electrical_bos + structural_boss + ile)  # $/W
coma_pv_s_w = 18 * dolar_a_clp  # $/W año

# datos NREl bat
bat_pck = 2955.44 / 12500
bat_bos = 1811.76 / 12500
bat_engeniering_fee = 95.52 / 12500
bat_labour = 1963.25 / 12500
bat_inverter = 2233.29 / 12500
bat_suply_chain = 350.02 / 12500
bat_overhead_profit = 3519.08 / 12500

inv_bateria = (bat_pck + bat_bos + bat_engeniering_fee + bat_labour + bat_inverter + bat_suply_chain
               + bat_overhead_profit) * dolar_a_clp

# datos cotización
precio_watt_pv = 411
precio_watt_inv_on_grid = 257.688
precio_watt_inv_off_grid = 257.688
precio_watt_mppt = 36.2767
precio_panel_400 = 232050
precio_bat_Wh = (145 + 122.9 + 159) / 3
precio_bat_litio_Wh = (383 + 315 + 337) / 3
precio_cargador_Ah = 36.2767

# evolucion futura
inversion_pv_eva_futu = 0.85 * dolar_a_clp  # $/W
inversion_bate_eva_futu = (1050 / 1000) * dolar_a_clp  # $/W

# para ntbg
uf_a_clp = 36500
medidor_bidireccional = 852457
# estudios tecnicos
solicitud_info = 0.691 * uf_a_clp
solicitud_conexion_sin_formulario1 = 0.949 * uf_a_clp
solicitud_conexion_sin_formulario2 = 1.589 * uf_a_clp

# trabajos de empalme trifasico
cambio_medidor = 1.111 * uf_a_clp
reprogramacion_medidor = 2.9 * uf_a_clp

# puesta en servicio
supervicion_puesta_servicio = 3.308 * uf_a_clp

tramites_ntbg = solicitud_info + solicitud_conexion_sin_formulario1 + cambio_medidor + \
                reprogramacion_medidor + supervicion_puesta_servicio

# promedios
inversion_solar = (inversion_pv_eva_futu + suma_pv_install_ENREL) / 2
inversion_banco_baterias = inv_bateria

# operacion y mantencion
coma_baterias = 0.025  # año
coma_solar = 17.21 * dolar_a_clp  # año (ENREL)

# https://atb.nrel.gov/electricity/2022/index

# datos finales

inv_solar_wdc_enrel_2021 = 1.56 * dolar_a_clp
coma_solar_kwdc_year_enrel_2021 = 19 * dolar_a_clp

inv_bat = 1463.6 * dolar_a_clp  # $/kWh

inv_bat_energy = 212 * dolar_a_clp  # $/kWh
inv_bat_power = 296 * dolar_a_clp  # $/kW

cooma_bat = 0.025 * inv_bat_power
porcentaje_coma_bat = 0.025


def V_A_N_ponderado(flujos_caja, inversion, tasa, factor_capex=0.5, factor_opex=0.5):
    valor = 0
    for i in range(0, len(flujos_caja)):
        i_esimo = (flujos_caja[i]) / ((1 + tasa) ** i)
        valor += i_esimo
    vancito = (valor * factor_opex) + (inversion * factor_capex)
    return vancito / 1000000


def valor_actual(flujos, tasa):
    valor = 0
    for i in range(0, len(flujos)):
        i_esimo = (flujos[i]) / ((1 + tasa) ** i)
        valor += i_esimo
    vancito = valor
    return vancito


def inversion_pv(pv_system):
    n_panles = pv_system.modules_per_string * pv_system.strings_per_inverter
    potencia = n_panles * Pmpo_panel  # W
    inv = potencia * inv_solar_wdc_enrel_2021
    # mppt = potencia * precio_watt_mppt
    # inv_total = inv + mppt
    return inv


def inversion_pv_2(n_panles):
    potencia = n_panles * Pmpo_panel  # W
    inv = potencia * inv_solar_wdc_enrel_2021
    # mppt = potencia * precio_watt_mppt
    # inv_total = inv + mppt
    return inv


def inversion_baterias(banco):
    capacidad = banco.capacidad * 1000  # Ah
    voltaje = banco.voltaje
    energia = capacidad * voltaje
    inv_baterias = energia * inversion_banco_baterias
    return inv_baterias


def inversion_baterias_2(capacidad, potencia):
    cost_E = inv_bat_energy * capacidad
    cost_P = inv_bat_power * potencia

    return cost_P + cost_E



def coma_pv_list(pv_syst, n_years):
    n_panles = pv_syst.modules_per_string * pv_syst.strings_per_inverter
    potencia = n_panles * Pmpo_panel
    a = coma_solar_kwdc_year_enrel_2021 * (potencia / 1000)
    coma = []
    for i in range(0, n_years):
        coma.append(a)
    return coma


def coma_pv(pv_syst):
    n_panles = pv_syst.modules_per_string * pv_syst.strings_per_inverter
    potencia = n_panles * Pmpo_panel
    a = coma_solar_kwdc_year_enrel_2021 * (potencia / 1000)
    return a


def coma_bat_list(banco, n_years):
    capacidad = banco.capacidad * 1000  # Ah
    voltaje = banco.voltaje
    energia = capacidad * voltaje
    a = coma_baterias * energia
    coma = []
    for i in range(0, n_years):
        coma.append(a)
    return coma


def coma_bat_list_2(banco, n_years):
    p = banco.potencia
    a = p * cooma_bat
    coma = []
    for i in range(0, n_years):
        coma.append(a)
    return coma


def coma_bat(banco):
    capacidad = banco.capacidad * 1000  # Ah
    voltaje = banco.voltaje
    energia = capacidad * voltaje
    a = coma_baterias * energia
    return a


def coma_bat_2(banco):
    p = banco.potencia
    a = p * cooma_bat
    return a


# planta_de_tratamiento, n_years, tasa, porc_aumento_demanda=0.04, porc_aumento_tarifa=0.03,
# porc_perdinda_efi_pv=0.005

class Econo(object):
    """

    """

    def __init__(self, planta_de_tratamiento, n_years, tasa, porc_aumento_demanda=0.04, porc_aumento_tarifa=0, factor=1):
        self.pta = planta_de_tratamiento
        self.n_years = n_years
        self.tasa = tasa
        self.proyeccion_consumos = self.pta.consumo.proyeccion_lineal_consumos(self.n_years, porc_aumento_demanda)
        self.hora_i = 8
        self.hora_f = 18
        self.porc_aumento_tarifa = porc_aumento_tarifa
        self.factor_analisis_inversion = factor

        self.inv_autogen = None
        self.inv_ntbg = None
        self.inv_banco = None
        self.inv_offgrid = None

        self.van_base = None
        self.van_autogen = None
        self.van_ntbg = None
        self.van_offgrid = None

        self.van_ahorros_base = None
        self.van_ahorros_autogen = None
        self.van_ahorros_ntbg = None
        self.van_ahorros_offgrid = None

        # lista del gasto anual
        self.list_year_ex_base = None
        self.list_year_ex_auto_gen = None
        self.list_year_ex_ntbg = None
        self.list_year_ex_off_grid = None

        # lista de listas de los 12 meses de cada año
        self.list_months_ex_base = None
        self.list_months_ex_auto_gen = None
        self.list_months_ex_ntbg = None
        self.lista_val_exe_not_used = None

        self.list_months_ener_base = None
        self.list_months_ener_autogen = None
        self.list_months_ener_ntbg = None

    def run_all_years(self):
        list_year_ex_base = []
        list_year_ex_auto_gen = []
        list_year_ex_ntbg = []
        list_year_ex_off_grid = []

        list_months_ex_base = []
        list_months_ex_auto_gen = []
        list_months_ex_ntbg = []

        list_months_ener_base = []
        list_months_ener_autogen = []
        list_months_ener_ntbg = []

        hora_i = self.pta.consumo.hora_i
        hora_f = self.pta.consumo.hora_f
        lista_val_exe_not_used = []
        memoria_val_ex_not_uses = 0

        self.pta.run_pta()
        self.pta.desing_off_grid_system()

        for i in range(0, self.n_years):
            consumo_i = etapas.Consumo(consumo_diario=self.proyeccion_consumos[i],
                                       hora_i=hora_i, hora_f=hora_f)
            self.pta.consumo = consumo_i
            # print(self.proyeccion_consumos[i])
            self.pta.redelec.aumento_tarifa(self.porc_aumento_tarifa)
            self.pta.valor_inyecciones_no_usado = memoria_val_ex_not_uses
            self.pta.run_pta()
            # +0print(pta.cost_year_energy_pta_grid)
            self.pta.run_pta_grid()
            self.pta.run_pta_pvs_grid()
            self.pta.run_pta_pvs_ntbg()
            self.pta.run_pta_off_grid_2()

            self.pta.avanza_periodo()

            a = self.pta.valor_inyecciones_no_usado
            memoria_val_ex_not_uses = a
            lista_val_exe_not_used.append(a)

            list_year_ex_base.append(self.pta.cost_year_energy_pta_grid)
            list_year_ex_auto_gen.append(self.pta.cost_year_energy_pta_pvs_grid)
            list_year_ex_ntbg.append(self.pta.cost_year_energy_pta_pvs_ntbg)
            list_year_ex_off_grid.append(self.pta.cost_year_energy_off_grid)

            list_months_ex_base.append(self.pta.cost_months_energy_pta_grid)
            list_months_ex_auto_gen.append(self.pta.cost_months_energy_pta_pvs_grid)
            list_months_ex_ntbg.append(self.pta.cost_months_energy_pta_pvs_ntbg)

            list_months_ener_base.append(self.pta.months_energy_dtg_pta_grid)
            list_months_ener_autogen.append(self.pta.months_energy_dtg_pta_pvs_grid)
            list_months_ener_ntbg.append(self.pta.months_energy_dtg_pta_pvs_ntbg)

        self.list_months_ener_base = list_months_ener_base
        self.list_months_ener_autogen = list_months_ener_autogen
        self.list_months_ener_ntbg = list_months_ener_ntbg

        self.lista_val_exe_not_used = lista_val_exe_not_used

        self.list_year_ex_base = list_year_ex_base
        self.list_year_ex_auto_gen = list_year_ex_auto_gen
        self.list_year_ex_ntbg = list_year_ex_ntbg
        self.list_year_ex_off_grid = list_year_ex_off_grid

        self.list_months_ex_base = list_months_ex_base
        self.list_months_ex_auto_gen = list_months_ex_auto_gen
        self.list_months_ex_ntbg = list_months_ex_ntbg
        # print(list_year_ex_base)
        self.pta.redelec.reset_tarifa()

    def calc_van_base_neg(self):
        I0 = 0
        f1 = self.list_year_ex_base
        for i in range(0, len(self.list_year_ex_base)):
            f1.append(self.list_year_ex_base[i] * (-1))
        van_base = V_A_N_ponderado(f1, I0, self.tasa)
        self.van_base = van_base
        self.van_ahorros_base = 0

    def calc_van_base(self, factor_capex, factor_opex):
        I0 = 0
        f1 = self.list_year_ex_base
        van_base = V_A_N_ponderado(f1, I0, self.tasa, factor_capex=factor_capex, factor_opex=factor_opex)
        self.van_base = van_base
        self.van_ahorros_base = 0

    def calc_van_base_separado(self):
        I0 = 0
        f1 = self.list_year_ex_base
        valor_act = valor_actual(f1, self.tasa)
        return round(I0), round(valor_act)

    def calc_van_autogen(self, factor_capex, factor_opex):
        pv_syst = self.pta.pta_pvs_grid_pv_system
        I0 = inversion_pv(pv_syst) * self.factor_analisis_inversion
        self.inv_autogen = I0
        coma = coma_pv_list(pv_syst, self.n_years)
        elec_ex = self.list_year_ex_auto_gen
        gasto_base = self.list_year_ex_base

        # flujo = []
        # for i in range(0, len(gasto_base)):
        # f = gasto_base[i] - (elec_ex[i] + coma[i])
        # flujo.append(f)

        f2 = []
        for i in range(0, len(elec_ex)):
            f = elec_ex[i] + coma[i]
            f2.append(f)

        self.van_autogen = V_A_N_ponderado(f2, I0, self.tasa, factor_capex=factor_capex, factor_opex=factor_opex)
        # self.van_ahorros_autogen = valor_actual(flujo, self.tasa)

    def calc_van_autogen_separado(self):
        pv_syst = self.pta.pta_pvs_grid_pv_system
        I0 = inversion_pv(pv_syst) * self.factor_analisis_inversion
        self.inv_autogen = I0
        coma = coma_pv_list(pv_syst, self.n_years)
        elec_ex = self.list_year_ex_auto_gen

        f2 = []
        for i in range(0, len(elec_ex)):
            f = elec_ex[i] + coma[i]
            f2.append(f)

        val_act_autogen = valor_actual(f2, self.tasa)
        return round(I0), round(val_act_autogen)

    def calc_van_ntbg(self, factor_capex, factor_opex):
        pv_syst = self.pta.pta_pvs_ntbg_pv_system
        Ipv = inversion_pv(pv_syst) * self.factor_analisis_inversion
        I_ntbg = tramites_ntbg + medidor_bidireccional
        I0 = Ipv + I_ntbg
        self.inv_ntbg = I0
        coma = coma_pv_list(pv_syst, self.n_years)
        elec_ex = self.list_year_ex_ntbg
        gasto_base = self.list_year_ex_base

        # flujo = []
        # for i in range(0, len(gasto_base)):
        # f = gasto_base[i] - (elec_ex[i] + coma[i])
        # flujo.append(f)

        f2 = []
        for i in range(0, len(elec_ex)):
            f = elec_ex[i] + coma[i]
            f2.append(f)

        self.van_ntbg = V_A_N_ponderado(f2, I0, self.tasa, factor_capex=factor_capex, factor_opex=factor_opex)
        # self.van_ahorros_ntbg = valor_actual(flujo, self.tasa)

    def calc_van_ntbg_separado(self):
        pv_syst = self.pta.pta_pvs_ntbg_pv_system
        Ipv = inversion_pv(pv_syst) * self.factor_analisis_inversion
        I_ntbg = tramites_ntbg + medidor_bidireccional
        I0 = Ipv + I_ntbg
        self.inv_ntbg = I0
        coma = coma_pv_list(pv_syst, self.n_years)
        elec_ex = self.list_year_ex_ntbg

        f2 = []
        for i in range(0, len(elec_ex)):
            f = elec_ex[i] + coma[i]
            f2.append(f)

        val_act_ntbg = valor_actual(f2, self.tasa)
        return round(I0), round(val_act_ntbg)

    def calc_van_offgrid(self):
        pv_syst = self.pta.pta_off_grid_pv_system
        banco = self.pta.battery_bank
        I0_pv = inversion_pv(pv_syst)
        I0_bat = inversion_baterias(banco)
        self.inv_banco = I0_bat
        I0 = I0_bat + I0_pv
        self.inv_offgrid = I0

        coma_pv_s = coma_pv_list(pv_syst, self.n_years)
        coma_bat_s = coma_bat_list(banco, self.n_years)
        coma_total = []
        flujo = []
        for i in range(0, self.n_years):
            gasto = coma_bat_s[i] + coma_pv_s[i]
            coma_total.append(gasto)
            no_gastado = self.list_year_ex_base[i]
            ahorro = no_gastado - gasto
            flujo.append(ahorro)

        self.van_offgrid = V_A_N_ponderado(flujo, I0, self.tasa)
        self.van_ahorros_offgrid = valor_actual(flujo, self.tasa)

    def calc_van_offgrid_separado(self):
        # capacida_bat kWh
        pv_system = self.pta.off_grid_pv_system
        capacidad_bat = self.pta.banco.capacidad
        power_bate = self.pta.banco.potencia
        print("capacidad_bat vgvgg ", capacidad_bat)

        I0_pv = inversion_pv(pv_system)
        I0_bat = inversion_baterias_2(capacidad=capacidad_bat, potencia=power_bate)

        I0 = I0_pv + I0_bat
        dd = self.list_year_ex_off_grid
        f1 = coma_pv_list(pv_system, self.n_years)
        f2 = coma_bat_list_2(self.pta.banco, self.n_years)

        flujo = []
        for i in range(0, self.n_years):
            a = f1[i] + f2[i]
            flujo.append(a)

        val_act_off_grid = valor_actual(flujo, self.tasa)
        return round(I0), round(val_act_off_grid)


'''        
        # resultados run_pta_grid (dtg -> demand to grid)
        self.cost_year_energy_pta_grid = self.pta.cost_year_energy_pta_grid
        self.cost_months_energy_pta_grid = self.pta.cost_months_energy_pta_grid


        # resultados pta_pvs_grid
        self.cost_year_energy_pta_pvs_grid = self.pta.cost_year_energy_pta_pvs_grid
        self.cost_months_energy_pta_pvs_grid = self.pta.cost_months_energy_pta_pvs_grid

        # resultados pta_pvs_ntbg
        self.cost_year_energy_pta_pvs_ntbg = self.pta.cost_year_energy_pta_pvs_ntbg
        self.cost_months_energy_pta_pvs_ntbg = self.pta.cost_months_energy_pta_pvs_ntbg
        self.valor_inyecciones_no_usado = self.pta.valor_inyecciones_no_usado'''
