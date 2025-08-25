from owlready2 import *
import pandas as pd
import uuid
import os
from regole import regola_luce, regola_riscaldamento, regola_tapparelle, regola_climatizzatore

def chiedi_dataset():
    while True:
        risposta = input("Vuoi usare il dataset originale (1) o con rumore (2)? ").strip()
        if risposta == "1":
            return "HomeC_with_occupancy.csv"
        elif risposta == "2":
            return "HomeC_noisy.csv"
        else:
            print("Inserisci 1 o 2.")

def apply_rules_to_row(row, onto, stanza):
    statoAttuale = onto.StatoAmbientale(f"Stato_Soggiorno_{uuid.uuid4()}")
    statoAttuale.haTemperatura = float(row["temperature"])
    statoAttuale.haIlluminazione = float(row["visibility"])
    statoAttuale.haOccupazione = bool(row["occupancy"])
    stanza.haStato.append(statoAttuale)


    azioni = []

    azione_luce = regola_luce(float(row["visibility"]), bool(row["occupancy"]))
    azione_riscaldamento = regola_riscaldamento(float(row["temperature"]), bool(row["occupancy"]))
    azione_tapparelle = regola_tapparelle(float(row["visibility"]), bool(row["occupancy"]))
    azione_climatizzatore = regola_climatizzatore(float(row["temperature"]), bool(row["occupancy"]))

    if azione_luce == "Accendi luce":
        azioni.append(onto.AccendiLuce(f"AccendiLuce_{uuid.uuid4()}"))
    elif azione_luce == "Spegni luce":
        azioni.append(onto.SpegniLuce(f"SpegniLuce_{uuid.uuid4()}"))

    if azione_riscaldamento == "Accendi riscaldamento":
        azioni.append(onto.AccendiRiscaldamento(f"AccendiRiscaldamento_{uuid.uuid4()}"))
    elif azione_riscaldamento == "Spegni riscaldamento":
        azioni.append(onto.SpegniRiscaldamento(f"SpegniRiscaldamento_{uuid.uuid4()}"))

    if azione_tapparelle == "Abbassa tapparelle":
        azioni.append(onto.AbbassaTapparelle(f"AbbassaTapparelle_{uuid.uuid4()}"))
    elif azione_tapparelle == "Alza tapparelle":
        azioni.append(onto.AlzaTapparelle(f"AlzaTapparelle_{uuid.uuid4()}"))
        
    if azione_climatizzatore == "Accendi climatizzatore":
        azioni.append(onto.AccendiClimatizzatore(f"AccendiClimatizzatore_{uuid.uuid4()}"))
    elif azione_climatizzatore == "Spegni climatizzatore":
        azioni.append(onto.SpegniClimatizzatore(f"SpegniClimatizzatore_{uuid.uuid4()}"))

    for az in azioni:
        statoAttuale.suggerisceAzione.append(az)

    return azioni

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome.owl")
    output_path = os.path.join(base_dir, "ontology", "smarthome_rules_applied.owl")

    dataset_filename = chiedi_dataset()
    file_path = os.path.join(base_dir, "data", dataset_filename)

    if not os.path.exists(ont_path):
        print(f" File ontologia mancante: '{os.path.relpath(ont_path)}'.")
        print(" Assicurati di aver eseguito il punto 2.")
        return

    # Controlla se il csv esiste
    if not os.path.exists(file_path):
        print(f" File dati mancante: '{os.path.relpath(file_path)}'.")
        if "noisy" in dataset_filename:
            print(" Assicurati di aver eseguito il punto 9 per creare il dataset rumoroso.")
        else:
            print(" Assicurati di aver eseguito il punto 1 per generare il dataset originale.")
        return

    if os.path.exists(output_path):
        risposta = input(f"ATTENZIONE: Il file '{os.path.relpath(output_path)}' esiste già. Vuoi sovrascriverlo? (s/n): ").strip().lower()
        if risposta != 's':
            print("Operazione annullata dall'utente.")
            return

    onto = get_ontology(ont_path).load()
    df = pd.read_csv(file_path, low_memory=False).head(100)  # puoi cambiare

    soggiorno = onto.Soggiorno("Soggiorno1")

    azioni_contate = {
        "AccendiLuce": 0,
        "SpegniLuce": 0,
        "AccendiRiscaldamento": 0,
        "SpegniRiscaldamento": 0,
        "AbbassaTapparelle": 0,
        "AlzaTapparelle": 0,
        "AccendiClimatizzatore": 0,
        "SpegniClimatizzatore": 0
    }

    for _, row in df.iterrows():
        azioni = apply_rules_to_row(row, onto, soggiorno)
        for az in azioni:
            nome_azione = az.name.split('_')[0]
            if nome_azione in azioni_contate:
                azioni_contate[nome_azione] += 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"Ontologia aggiornata con regole applicate salvata come '{os.path.relpath(output_path)}'.")

    print("\nStatistiche azioni applicate:")
    for az, count in azioni_contate.items():
        print(f"{az}: {count}")

if __name__ == "__main__":
    main()
