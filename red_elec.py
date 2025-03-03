class RedElec(object):

    def __init__(self, cargo_fijo_mensual, cargo_servicio_publico, cargo_transporte,
                 cargo_energia, cargo_potencia=0, tarifa_inyeccion=0, factor_analisis_tarifas=1):
        self.cargo_fijo_mensual_perma = cargo_fijo_mensual
        self.cargo_servicio_publico_perma = cargo_servicio_publico
        self.cargo_transporte_perma = cargo_transporte
        self.cargo_energia_perma = cargo_energia
        self.cargo_potencia_perma = cargo_potencia
        self.tarifa_inyeccion_perma = tarifa_inyeccion

        self.cargo_fijo_mensual = cargo_fijo_mensual
        self.cargo_servicio_publico = cargo_servicio_publico
        self.cargo_transporte = cargo_transporte
        self.cargo_energia = cargo_energia
        self.cargo_potencia = cargo_potencia
        self.tarifa_inyeccion = tarifa_inyeccion

        self.factor_analisis_tarifas = factor_analisis_tarifas

    def elec_ex(self, pote_contratada=0, months_energy=None, months_exedentes=None, valor_inyec_not_used=0):
        cost_year_energy = 0  # monto en pesos $
        cost_month_energy = []  # lista de valores monto en pesos $
        valor_inyec_not_used_local = valor_inyec_not_used  # monto en pesos $
        months_exe_list = []
        months_exe_valorizados_disponibles = []
        months_monto_inyec = []
        #print("valor_inyec_not_used_recibido: ", valor_inyec_not_used)
        for i in range(0, 12):
            #print(f" mes {i}")

            energy_m_i = months_energy[i]  # kWh

            excedentes_mi = 0
            if months_exedentes is not None:
                excedentes_mi = months_exedentes[i]
                #print("exedentes energia: ", excedentes_mi)
            # cargos variables (que dependen de la energía consumida)
            c_var = self.cargo_transporte + self.cargo_servicio_publico + self.cargo_energia

            monto_fijo = self.cargo_fijo_mensual
            monto_pote = self.cargo_potencia * pote_contratada
            monto_var = c_var * energy_m_i * self.factor_analisis_tarifas
            monto_inyec = self.tarifa_inyeccion * excedentes_mi

            monto_mensual = monto_fijo + monto_pote + monto_var - monto_inyec
            monto_mensual_ajustado = monto_mensual - valor_inyec_not_used_local

            acumulado = monto_inyec + valor_inyec_not_used_local

            months_monto_inyec.append(monto_inyec)
            months_exe_valorizados_disponibles.append(acumulado)
            #print(f"energia_mes_{i}: {energy_m_i}")
            #print(f"exedentes_mes_{i}: {excedentes_mi}")
            #print("monto_mensual_consumo: ", monto_fijo + monto_pote + monto_var)
            #print("monto_inyec: ", monto_inyec)

            #print("valor_inyec_not_used: ", valor_inyec_not_used)
            #
            if monto_mensual_ajustado > 0:
                valor_inyec_not_used_local = 0
                cost_month_energy.append(monto_mensual_ajustado)
                cost_year_energy += monto_mensual_ajustado
                #print("boleta:", monto_mensual_ajustado)
            else:
                aa = valor_inyec_not_used_local - monto_mensual
                valor_inyec_not_used_local = aa * (1 + 0.00404)  # ajuste por ipc mensual
                cost_month_energy.append(0)
                cost_year_energy += 0
                #print("boleta:", 0)
            months_exe_list.append(valor_inyec_not_used_local)
            #print("----------------------------------")
            #print(f"valor_inyec_not_used_local_{i}: ", valor_inyec_not_used_local)
        return cost_year_energy, cost_month_energy, valor_inyec_not_used_local, months_exe_list, \
               months_exe_valorizados_disponibles, months_monto_inyec

    def aumento_tarifa(self, factor):
        algo = 1 + factor
        self.cargo_fijo_mensual = self.cargo_fijo_mensual * algo
        self.cargo_servicio_publico = self.cargo_servicio_publico * algo
        self.cargo_transporte = self.cargo_transporte * algo
        self.cargo_energia = self.cargo_energia * algo
        self.cargo_potencia = self.cargo_potencia * algo
        self.tarifa_inyeccion = self.tarifa_inyeccion * algo

    def reset_tarifa(self):
        self.cargo_fijo_mensual = self.cargo_fijo_mensual_perma
        self.cargo_servicio_publico = self.cargo_servicio_publico_perma
        self.cargo_transporte = self.cargo_transporte_perma
        self.cargo_energia = self.cargo_energia_perma
        self.cargo_potencia = self.cargo_potencia_perma
        self.tarifa_inyeccion = self.tarifa_inyeccion_perma

