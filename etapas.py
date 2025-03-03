import pvlib

from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import pandas as pd
import matplotlib.pyplot as plt


def buscarv(indice_buscado, lista_indice, lista_datos):
    indice = lista_indice.index(indice_buscado)
    valor = lista_datos[indice]
    return valor


def promedio_lista(lista):
    n = len(lista)
    suma = 0
    for i in range(0, n):
        suma += lista[i]
    return suma/n


def separa_en_dias(lista):
    days = []
    cuenta1 = 0
    while cuenta1 <= 364:
        start = (cuenta1 * 24)
        finish = start + 24
        day = []

        # aprovecho el mismo for para calcular dos cosas
        for i in range(start, finish):
            power_i = lista.iloc[i]
            day.append(power_i)
        days.append(day)
        cuenta1 += 1
    return days



def promedios(lista_de_listas_entrada):
    lista_de_listas_salida = []
    for i in range(0, 24):
        suma = 0
        for k in range(0, len(lista_de_listas_entrada)):
            valor = lista_de_listas_entrada[k][i]
            suma += valor
        promedio = suma / len(lista_de_listas_entrada)
        lista_de_listas_salida.append(promedio)
    return lista_de_listas_salida


def separa_estaciones(lista_de_listas):
    listas_verano = []
    listas_otono = []
    listas_invierno = []
    listas_primavera = []

    verano = 79
    otono = verano + 93
    invierno = otono + 92
    primavera = invierno + 91
    verano2 = primavera + 10
    for i in range(0, 365):
        if i < verano:
            listas_verano.append(lista_de_listas[i])
        elif verano < i < otono:
            listas_otono.append(lista_de_listas[i])
        elif otono < i < invierno:
            listas_invierno.append(lista_de_listas[i])
        elif invierno < i < primavera:
            listas_primavera.append(lista_de_listas[i])
        elif i < verano2:
            listas_verano.append(lista_de_listas[i])

    return listas_verano, listas_otono, listas_invierno, listas_primavera


def promedios_estaciones(lista):
    datos2 = separa_en_dias(lista)
    listas_verano, listas_otono, listas_invierno, listas_primavera = separa_estaciones(datos2)
    prom_verano = promedios(listas_verano)
    prom_otono = promedios(listas_otono)
    prom_invierno = promedios(listas_invierno)
    prom_primavera = promedios(listas_primavera)

    return prom_verano, prom_otono, prom_invierno, prom_primavera


def aumento_lineal(valor_i, factor, periodos):
    nueva_lista = []
    for i in range(0, periodos):
        nueva_lista.append(valor_i * factor * i)
    return nueva_lista


def energy(year_power):
    days = []
    days_energy = []
    year_energy = 0

    cuenta1 = 0
    while cuenta1 <= 364:
        start = (cuenta1 * 24)
        finish = start + 24
        day = []
        suma_diaria = 0
        # aprovecho el mismo for para calcular dos cosas
        for i in range(start, finish):
            power_i = year_power[i]
            day.append(power_i)
            suma_diaria += power_i
        days.append(day)
        days_energy.append(suma_diaria)
        year_energy += suma_diaria
        cuenta1 += 1

    lista_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    months_energy = []
    cuenta2 = 0
    for i in range(0, len(lista_meses)):
        suma_mes = 0
        for k in range(cuenta2, cuenta2 + lista_meses[i]):
            suma_mes += days_energy[k]
        months_energy.append(suma_mes)
        cuenta2 += lista_meses[i]
    return year_energy, months_energy, days_energy, days


def suma_elementos_sublistas(lista_de_sublistas):  # crado usando Chant GPT
    if not lista_de_sublistas:
        return []  # Devolver una lista vacía si no hay sublistas

    # Asumimos que todas las sublistas tienen la misma longitud
    longitud_sublistas = len(lista_de_sublistas[0])

    # Inicializar una lista para almacenar las sumas
    sumas = [0] * longitud_sublistas

    for sublista in lista_de_sublistas:
        for i, elemento in enumerate(sublista):
            sumas[i] += elemento
    return sumas


def repetir_365(lista):
    assert len(lista) == 24
    lista_365 = []
    n = 0
    while n < 365:
        for i in range(0, len(lista)):
            lista_365.append(lista[i])
        n += 1
    return lista_365


def extraer_iloc(panda):
    lista = []
    for i in range(0, 8760):
        lista.append(panda.iloc[i])
    return lista


def calc_demand_grid(energy_pta, energy_pvs):
    assert len(energy_pta) == len(energy_pvs)
    dif = []
    for i in range(0, len(energy_pta)):
        a = energy_pta[i] - energy_pvs[i]
        if a < 0:
            a = 0
        dif.append(a)
    return dif


def calc_demand_grid_ntbg(energy_pta, energy_pvs):
    assert len(energy_pta) == len(energy_pvs)
    dtg = []
    exce = []
    for i in range(0, len(energy_pta)):
        dif = energy_pta[i] - energy_pvs[i]

        if dif < 0:
            exce.append(dif * (-1))
            dtg.append(0)
        else:
            exce.append(0)
            dtg.append(dif)
    return dtg, exce


def calc_demand_to_battery(energy_pta, energy_pvs):
    assert len(energy_pta) == len(energy_pvs)
    dif = []
    to_bat = []
    to_pta = []
    for i in range(0, len(energy_pta)):
        a = energy_pta[i] - energy_pvs[i]
        if a < 0:  # cuando hay mas pv que pta
            to_bat.append(a * (-1))
            to_pta.append(energy_pta[i])
        elif a >= 0 and energy_pvs[i] > 0:  # cuando hay pv pero es menor que pta
            to_bat.append(0)
            to_pta.append(energy_pvs[i])
        elif a >= 0 and energy_pvs[i] <= 0:  # cunado no hay pv
            to_bat.append(0)
            to_pta.append(0)
        dif.append(a)
    return dif, to_bat, to_pta


def pd_to_list_float(pd_array, conversion):
    lista = []
    for i in range(0, 8760):
        n = pd_array.iloc[i]
        flt = float(n) / conversion
        lista.append(flt)
    return lista


class ACPump(object):
    """
    Class que reprsenta el sistema de bombeo compuesto por una
    bomba y un motor AC

    Atributos

    em: eficiencia del motor
    ed: eficiencia de la transmisión
    ep: eficiencia de la bomba
    head: altura del bombeo
    w_dsty: densidad del agua en Kg/m^3 (1000 por defecto)

    Métodos
    power(self, flow_rate): Calcula la potencia a cada hora del año
                y retorna un vector de largo 8760 con los valores
                calculados

    energy(self): usa el self.year_power creado por power(self, flow_rate)
                para calcular:
                year_energy -> la energía total anual consumida
                months_energy -> una lista de largo 12, cada elemento en la energía
                    consumida en cada mes
                days_energy -> una lista de largo 365, cada elemento es la energía
                    consumida en un día
                days -> una lista de largo 365, que contiene sublistas de largo 24,
                    cada sublista contiene la potencia consumida cada hora
    run(self): ejecuta los métodos power y energy en orden, para escribir los atributos
                year_power, year_energy, months_energy, days_energy, y days_power.
    """

    def __init__(self, head, em=0.95, ed=1, ep=1, w_dsty=1000, L=1, D=1, fpa=1):
        self.head = head  # [m]
        self.eww = em * ed * ep  # [p.u.]
        self.w_dsty = w_dsty  # [Kg/m3]
        self.fpa = fpa

        self.L = L
        self.D = D
        self.V = 1
        self.f = 1
        self.Hpf = (self.f * self.L * self.V ** 2) / (self.D * 2 * 9.81)
        self.Hv = (self.V ** 2) / (2 * 9.81)
        self.TDH = self.head + self.Hpf + self.Hv

        self.year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None

        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

    # power(self, flow_rate) ->
    def power(self, flow_rate):
        # print("calculando power de AC pump")
        rho = self.w_dsty
        g = 9.81  # [m/s2]
        h = self.head
        eww = self.eww
        Ppump_8760 = []
        for i in range(0, len(flow_rate)):
            Qm3s = flow_rate[i] / 3600  # flow_rate m3/h -> m3/s
            P_pump = ((Qm3s * g * rho * h) / eww) / 1000  # [kW]
            Ppump_8760.append(P_pump)
        self.year_power = Ppump_8760
        self.consumo_sin_perdidas = flow_rate

    # este energy() queda como respaldo)
    def energy(self):
        days = []
        days_energy = []
        year_energy = 0

        cuenta1 = 0
        while cuenta1 <= 364:
            start = (cuenta1 * 24)
            finish = start + 24
            day = []
            suma_diaria = 0
            # aprovecho el mismo for para calcular dos cosas
            for i in range(start, finish):
                power_i = self.year_power[i]
                day.append(power_i)
                suma_diaria += power_i
            days.append(day)
            days_energy.append(suma_diaria)
            year_energy += suma_diaria
            cuenta1 += 1

        lista_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        months_energy = []
        cuenta2 = 0
        for i in range(0, len(lista_meses)):
            suma_mes = 0
            for k in range(cuenta2, cuenta2 + lista_meses[i]):
                suma_mes += days_energy[k]
            months_energy.append(suma_mes)
            cuenta2 += lista_meses[i]

        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * self.fpa)
        self.consumo_con_perdidas = consumo_con_perdidas

    def run(self, flow_rate):
        self.power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class MeteringPump(object):
    """

    """

    def __init__(self, head, factor, em=0.9, ed=0.9, ep=0.9, w_dsty=1000):
        self.head = head  # [m]
        self.eww = em * ed * ep  # [p.u.]
        self.w_dsty = w_dsty  # [Kg/m3]
        self.factor = factor

        self.year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None

        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

    # power(self, flow_rate) ->
    def power(self, flow_rate):
        # print("calculando power de metering pump")
        rho = self.w_dsty
        g = 9.81  # [m/s2]
        h = self.head
        eww = self.eww
        Ppump_8760 = []
        for i in range(0, len(flow_rate)):
            # el factor es el porcentaje de cloro c/r al flow rate
            Qm3s = (flow_rate[i] * self.factor) / 3600  # flow_rate m3/h -> m3/s
            P_pump = ((Qm3s * g * rho * h) / eww) / 1000  # [kW]
            Ppump_8760.append(P_pump)
        self.year_power = Ppump_8760
        self.consumo_sin_perdidas = flow_rate

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * 1)
        self.consumo_con_perdidas = consumo_con_perdidas

    def run(self, flow_rate):
        self.power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class Coagulation(object):
    """
    Clase que representa una etapa de coagulación

    Atributos:
    t_det: tiempo de detención [s]
    motor_effi: eficiencia del potor que mueve las paletas del flash mix
    G: gradeinte de velocidad [1/s], entre 600 y 1000 (800 por defecto)
    dynamic_viscosity: viscosidad dinámica del agua [N*s/m^2], (0.00089 por defecto)
    coag_dsty: densidad del coagulante utilizado
    coag_head: altura de bombeo del coagulante
    m_pmp_effi: eficiencia de la bomba_motor (metering pump)

    Métodos
    flash_mix_power(self, flow_rate): calcula la potencia del flash mix en las 8760 horas del año

    coagulant_adition_power(self, coag_flow_rate): calcula la potencia del coag adition en las 8760 horas del año

    run(self, flow_rate, coag_flow_rate): ejecuta las cosas en orden, y escribe los resultados
    """

    def __init__(self, t_det, n_etapas=1, motor_effi=0.8, G=800, dynamic_viscosity=0.00089,
                 coag_dsty=1100, coag_head=1, m_pmp_effi=0.8, fpa=1):
        self.G = G
        self.dynamic_viscosity = dynamic_viscosity
        self.motor_effi = motor_effi
        self.t_det = t_det
        self.n_etapas = n_etapas
        self.fpa = fpa

        # coagulante
        self.coag_dsty = coag_dsty
        self.coag_head = coag_head
        self.m_pmp_effi = m_pmp_effi
        # resultados
        self.FM_year_power = None
        self.CA_year_power = None
        self.year_power = None

        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None

        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

    def flash_mix_power(self, flow_rate):
        # print("calculando power de flash_mix")
        G = self.G
        mu = self.dynamic_viscosity
        t_det = self.t_det
        eww = self.motor_effi
        Pfmx_8760 = []
        for i in range(0, len(flow_rate)):
            Qm3s = (flow_rate[i] / 3600) / self.n_etapas  # consumo m3/h -> m3/s
            P_fmx = ((G ** 2 * Qm3s * t_det * mu) / eww) / 1000  # [kW]
            Pfmx_8760.append(P_fmx)
        self.FM_year_power = Pfmx_8760
        self.consumo_sin_perdidas = flow_rate

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * self.fpa)
        self.consumo_con_perdidas = consumo_con_perdidas

    def coagulant_adition_power(self, flow_rate):
        # print("calculando power de coagulant_adition")
        rho = self.coag_dsty
        g = 9.81  # [m/s2]
        h = self.coag_head
        eww = self.m_pmp_effi
        P_Mpump_8760 = []
        for i in range(0, len(flow_rate)):
            # el flow rate del coagulante se calcula como un 5% del flow rate de consumo
            Qm3s = ((flow_rate[i] / 3600) / self.n_etapas) * 0.05  # flow_rate m3/h -> m3/s
            P_Mpump = ((Qm3s * g * rho * h) / eww) / 1000  # [kW]
            P_Mpump_8760.append(P_Mpump)
        self.CA_year_power = P_Mpump_8760

    def run(self, flow_rate):
        self.flash_mix_power(flow_rate)
        self.coagulant_adition_power(flow_rate)
        self.year_power = suma_elementos_sublistas([self.FM_year_power, self.CA_year_power])
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class Floculation(object):
    """
    Clase que representa una etapa de floculación

    Atributos:
    t_det: tiempo de detención [s]
    motor_effi: eficiencia del potor que mueve las paletas del flash mix
    G: gradeinte de velocidad [1/s], entre 600 y 1000 (800 por defecto)
    dynamic_viscosity: viscosidad dinámica del agua [N*s/m^2], (0.00089 por defecto)

    Métodos
    slow_mix_power(self, flow_rate): calcula la potencia del flash mix en las 8760 horas del año

    run(self, flow_rate: ejecuta las cosas en orden, y escribe los resultados
    """

    def __init__(self, t_det, n_etapas=1, motor_effi=0.8, G=50, dynamic_viscosity=0.00089, fpa=1):
        self.G = G
        self.dynamic_viscosity = dynamic_viscosity
        self.motor_effi = motor_effi
        self.t_det = t_det
        self.n_etapas = n_etapas
        self.fpa = fpa

        # resultados
        self.year_power = None

        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None

        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

    def slow_mix_power(self, flow_rate):
        # print("calculando power de slow_mix")
        G = self.G
        mu = self.dynamic_viscosity
        t_det = self.t_det
        eww = self.motor_effi
        Psmx_8760 = []
        for i in range(0, len(flow_rate)):
            Qm3s = (flow_rate[i] / 3600) / self.n_etapas  # consumo m3/h -> m3/s
            P_smx = ((G ** 2 * Qm3s * t_det * mu) / eww) / 1000  # [kW]
            Psmx_8760.append(P_smx)
        self.year_power = Psmx_8760
        self.consumo_sin_perdidas = flow_rate

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * self.fpa)
        self.consumo_con_perdidas = consumo_con_perdidas

    def run(self, flow_rate):
        self.slow_mix_power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class Consumo(object):
    """
    clase para el consumo de agua

    Atributos:

    consumo_diario: lista de largo 24 con el consumo de cada hora del día en m3/h
    consumo_365: lista de largo 8760 con el consumo de agua cada día del año en m3/h
    """

    def __init__(self, consumo_diario, hora_i=None, hora_f=None):
        self.consumo_diario = consumo_diario
        self.consumo_365 = None
        self.consumo_total_dia = None
        self.hora_i = None
        self.hora_f = None

        self.proyeccion_consumos = None

        if type(consumo_diario) == list:
            assert len(consumo_diario) == 24
            self.consumo_365 = repetir_365(self.consumo_diario)

        elif type(consumo_diario) == int or type(consumo_diario) == float:
            self.hora_i = hora_i
            self.hora_f = hora_f
            self.consumo_total_dia = self.consumo_diario
            self.consumo_diario = self.consumo_horario()
            self.consumo_365 = repetir_365(self.consumo_diario)

    def consumo_horario(self):
        n_horas = self.hora_f - self.hora_i
        Q = self.consumo_diario / n_horas
        consumo = []
        for i in range(0, 24):
            if self.hora_i <= i < self.hora_f:
                consumo.append(Q)
            else:
                consumo.append(0)
        return consumo

    def consumo_variable_estacion(self):
        consumo_base = repetir_365(self.consumo_diario)
        nuevo_consumo = []
        horas_por_estacion = 2190
        verano = 79 * 24
        otono = verano + (93 * 24)
        invierno = otono + (71 * 24)
        primavera = invierno + (113 * 24)
        verano2 = primavera + (9 * 24) - 1
        for i in range(0, 8760):
            if i < verano:
                nuevo_consumo.append(consumo_base[i] * 1.05)
            elif verano < i < otono:
                nuevo_consumo.append(consumo_base[i] * 1)
            elif otono < i < invierno:
                nuevo_consumo.append(consumo_base[i] * 0.95)
            elif invierno < i < primavera:
                nuevo_consumo.append(consumo_base[i] * 1)
            elif i <= verano2:
                nuevo_consumo.append(consumo_base[i] * 1.05)
        return nuevo_consumo

    def proyeccion_lineal_consumos(self, n_years, porcentaje_anual):
        suma = 1
        lista = []
        for i in range(0, n_years):
            lista.append(self.consumo_total_dia * suma)
            suma += porcentaje_anual
        return lista

    def proyeccion_lineal_consumos_2(self, n_years, porcentaje_anual):
        suma = 1
        lista = []
        for i in range(0, n_years):
            lista.append(self.consumo_total_dia * suma)
            suma += porcentaje_anual
        self.proyeccion_consumos = lista

    def consumo_vida_util(self, n_years):
        assert type(self.proyeccion_consumos) == list
        suma = 0
        for i in range(0, n_years):
            a = self.proyeccion_consumos[i]*365
            suma += a
        return suma

    def consumo_vida_util_lista(self, n_years):
        lista = []
        for i in range(0, n_years):
            a = self.proyeccion_consumos[i] * 365
            lista.append(a)
        return lista

    def plot_comsumo_diario(self):
        t = range(0, 24)
        plt.figure()
        plt.grid(True)
        plt.plot(t, self.consumo_diario)
        plt.xlabel('Horas')
        plt.ylabel("m3/s")
        plt.title('Producción horaria de agua')
        plt.show()

    def suma_consumo_anual(self):
        suma = sum(self.consumo_365)
        return suma
class ReverseOsmosisFixSEC(object):
    """
    calcula el power consumido por el RO, a partir de un SEC fijo dado
    """

    def __init__(self, sec_ro=2, fpa=1):
        self.year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None
        self.sec = sec_ro
        self.fpa = fpa
        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

    def ro_power(self, consumtion):
        ro_power_8760 = []
        for i in range(0, 8760):
            p = consumtion[i] * self.sec
            ro_power_8760.append(p)
        self.year_power = ro_power_8760
        self.consumo_sin_perdidas = consumtion

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * self.fpa)
        self.consumo_con_perdidas = consumo_con_perdidas

    def run(self, flow_rate):
        self.ro_power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class ReverseOsmosisShaoChi(object):
    """
    calcula el porwer consumido por el RO a partir de un SEC calculado a partir del podelo de:
    Evaluation of the Specific Energy Consumption of Sea Water
    Reverse Osmosis Integrated with Membrane Distillation and
    Pressure–Retarded Osmosis Processes with Theoretical Models - Shao-Chi Tsai

    los valores que entrega son un poco altos a mi juicio
    """

    def __init__(self, salinity, temperature=298, rejection_rate=0.99,
                 water_recovery_rate=0.5, motor_effi=0.8, erd_effi=None):
        self.salinity = salinity
        self.temperature = temperature
        self.rejection_rate = rejection_rate
        self.water_recovery_rate = water_recovery_rate
        self.motor_effi = motor_effi
        if erd_effi is None:
            self.erd_effi = 0
        else:
            self.erd_effi = erd_effi
        self.i = 1.9
        self.R = 8.31446261815324
        self.year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None

        self.fpa = 0.9
        self.consumo_sin_perdidas = None
        self.consumo_con_perdidas = None

        self.pi = self.i * self.salinity * self.R * self.temperature
        self.sec_ro = (self.pi * self.rejection_rate * (1 - self.erd_effi * (1 - self.water_recovery_rate))) / \
                      (self.motor_effi * self.water_recovery_rate * (1 - self.water_recovery_rate))
        self.sec = self.sec_ro

    def perdidas_agua(self):
        consumo_con_perdidas = []
        for i in range(0, len(self.consumo_sin_perdidas)):
            consumo_con_perdidas.append(self.consumo_sin_perdidas[i] * self.fpa)
        self.consumo_con_perdidas = consumo_con_perdidas

    def ro_power(self, consumtion):
        ro_power_8760 = []
        for i in range(0, 8760):
            p = consumtion[i] * self.sec_ro
            ro_power_8760.append(p)
        self.year_power = ro_power_8760
        self.consumo_sin_perdidas = consumtion

    def run(self, flow_rate):
        self.ro_power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days
        self.perdidas_agua()


class ReverseOsmosisAlanood(object):
    """
    calcula el power del ro a partir de un SEC calculado con las formulas de:
    'Evaluation and minimisation of energy consumption in a mediumscale
    reverse osmosis brackish water desalination plant' - Alanood A. Alsarayreh
    """

    def __init__(self, effi_ERD, Pf_in_plant=9.22, RR1=0.75, RR2=0.85, Pcoef1=0.85, effi_hhp=0.8, effi_bp=0.8):
        self.effi_ERD = effi_ERD
        self.Pf_in_plant = Pf_in_plant
        self.RR1 = RR1
        self.RR2 = RR2
        self.Pcoef1 = Pcoef1
        self.effi_hpp = effi_hhp
        self.effi_bp = effi_bp
        self.Pf_pass_1 = self.Pf_in_plant * self.Pcoef1
        self.Pf_B_pump = self.Pf_in_plant - (self.Pf_pass_1 * self.effi_ERD)
        self.sec = None
        self.year_power = None
        self.year_energy = None
        self.months_energy = None
        self.days_energy = None
        self.days_power = None
        self.consumo_con_perdidas = None

    """def calc_sec(self, test=50):
        Qp_total_plant = test / 3600
        Qf_pass_2 = Qp_total_plant / self.RR2  # salida limpia Pass 1 = entrada Pass 2

        Qf_in_plant = Qf_pass_2 / self.RR1  # entrada combinada al Pass 1
        Qr_pass_1 = Qf_in_plant * (1 - self.RR1)  # salida sucia Pass 1

        Q_recycled = Qf_pass_2 * (1 - self.RR2)  # salida sucia Pass 2
        Q_rw = Qf_in_plant - Q_recycled  # entrada de agua cruda
        E_HPP = (self.Pf_in_plant * 101325 * Qf_in_plant) / (Qp_total_plant * self.effi_hpp)
        E_BP = (self.Pf_B_pump * 101325 * Qf_pass_2) / (Qp_total_plant * self.effi_bp)
        E_ERD = (self.Pf_pass_1 * 101325 * Qr_pass_1 * self.effi_ERD) / Qp_total_plant

        SEC = (E_HPP + E_BP - E_ERD) / (3600 * 1000)
        self.sec = SEC
        self.consumo_con_perdidas = Q_rw"""

    def ro_power(self, consumtion):
        # print("calculando power de RO")
        ro_power_8760 = []
        agua_cruda = []
        for i in range(0, 8760):
            Qp_total_plant = consumtion[i]  # m3h porque la expresión es la energía consumida por m3 de agua
            if consumtion[i] == 0:
                Qp_total_plant = 0.001
            # si le doy m3h, será la energía que se consumió durante una hora con esa potencia media
            Qf_pass_2 = Qp_total_plant / self.RR2  # salida limpia Pass 1 = entrada Pass 2

            Qf_in_plant = Qf_pass_2 / self.RR1  # entrada combinada al Pass 1
            Qr_pass_1 = Qf_in_plant * (1 - self.RR1)  # salida sucia Pass 1

            Q_recycled = Qf_pass_2 * (1 - self.RR2)  # salida sucia Pass 2
            Q_rw = Qf_in_plant - Q_recycled  # entrada de agua cruda
            E_HPP = (self.Pf_in_plant * 101325 * Qf_in_plant) / (Qp_total_plant * self.effi_hpp)
            E_BP = (self.Pf_B_pump * 101325 * Qf_pass_2) / (Qp_total_plant * self.effi_bp)
            E_ERD = (self.Pf_pass_1 * 101325 * Qr_pass_1 * self.effi_ERD) / Qp_total_plant

            SEC = (E_HPP + E_BP - E_ERD) / (3600 * 1000)
            self.sec = SEC
            agua_cruda.append(Q_rw)
            ro_power = self.sec * Qp_total_plant
            ro_power_8760.append(ro_power)
        self.year_power = ro_power_8760
        self.consumo_con_perdidas = agua_cruda

    def run(self, flow_rate):
        # self.calc_sec(test=50)
        self.ro_power(flow_rate)
        year_energy, months_energy, days_energy, days = energy(self.year_power)
        self.year_energy = year_energy
        self.months_energy = months_energy
        self.days_energy = days_energy
        self.days_power = days


sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')
cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')
module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
inverter = cec_inverters['ABB__PVI_3_0_OUTD_S_US__208V_']
temperature_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']


class SolarSystem(object):
    """

    """

    def __init__(self, latitude, longitude, altitude, name,
                 surface_tilt, surface_azimuth,
                 modules_per_string, strings_per_inverter,
                 tz="America/Santiago",
                 module_parameters=module, inverter_parameters=inverter,
                 temperature_model_parameters=temperature_parameters):
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
        '''print(type(self.modelchain.results.dc))
        #self.year_power_dc = pd_to_list_float(self.modelchain.results.dc)
        self.year_power_dc = self.modelchain.results.dc
        print(self.modelchain.results.dc.iloc[13].iloc[4])
        year_energy_dc, months_energy_dc, days_energy_dc, days_dc = energy(self.year_power_dc)
        self.year_energy_dc = year_energy_dc
        self.months_energy_dc = months_energy_dc
        self.days_energy_dc = days_energy_dc
        self.days_power_dc = days_dc'''

        self.year_power_ac = pd_to_list_float(self.modelchain.results.ac, 1000)
        year_energy_ac, months_energy_ac, days_energy_ac, days_ac = energy(self.year_power_ac)
        self.year_energy_ac = year_energy_ac
        self.months_energy_ac = months_energy_ac
        self.days_energy_ac = days_energy_ac
        self.days_power_ac = days_ac


'''class RedElec(object):

    def __init__(self, cargo_f_m, cargo_v_servicio_publico_m, cargo_v_transp_m,
                 tarifa_v_m, tarifa_inyeccion, voltaje=220, frecuencia=50, inyecta=99999999,
                 absorbe=99999999):
        self.voltaje = voltaje
        self.frecuenia = frecuencia
        self.inyecta = inyecta
        self.absorbe = absorbe
        self.tarifa_inyeccion = tarifa_inyeccion
        self.cargo_f_m = cargo_f_m
        self.cargo_v_servicio_publico_m = cargo_v_servicio_publico_m
        self.cargo_v_transp_m = cargo_v_transp_m
        self.tarifa_v_m = tarifa_v_m'''


class Banco(object):
    """

    """

    def __init__(self, capacidad, potencia, voltaje):

        self.capacidad = capacidad
        self.potencia = potencia
        self.voltaje = voltaje


