import matplotlib.pyplot as plt
import etapas
import pandas as pd


def cuenta_soc(list_soc):
    cuenta_soc0 = 0
    cuenta_soc_04 = 0
    cuenta_soc_03 = 0
    cuenta_soc_02 = 0
    cuenta_soc_01 = 0

    for i in range(0, len(list_soc)):
        if list_soc[i] == 0:
            cuenta_soc0 += 1
        elif list_soc[i] < 0.1:
            cuenta_soc_01 += 1
        elif list_soc[i] < 0.2:
            cuenta_soc_02 += 1
        elif list_soc[i] < 0.3:
            cuenta_soc_03 += 1
        elif list_soc[i] < 0.4:
            cuenta_soc_04 += 1

    return cuenta_soc0, cuenta_soc_04, cuenta_soc_03, cuenta_soc_02, cuenta_soc_01


class BatteryBank(object):
    """
    gaskd
    """

    def __init__(self, capacidad, tiempo_nom=10, limite_cc=0.1):
        self.voltaje = 360
        self.capacidad = capacidad
        self.tiempo_nom = tiempo_nom
        self.limite_cc = limite_cc
        self.max_charge_current = self.capacidad * self.limite_cc
        self.soc = 1
        self.list_soc = [self.soc]
        self.power_desc = []
        self.power_to_bat = None
        self.power_to_pta = None

    def factor(self):
        soc = self.soc
        factor = 1
        if 0 < soc <= 0.6:
            factor = 0.9
        elif 0.6 < soc <= 0.7:
            factor = 0.85
        elif 0.7 < soc <= 0.8:
            factor = 0.5
        elif 0.8 < soc <= 0.9:
            factor = 0.3
        elif 0.9 < soc <= 0.95:
            factor = 0.2
        elif 0.95 < soc <= 1:
            factor = 0.1
        # print(factor)
        return factor

    def limit_char_current(self, corriente):
        c10 = self.capacidad
        max_charging_current = self.limite_cc * c10
        if corriente > max_charging_current:
            return max_charging_current * self.factor()
        elif corriente < 0:
            return 0
        else:
            return corriente * self.factor()

    def descarga(self, corriente_i):
        assert corriente_i >= 0
        Qd = corriente_i  # kAh
        soc = self.soc - (Qd / self.capacidad)
        power_desc = Qd * self.voltaje  # kWh
        self.soc = soc

        if self.soc > 1:
            self.soc = 1
        elif self.soc < 0:
            self.soc = 0
        else:
            pass
        self.list_soc.append(self.soc)
        self.power_desc.append(power_desc)

    def carga(self, corriente_i):
        assert corriente_i < 0
        Ic = corriente_i * (-1)  # kA
        Q_charge = self.limit_char_current(corriente=Ic)  # kAh
        self.soc += Q_charge / self.capacidad  # p.u.

        if self.soc > 1:
            self.soc = 1
        elif self.soc < 0:
            self.soc = 0
        else:
            pass
        self.list_soc.append(self.soc)
        self.power_desc.append(0)

    def results_to_csv(self, pta_power, pv_power, power_diferencia):
        df1 = pd.DataFrame({"power_pta": pta_power})
        df2 = pd.DataFrame({"power_pvs": pv_power})
        df3 = pd.DataFrame({"power_dif": power_diferencia})

        pandita = pd.concat([df1, df2, df3], axis=1)
        pandita.to_csv("datos_chile/corrientes.csv")

    def cuenta_soc(self):
        cuenta_soc = 0
        cuenta_soc_04 = 0
        cuenta_soc_03 = 0
        cuenta_soc_02 = 0
        cuenta_soc_01 = 0

        for i in range(0, len(self.list_soc)):
            if self.list_soc[i] == 0:
                cuenta_soc += 1
            elif self.list_soc[i] < 0.1:
                cuenta_soc_01 += 1
            elif self.list_soc[i] < 0.2:
                cuenta_soc_02 += 1
            elif self.list_soc[i] < 0.3:
                cuenta_soc_03 += 1
            elif self.list_soc[i] < 0.4:
                cuenta_soc_04 += 1

        print("cuenta SOC = ", cuenta_soc)
        print("cuenta_soc_04 = ", cuenta_soc_04)
        print("cuenta_soc_03 = ", cuenta_soc_03)
        print("cuenta_soc_02 = ", cuenta_soc_02)
        print("cuenta_soc_01 = ", cuenta_soc_01)

    def run_battery(self, pta_power, pv_power):
        pv_power_corregido = []
        for k in range(0, len(pv_power)):
            if pv_power[k] < 0:
                pv_power_corregido.append(0)
            else:
                pv_power_corregido.append(pv_power[k])
        power_diferencia, power_to_bat, power_to_pta = etapas.calc_demand_to_battery(energy_pta=pta_power,
                                                                                     energy_pvs=pv_power_corregido)  # kW

        self.power_to_bat = power_to_bat
        self.power_to_pta = power_to_pta

        for i in range(0, len(power_diferencia)):
            corriente_i = (power_diferencia[i] / self.voltaje)  # kA
            if corriente_i < 0:
                self.carga(corriente_i)
            else:
                self.descarga(corriente_i)




Id1 = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
       10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

Id2 = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
       -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]

Id3 = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, -30, -30,
       -30, -30, -30, -30, -30, -30, 3, 3, 3, 3, 3, 3,
       3, 3, 3, 3, 3, 3, 3, 3, 3, 3, -30, -30,
       -30, -30, -30, -30, -30, -30, 3, 3, 3, 3, 3, 3]

Id4 = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, -20, -20,
       -20, -20, -20, -20, -20, -20, 3, 3, 3, 3, 3, 3]

Id5 = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10,
       -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]

Id = [5, 5, 10, 10, 10, 10, 10, 10, 10, 10, -30, -30,
      -30, -30, -30, -30, -30, -30, 10, 10, 10, 10, 5, 5,
      5, 5, 10, 10, 10, 10, 10, 10, 10, 10, -30, -30,
      -30, -30, -30, -30, -30, -30, 10, 10, 10, 10, 5, 5]

Id6 = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, -30, -30,
       -30, -30, -30, -30, -30, 5, 5, 5, 5, 5, 5, 5,
       5, 5, 5, 5, 5, 5, 5, 5, 5, 5, -30, -30,
       -30, -30, -30, -30, -30, 5, 5, 5, 5, 5, 5, 5,
       5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
       5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
       5, 5, 5, 5, 5, 5, 5, 5, 5, 5, -30, -30,
       -30, -30, -30, -30, -30, 5, 5, 5, 5, 5, 5, 5]

'''bat = BatteryBank(capacidad=500)
bat.run_battery(Id6)


time = range(0, len(Id6)+1)
plt.figure(figsize=(16,9))
plt.grid(True)
#plt.plot(time, Q_discharge_list, label="Q_discharge_list")
plt.plot(time, bat.list_soc, label="s_o_c_list")
plt.xlabel('horas')
plt.ylabel("voltaje terminales")
plt.title('resultadetes')
plt.legend()
plt.show()'''
