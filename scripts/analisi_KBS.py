import os
import pandas as pd
from owlready2 import *
from regole import azioni_da_regole

def main():
    print("Analisi SmartHome KBS basata sul reasoning...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")
    csv_path = os.path.join(base_dir, "data", "SmartHome_base.csv")
    report_path = os.path.join(base_dir, "data", "report_KBS_reasoning.csv")

    if not os.path.exists(ont_path):
        print (f"ERRORE : Ontologia non trovata: {os.path.relpath(ont_path)}.")
    if not os.path.exists(csv_path):
        print(f"ERRORE : Dataset non trovato: {os.path.relpath(csv_path)}.")
        return

    onto = get_ontology(ont_path).load()
    print(f"Ontologia caricata: {len(list(onto.classes()))} classi, {len(list(onto.individuals()))} individui.")

    print("\nEsecuzione reasoner...")
    start = time.time()
    with onto:
        sync_reasoner(infer_property_values=True, debug=0)
    end = time.time()
    print(f"Tempo di reasoning: {end - start:.2f} secondi.")
    print("Reasoner completato.")

    df = pd.read_csv(csv_path)
    print(f"Dataset caricato: {len(df)} righe.")

    # Stanze inferite dal reasoner
    stanze_cat = {
        "StanzaDaRiscaldare": list(onto.StanzaDaRiscaldare.instances()),
        "StanzaEnergiaAlta": list(onto.StanzaEnergiaAlta.instances()),
        "StanzaLuminosissima": list(onto.StanzaLuminosissima.instances()),
        "StanzaBuiaNotteOccupata": list(onto.StanzaBuiaNotteOccupata.instances()),
    }

    for cat, stanze in stanze_cat.items():
        print(f"\n--- {cat} ---")
        if stanze:
            for s in stanze:
                stato = s.haStato[0] if s.haStato else None
                print(f"- {s.name}.")
        else:
            print("Nessuna stanza inferita.")

    # Azioni suggerite usando regole.py
    print("\nAzioni suggerite per le stanze nel report_CSV.")
    azioni_per_stanza = {}
    for s in onto.Stanza.instances():
        stato = s.haStato[0] if s.haStato else None
        if stato:
            acts = azioni_da_regole(stato.haIlluminazione, stato.haTemperatura, stato.haOccupazione, stato.haOrario)
            if acts:
                azioni_per_stanza[s.name] = acts

    # Totale azioni per tipo
    azioni_totali = {}
    for acts in azioni_per_stanza.values():
        for a in acts:
            azioni_totali[a] = azioni_totali.get(a, 0) + 1

    print("\nTotale azioni generate per stanza...")
    for az, count in azioni_totali.items():
        print(f"{az}: {count}")

    report_data = []
    for stanza, acts in azioni_per_stanza.items():
        for az in acts:
            report_data.append({"stanza": stanza, "azione": az})
    df_report = pd.DataFrame(report_data)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    df_report.to_csv(report_path, index=False)
    print(f"\nReport aggregato salvato in '{os.path.relpath(report_path)}'.")

if __name__ == "__main__":
    main()
