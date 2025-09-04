# analisi_KBS_reasoning.py - Analisi SmartHome KBS basata su reasoning + regole.py
import os
import pandas as pd
from owlready2 import *
from regole import azioni_da_regole  # <-- importa le tue regole già scritte

def main():
    print("Analisi SmartHome KBS basata sul reasoning...")

    # --- Percorsi ---
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")
    csv_path = os.path.join(base_dir, "data", "SmartHome.csv")
    report_path = os.path.join(base_dir, "data", "report_KBS_reasoning.csv")

    if not os.path.exists(ont_path):
        raise FileNotFoundError(f"Ontologia non trovata: {ont_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset non trovato: {csv_path}")

    # --- Carica ontologia ---
    onto = get_ontology(ont_path).load()
    print(f"✅ Ontologia caricata: {len(list(onto.classes()))} classi, {len(list(onto.individuals()))} individui")

    # --- Esegui reasoning ---
    print("\n🔹 Esecuzione reasoner...")
    with onto:
        sync_reasoner(infer_property_values=True)
    print("✅ Reasoner completato")

    # --- Carica dataset (opzionale) ---
    df = pd.read_csv(csv_path)
    print(f"✅ Dataset caricato: {len(df)} righe")

    # ----------------- Stanze inferite dal reasoner -----------------
    stanze_cat = {
        "StanzaDaRiscaldare": list(onto.StanzaDaRiscaldare.instances()),
        "StanzaDaSpegnereLuce": list(onto.StanzaDaSpegnereLuce.instances()),
        "StanzaEnergiaAlta": list(onto.StanzaEnergiaAlta.instances()),
        "StanzaLuminosissima": list(onto.StanzaLuminosissima.instances())
    }

    for cat, stanze in stanze_cat.items():
        print(f"\n--- {cat} ---")
        if stanze:
            for s in stanze:
                stato = s.haStato[0] if s.haStato else None
                temp = stato.haTemperatura if stato else "N/A"
                lux = stato.haIlluminazione if stato else "N/A"
                occ = stato.haOccupazione if stato else "N/A"
                print(f"- {s.name}: temp={temp}, lux={lux}, occupazione={occ}")
        else:
            print("Nessuna stanza inferita.")

    # ----------------- Azioni suggerite usando regole.py -----------------
    print("\n--- Azioni suggerite per le stanze ---")
    azioni_per_stanza = {}
    for s in onto.Stanza.instances():
        stato = s.haStato[0] if s.haStato else None
        if stato:
            acts = azioni_da_regole(stato.haIlluminazione, stato.haTemperatura, stato.haOccupazione)
            if acts:
                azioni_per_stanza[s.name] = acts
                print(f"- {s.name}: {acts}")

    # --- Totale azioni per tipo ---
    azioni_totali = {}
    for acts in azioni_per_stanza.values():
        for a in acts:
            azioni_totali[a] = azioni_totali.get(a, 0) + 1

    print("\n--- Totale azioni generate per tipo ---")
    for az, count in azioni_totali.items():
        print(f"{az}: {count}")

    # --- Salvataggio report aggregato ---
    report_data = []
    for stanza, acts in azioni_per_stanza.items():
        for az in acts:
            report_data.append({"stanza": stanza, "azione": az})
    df_report = pd.DataFrame(report_data)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df_report.to_csv(report_path, index=False)
    print(f"\n✅ Report aggregato salvato in '{os.path.relpath(report_path)}'")
    print("\n✅ Analisi completata secondo linee guida del progetto.")

if __name__ == "__main__":
    main()
