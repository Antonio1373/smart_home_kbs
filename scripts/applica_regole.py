"""
applica_regole.py - Applicazione delle regole SmartHome
Obiettivo: usare le regole Python per generare azioni automatiche
           sulle istanze della KB SmartHome popolata.
"""

from owlready2 import *
import os
from regole import azioni_da_regole

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kb_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")

    if not os.path.exists(kb_path):
        print(f"Errore: file ontologia non trovato: '{kb_path}'")
        return

    # Carica KB
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

    # Per ogni casa e stanza
    for casa in onto.Casa.instances():
        for stanza in casa.haStanza:
            # Applica regole solo se esiste almeno uno stato ambientale
            if not stanza.haStato:
                continue
            stato = stanza.haStato[0]  # Consideriamo lo stato corrente

            temp = stato.haTemperatura
            light = stato.haIlluminazione
            occupazione = stato.haOccupazione

            # Ottieni azioni suggerite dalle regole Python
            azioni = azioni_da_regole(light, temp, occupazione)

            # Crea istanze Azione nella KB e collega ai dispositivi
            for az in azioni:
                azione_nome = f"{az}_{stanza.name}"
                AzClasse = azione_to_classe.get(az.replace(" ", ""))
                if AzClasse is None:
                    # crea sottoclasse dinamica generica se non esiste
                    AzClasse = type(f"Azione_{az}_{stanza.name}", (onto.Azione,), {})

                azione_istanza = AzClasse(azione_nome)

                # Collega azione ai dispositivi pertinenti
                if "Luce" in az:
                    for disp in [d for d in stanza.haDispositivo if isinstance(d, onto.Luce)]:
                        azione_istanza.controllaDispositivo.append(disp)
                elif "Riscaldamento" in az:
                    for disp in [d for d in stanza.haDispositivo if isinstance(d, onto.Riscaldamento)]:
                        azione_istanza.controllaDispositivo.append(disp)
                elif "Climatizzatore" in az:
                    for disp in [d for d in stanza.haDispositivo if isinstance(d, onto.Climatizzatore)]:
                        azione_istanza.controllaDispositivo.append(disp)
                elif "Tapparella" in az:
                    for disp in [d for d in stanza.haDispositivo if isinstance(d, onto.Tapparella)]:
                        azione_istanza.controllaDispositivo.append(disp)

                # Collega azione allo stato ambientale come suggerimento
                stato.suggerisceAzione.append(azione_istanza)

    # Salva KB aggiornata
    output_path = os.path.join(base_dir, "ontology", "smarthome_con_azioni.owl")
    onto.save(file=output_path, format="rdfxml")
    print(f"✅ Azioni applicate e KB salvata in '{os.path.relpath(output_path)}'")

if __name__ == "__main__":
    main()
