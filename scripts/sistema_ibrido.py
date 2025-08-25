import uuid
from regole import regola_luce, regola_riscaldamento, regola_tapparelle, regola_climatizzatore
from owlready2 import get_ontology
import os
from joblib import load
import pandas as pd


def chiedi_input_float(prompt, default=None, min_val=None, max_val=None):
    while True:
        val = input(f"{prompt}" + (f" [{default}]" if default is not None else "") + ": ").strip()
        if val == "" and default is not None:
            val = default
        try:
            valf = float(val)
            if min_val is not None and valf < min_val:
                print(f"Valore troppo basso! Minimo {min_val}.")
                continue
            if max_val is not None and valf > max_val:
                print(f"Valore troppo alto! Massimo {max_val}.")
                continue
            return valf
        except ValueError:
            print("Input non valido. Inserisci un numero.")

def chiedi_input_temperatura(prompt, default=None):
    return chiedi_input_float(prompt, default, min_val=5, max_val=38)

def chiedi_input_umidita(prompt, default=None):
    return chiedi_input_float(prompt, default, min_val=0, max_val=100)

def chiedi_input_consumo(prompt, default=None):
    return chiedi_input_float(prompt, default, min_val=0, max_val=5)

def chiedi_input_luce(prompt, default=None):
    return chiedi_input_float(prompt, default, min_val=0, max_val=1000)

def chiedi_input_occupancy(prompt, default=None):
    while True:
        val = input(f"{prompt}" + (f" [{default}]" if default is not None else "") + ": ").strip()
        if val == "" and default is not None:
            val = default
        try:
            val = int(val)
            if val in [0, 1]:
                return val
            print("Inserisci 0 o 1.")
        except ValueError:
            print("Input non valido. Inserisci 0 o 1.")

def chiedi_input_strategy(prompt, default="1"):
    while True:
        val = input(f"{prompt} [{default}]: ").strip() or default
        if val in ["1", "2", "3"]:
            return int(val)
        print("Seleziona 1, 2 o 3.")

def scegli_da_lista_obbligatorio(prompt, opzioni, default=1):
    """Mostra le opzioni e restituisce un indice valido (0-based)"""
    while True:
        for i, op in enumerate(opzioni, 1):
            print(f" {i}. {op}")
        val = input(f"{prompt} [{default}]: ").strip() or str(default)
        try:
            idx = int(val)
            if 1 <= idx <= len(opzioni):
                return idx - 1
            print(f"Errore: inserisci un numero tra 1 e {len(opzioni)}")
        except ValueError:
            print("Errore: devi inserire un numero!")

def carica_modello(base_dir):
    # supporta sia modello.joblib (generico) sia modello_rf.joblib (compatibilità)
    candidate_paths = [
        os.path.join(base_dir, "data", "modello.joblib"),
        os.path.join(base_dir, "data", "modello_rf.joblib"),
    ]
    for model_path in candidate_paths:
        if os.path.exists(model_path):
            try:
                model = load(model_path)
                return model, model_path
            except Exception:
                pass
    return None, candidate_paths[0]

def scegli_o_crea_istanza_stanza(onto):
    # Raccogli tutte le classi che ereditano da Stanza (escluse le superclassi)
    classi_stanza = [cls for cls in onto.classes() if issubclass(cls, onto.Stanza) and cls is not onto.Stanza]
    if not classi_stanza:
        print("Nessuna classe Stanza trovata nell'ontologia.")
        return None

    # Selezione classe stanza
    while True:
        print("\nClassi di stanze disponibili:")
        for i, c in enumerate(classi_stanza, 1):
            print(f" {i}. {c.name}")
        scelta = input(f"Seleziona tipo stanza (1-{len(classi_stanza)}) [1]: ").strip()
        if scelta == "":
            idx = 0
        else:
            try:
                idx = int(scelta) - 1
            except ValueError:
                print("Input non valido. Inserisci un numero.")
                continue
        if 0 <= idx < len(classi_stanza):
            cls_scelt = classi_stanza[idx]
            break
        else:
            print(f"Seleziona un numero tra 1 e {len(classi_stanza)}.")

    # Elenco istanze esistenti
    istanze = list(cls_scelt.instances())
    if istanze:
        while True:
            print("\nIstanze esistenti della stanza:")
            for i, inst in enumerate(istanze, 1):
                print(f" {i}. {inst.name}")
            print(f" {len(istanze)+1}. + Crea nuova istanza")
            scelta = input(f"Scegli istanza (1-{len(istanze)+1}) [1]: ").strip()
            if scelta == "":
                s = 1
            else:
                try:
                    s = int(scelta)
                except ValueError:
                    print("Input non valido. Inserisci un numero.")
                    continue
            if 1 <= s <= len(istanze):
                return istanze[s-1]
            elif s == len(istanze)+1:
                nome = input("Nome nuova istanza (es. Soggiorno_Nuovo): ").strip() or f"{cls_scelt.name}_{uuid.uuid4().hex[:6]}"
                return cls_scelt(nome)
            else:
                print(f"Seleziona un numero tra 1 e {len(istanze)+1}.")
    else:
        nome = input(f"Nessuna istanza trovata. Nome nuova istanza per {cls_scelt.name}: ").strip() or f"{cls_scelt.name}_{uuid.uuid4().hex[:6]}"
        return cls_scelt(nome)

def acquisisci_misure_per_stanza():
    temp = chiedi_input_temperatura("Temperatura (°C)", 22.0)
    light = chiedi_input_luce("Luce (lux 0-1000)", 200.0)
    humidity = chiedi_input_umidita("Umidità (%) 0-100", 40.0)
    use_kw = chiedi_input_consumo("Consumo istantaneo 'use [kW]' (0-5)", 0.0)
    occupancy = chiedi_input_occupancy("Occupazione (0=assente, 1=presente)", 0)
    return temp, light, humidity, use_kw, occupancy


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")
    update_path = os.path.join(base_dir, "ontology", "smarthome_updated.owl")
    
    if not os.path.exists(ont_path):
        print(f" ATTENZIONE: File ontologia popolata mancante: '{os.path.relpath(ont_path)}'. Esegui il punto 3.")
        return

    model, model_path = carica_modello(base_dir)
    if model is None:
        print(f"ATTENZIONE: Modello ML non trovato (cercato in {os.path.relpath(model_path)}). Proseguirò solo con regole.")

    print("Sistema ibrido: regole + ontologia + (opzionale) ML")

    if os.path.exists(update_path):
        risposta = input(f" Il file aggiornato '{os.path.relpath(update_path)}' esiste già. Sovrascriverlo? (s/n): ").strip().lower()
        if risposta != 's':
            print("Operazione annullata dall'utente.")
            return

    onto = get_ontology(ont_path).load()

    # Numero di stanze da aggiornare in questo run
    while True:
        try:
            n = int(input("Quante stanze vuoi aggiornare in questo run? [1]: ") or "1")
            if 1 <= n <= 10:
                break
            print("Inserisci un numero tra 1 e 10.")
        except ValueError:
            print("Input non valido. Inserisci un numero intero.")

    azioni_totali = []

    with onto:
        for _ in range(n):
            stanza = scegli_o_crea_istanza_stanza(onto)
            if stanza is None:
                continue

            temp, light, humidity, use_kw, occupancy = acquisisci_misure_per_stanza()

            threshold = 0.7
            occupancy_ml = None
            ml_conf = None

            if light < 100 and use_kw < 1:
                final_occupancy = 0
            else:
                if model is not None:
                    features_df = pd.DataFrame([[temp, humidity, light, use_kw]],
                                                columns=['temperature', 'humidity', 'visibility', 'use [kW]'])
                    try:
                        proba = model.predict_proba(features_df)[0]
                        ml_conf = float(proba[1])
                        occupancy_ml = int(model.predict(features_df)[0])
                        print(f"Predizione ML: occupancy={occupancy_ml} conf={ml_conf:.3f}")
                    except Exception as e:
                        print(f"Errore durante la previsione ML: {e}")
                        occupancy_ml = None

            scelta_fusione = chiedi_input_strategy("Strategia fusione: 1=OR  2=solo ML (se conf>=0.7)  3=solo manuale")

            final_occupancy = occupancy
            if scelta_fusione == "1":
                if occupancy_ml is not None:
                    final_occupancy = int(bool(occupancy) or bool(occupancy_ml))
            elif scelta_fusione == "2":
                if occupancy_ml is not None and ml_conf is not None and ml_conf >= threshold:
                    final_occupancy = occupancy_ml

            print(f"Occupancy finale usata per regole: {final_occupancy}")

            stato_attuale = onto.StatoAmbientale(f"Stato_{stanza.name}_{uuid.uuid4().hex[:8]}")
            stato_attuale.haTemperatura = temp
            stato_attuale.haIlluminazione = light
            stato_attuale.haOccupazione = bool(final_occupancy)
            stanza.haStato.append(stato_attuale)

            # Applica regole
            azioni = []
            azione_luce = regola_luce(light, final_occupancy)
            azione_riscaldamento = regola_riscaldamento(temp, final_occupancy)
            azione_tapparelle = regola_tapparelle(light, final_occupancy)
            azione_climatizzatore = regola_climatizzatore(temp, final_occupancy)

            if azione_luce == "Accendi luce":
                azioni.append(onto.AccendiLuce(f"AccendiLuce_{uuid.uuid4().hex[:8]}"))
            elif azione_luce == "Spegni luce":
                azioni.append(onto.SpegniLuce(f"SpegniLuce_{uuid.uuid4().hex[:8]}"))

            if azione_riscaldamento == "Accendi riscaldamento":
                azioni.append(onto.AccendiRiscaldamento(f"AccendiRiscaldamento_{uuid.uuid4().hex[:8]}"))
            elif azione_riscaldamento == "Spegni riscaldamento":
                azioni.append(onto.SpegniRiscaldamento(f"SpegniRiscaldamento_{uuid.uuid4().hex[:8]}"))

            if azione_tapparelle == "Abbassa tapparelle":
                azioni.append(onto.AbbassaTapparelle(f"AbbassaTapparelle_{uuid.uuid4().hex[:8]}"))
            elif azione_tapparelle == "Alza tapparelle":
                azioni.append(onto.AlzaTapparelle(f"AlzaTapparelle_{uuid.uuid4().hex[:8]}"))

            if azione_climatizzatore == "Accendi climatizzatore":
                azioni.append(onto.AccendiClimatizzatore(f"AccendiClimatizzatore_{uuid.uuid4().hex[:8]}"))
            elif azione_climatizzatore == "Spegni climatizzatore":
                azioni.append(onto.SpegniClimatizzatore(f"SpegniClimatizzatore_{uuid.uuid4().hex[:8]}"))

            if azioni:
                print("\n AZIONI SUGGERITE:")
                for az in azioni:
                    print(f" - {az.__class__.__name__}")
                    stato_attuale.suggerisceAzione.append(az)
            else:
                print("Nessuna azione da aggiungere alla KB.")

            azioni_totali.extend(azioni)

    os.makedirs(os.path.dirname(update_path), exist_ok=True)
    onto.save(file=update_path, format="rdfxml")
    print(f"Ontologia aggiornata salvata come '{os.path.relpath(update_path)}'.")

    # piccolo riepilogo multi-stanza
    if azioni_totali:
        from collections import Counter
        cnt = Counter([a.__class__.__name__ for a in azioni_totali])
        print("\nRIEPILOGO AZIONI (tutte le stanze in questo run):")
        for k, v in cnt.items():
            print(f" {k}: {v}")


if __name__ == "__main__":
    main()
