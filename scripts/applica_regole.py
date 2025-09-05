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

    # --- Mappatura azione -> classe KB ---
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

    for casa in onto.Casa.instances():
        for stanza in casa.haStanza:
            if not stanza.haStato:
                continue
            stato = stanza.haStato[0]

            temp = stato.haTemperatura
            light = stato.haIlluminazione
            occupazione = stato.haOccupazione

            # --- Azioni dalle regole Python ---
            azioni_python = azioni_da_regole(light, temp, occupazione)

            # --- Azioni già presenti in KB (prima) ---
            azioni_kb_before = [a.__class__.__name__ for a in stato.suggerisceAzione]

            # --- Log confronto prima ---
            print(f"\nStanza: {stanza.name}")
            print(f" - Azioni Python: {azioni_python}")
            print(f" - Azioni KB: {azioni_kb_before}")

            # confronto
            azioni_kb_clean = [a.replace("Azione_", "").split("_")[0].replace(" ", "").lower() for a in azioni_kb_before]
            azioni_python_clean = [a.replace(" ", "").lower() for a in azioni_python]

            differenze = set(azioni_python_clean) ^ set(azioni_kb_clean)
            if differenze:
                print(f"Differenze tra Python e KB: {differenze}")
            else:
                print("Azioni coerenti tra Python e KB.")


    output_path = os.path.join(base_dir, "ontology", "smarthome_con_azioni.owl")
    onto.save(file=output_path, format="rdfxml")
    print(f"\nAzioni applicate e KB salvata in '{os.path.relpath(output_path)}'.")

if __name__ == "__main__":
    main()
