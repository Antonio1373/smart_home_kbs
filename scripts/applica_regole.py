from owlready2 import *
import os
from regole import azioni_da_regole

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kb_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")

    if not os.path.exists(kb_path):
        print(f"ERRORE : file ontologia non trovato: '{os.path.relpath(kb_path)}'")
        return

    onto = get_ontology(kb_path).load()

    azione_to_classe = {
        "AccendiLuce": onto.AccendiLuce,
        "SpegniLuce": onto.SpegniLuce,
        "AccendiRiscaldamento": onto.AccendiRiscaldamento,
        "SpegniRiscaldamento": onto.SpegniRiscaldamento,
        "AccendiClimatizzatore": onto.AccendiClimatizzatore,
        "SpegniClimatizzatore": onto.SpegniClimatizzatore,
        "AlzaTapparelle": onto.AlzaTapparelle,
        "AbbassaTapparelle": onto.AbbassaTapparelle
    }

    print("\nApplicazione regole Python e confronto con inferenze reasoner...\n")

    # Eseguo reasoner per aggiornare le classi derivabili
    with onto:
        try:
            sync_reasoner(infer_property_values=True, debug=0)
            print("Reasoner completato.")
        except Exception as e:
            print(f"ATTENZIONE: Reasoner non completato correttamente: {e}")

    for casa in onto.Casa.instances():
        for stanza in casa.haStanza:
            if not stanza.haStato:
                continue
            stato = stanza.haStato[0]

            temp = getattr(stato, "haTemperatura", None)
            light = getattr(stato, "haIlluminazione", None)
            occupazione = getattr(stato, "haOccupazione", None)

            if temp is None or light is None or occupazione is None:
                continue

            # --- Azioni dalle regole Python ---
            azioni_python = azioni_da_regole(light, temp, occupazione)

            # --- Azioni già presenti in KB ---
            azioni_kb_before = [a.__class__.__name__ for a in stato.suggerisceAzione]

            print(f"\nStanza: {stanza.name}")
            print(f" - Azioni Python: {azioni_python}")
            print(f" - Azioni KB: {azioni_kb_before}")

            # Pulizia dei nomi per confronto
            azioni_kb_clean = [a.replace("Azione_", "").split("_")[0].replace(" ", "").lower() for a in azioni_kb_before]
            azioni_python_clean = [a.replace(" ", "").lower() for a in azioni_python]

            differenze = set(azioni_python_clean) ^ set(azioni_kb_clean)
            if differenze:
                print(f"Differenze tra Python e KB: {differenze}")
            else:
                print("Azioni coerenti tra Python e KB.")

            # aggiungo azioni KB mancanti direttamente
            for az in azioni_python:
                az_clean = az.replace(" ", "")
                if az_clean.lower() not in azioni_kb_clean:
                    AzClasse = azione_to_classe.get(az_clean, type(f"Azione_{az}_{stanza.name}", (onto.Azione,), {}))
                    azione_istanza = AzClasse(f"{az}_{stanza.name}")
                    # Collegamento ai dispositivi
                    if "Luce" in az:
                        azione_istanza.controllaDispositivo.extend([d for d in stanza.haDispositivo if isinstance(d, onto.Luce)])
                    elif "Riscaldamento" in az:
                        azione_istanza.controllaDispositivo.extend([d for d in stanza.haDispositivo if isinstance(d, onto.Riscaldamento)])
                    elif "Climatizzatore" in az:
                        azione_istanza.controllaDispositivo.extend([d for d in stanza.haDispositivo if isinstance(d, onto.Climatizzatore)])
                    elif "Tapparella" in az:
                        azione_istanza.controllaDispositivo.extend([d for d in stanza.haDispositivo if isinstance(d, onto.Tapparella)])
                    stato.suggerisceAzione.append(azione_istanza)

    output_path = os.path.join(base_dir, "ontology", "smarthome_con_azioni.owl")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"\nAzioni applicate e KB salvata in '{os.path.relpath(output_path)}'.")

if __name__ == "__main__":
    main()
