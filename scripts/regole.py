# REGOLA LUCE 
def regola_luce(illuminazione, occupazione, orario):
    if not occupazione:
        if illuminazione >= 300:
            return "Spegni luce"
        return "Nessuna azione"
    
    # Stanza occupata
    if illuminazione < 100:
        return "Accendi luce"
    elif illuminazione > 800:
        return "Spegni luce"

    # Regola temporale: di notte, luce accesa se sotto 200 lux
    if orario == "Notte" and illuminazione < 200:
        return "Accendi luce"

    return "Nessuna azione"


# REGOLA RISCALDAMENTO
def regola_riscaldamento(temperatura, occupazione, orario):
    if not occupazione:
        if temperatura >= 25:
            return "Spegni riscaldamento"
        return "Nessuna azione"
    
    # Stanza occupata
    if temperatura < 19:
        return "Accendi riscaldamento"
    elif temperatura >= 28:
        return "Spegni riscaldamento"

    # Regola temporale: di sera/notte accendi se < 21 °C
    if orario == "Notte" and temperatura < 21:
        return "Accendi riscaldamento"

    return "Nessuna azione"


# REGOLA TAPPARELLE
def regola_tapparelle(illuminazione, occupazione, orario):
    if not occupazione:
        if illuminazione >= 800:
            return "Abbassa tapparelle"
        return "Nessuna azione"
    
    # Stanza occupata
    if illuminazione > 800:
        return "Abbassa tapparelle"
    elif illuminazione < 200:
        return "Alza tapparelle"

    # Regola temporale: di notte abbassare sempre
    if orario == "Notte":
        return "Abbassa tapparelle"

    return "Nessuna azione"


# REGOLA CLIMATIZZATORE 
def regola_climatizzatore(temperatura, occupazione, orario):
    if not occupazione:
        if temperatura <= 21:
            return "Spegni climatizzatore"
        return "Nessuna azione"
    
    # Stanza occupata
    if temperatura > 28:
        return "Accendi climatizzatore"
    elif 21 <= temperatura <= 28:
        return "Spegni climatizzatore"

    # Regola combinata: se notte e temperatura > 26, spegnere per risparmio
    if orario == "Notte" and temperatura > 26:
        return "Spegni climatizzatore"

    return "Nessuna azione"


# REGOLE COMBINATE
def regola_combinata(temperatura, illuminazione, occupazione, orario):
    # Caso: stanza occupata, buia e fredda
    if occupazione and illuminazione < 100 and temperatura < 18:
        return ["Accendi luce", "Accendi riscaldamento"]

    # Caso: stanza molto calda e molto luminosa → raffrescare e abbassare tapparelle
    if occupazione and temperatura > 29 and illuminazione > 700:
        return ["Accendi climatizzatore", "Abbassa tapparelle"]

    # Caso: notte, stanza occupata ma luminosa → abbassare tapparelle + spegnere luce
    if orario == "Notte" and occupazione and illuminazione > 500:
        return ["Abbassa tapparelle", "Spegni luce"]

    return []


# FUNZIONE DI AGGREGAZIONE 
def azioni_da_regole(illuminazione, temperatura, occupazione, orario="Giorno"):
    azioni = [
        regola_luce(illuminazione, occupazione, orario),
        regola_riscaldamento(temperatura, occupazione, orario),
        regola_tapparelle(illuminazione, occupazione, orario),
        regola_climatizzatore(temperatura, occupazione, orario),
    ]

    # Regole combinate
    azioni.extend(regola_combinata(temperatura, illuminazione, occupazione, orario))

    # Filtra azioni "Nessuna azione"
    return [a for a in azioni if a != "Nessuna azione"]
