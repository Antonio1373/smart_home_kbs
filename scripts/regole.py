# ---------- REGOLA LUCE ----------
def regola_luce(illuminazione, occupazione):
    if not occupazione:
        if illuminazione >= 300:
            return "Spegni luce"
        return "Nessuna azione"
    
    # Stanza occupata
    if illuminazione < 100:
        return "Accendi luce"
    elif illuminazione > 800:
        return "Spegni luce"
    return "Nessuna azione"


# ---------- REGOLA RISCALDAMENTO ----------
def regola_riscaldamento(temperatura, occupazione):
    if not occupazione:
        if temperatura >= 25:
            return "Spegni riscaldamento"
        return "Nessuna azione"
    
    # Stanza occupata
    if temperatura < 19:
        return "Accendi riscaldamento"
    elif temperatura >= 28:
        return "Spegni riscaldamento"
    return "Nessuna azione"


# ---------- REGOLA TAPPARELLE ----------
def regola_tapparelle(illuminazione, occupazione):
    if not occupazione:
        if illuminazione >= 800:
            return "Abbassa tapparelle"
        return "Nessuna azione"
    
    # Stanza occupata
    if illuminazione > 800:
        return "Abbassa tapparelle"
    elif illuminazione < 200:
        return "Alza tapparelle"
    return "Nessuna azione"


# ---------- REGOLA CLIMATIZZATORE ----------
def regola_climatizzatore(temperatura, occupazione):
    if not occupazione:
        if temperatura <= 21:
            return "Spegni climatizzatore"
        return "Nessuna azione"
    
    # Stanza occupata
    if temperatura > 28:
        return "Accendi climatizzatore"
    elif 21 <= temperatura <= 28:
        return "Spegni climatizzatore"
    return "Nessuna azione"


# ---------- FUNZIONE DI AGGREGAZIONE ----------
def azioni_da_regole(illuminazione, temperatura, occupazione):
    azioni = [
        regola_luce(illuminazione, occupazione),
        regola_riscaldamento(temperatura, occupazione),
        regola_tapparelle(illuminazione, occupazione),
        regola_climatizzatore(temperatura, occupazione)
    ]
    # Filtra azioni "Nessuna azione"
    return [a for a in azioni if a != "Nessuna azione"]
