def regola_luce(light, occupancy):
    if not occupancy:
        if light >= 300:
            return "Spegni luce"
        return "Nessuna azione"
    if light < 100:
        return "Accendi luce"
    elif light > 800:
        return "Spegni luce"
    return "Nessuna azione"


def regola_riscaldamento(temp, occupancy):
    if not occupancy:
        if temp >= 25:
            return "Spegni riscaldamento"
        return "Nessuna azione"
    if occupancy and temp < 19:
        return "Accendi riscaldamento"
    elif temp >= 28:
        return "Spegni riscaldamento"
    return "Nessuna azione"

    
def regola_tapparelle(light, occupancy):
    if not occupancy:
        if light >= 800:
            return "Abbassa tapparelle"
        return "Nessuna azione"
    if light > 800 and occupancy:
        return "Abbassa tapparelle"
    elif light < 200 and occupancy:
        return "Alza tapparelle"
    return "Nessuna azione"


def regola_climatizzatore(temp, occupancy):
    if not occupancy:
        if temp <= 21:
            return "Spegni climatizzatore"
        return "Nessuna azione"
    if occupancy and temp > 28:
        return "Accendi climatizzatore"
    elif occupancy and temp <= 28 and temp >= 21:
        return "Spegni climatizzatore"
    return "Nessuna azione"


def azioni_da_regole(light, temp, occupancy):
    return {
        regola_luce(light, occupancy),
        regola_riscaldamento(temp, occupancy),
        regola_tapparelle(light, occupancy),
        regola_climatizzatore(temp, occupancy)
    }
