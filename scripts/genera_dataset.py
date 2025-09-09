import os
import random
import pandas as pd
from owlready2 import get_ontology, sync_reasoner

ONTO_FILE = "ontology/smarthome_popolata.owl"
OUTPUT_DIR = "data"
RIGHE_PER_STANZA = 1  # Numero di campioni per stanza

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, ONTO_FILE)
    output_dir = os.path.join(base_dir, OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(ont_path):
        print(f"ERRORE : File ontologia non trovato: {os.path.relpath(ont_path)}")
        return

    print(f"Caricamento ontologia da: {os.path.relpath(ont_path)}")

    onto = get_ontology(ont_path).load()
    print("Esecuzione reasoner per calcolare le classi inferite...")
    with onto:
        sync_reasoner(infer_property_values=True, debug=0)
    print("Reasoner completato.")
    
    dataset_base = []
    dataset_enhanced = []
    idx = 0

    for casa in onto.Casa.instances():
        for stanza in casa.haStanza:
            for stato in stanza.haStato:
                for _ in range(RIGHE_PER_STANZA):
                    # Occupazione
                    occupazione = int(getattr(stato, "haOccupazione", 0))
                    ora_giorno = random.randint(0, 23)  # Orario simulato

                    # Valori grezzi dalla KB
                    temperatura = getattr(stato, "haTemperatura", 22)
                    illuminazione = getattr(stato, "haIlluminazione", 400)
                    umidita = getattr(stato, "haUmidita", 45)

                    # Consumi dei dispositivi (default 0 se assente)
                    consumo_luce = round(max([disp.haConsumo for disp in stanza.haDispositivo if isinstance(disp, onto.Luce)], default=0), 2)
                    consumo_riscaldamento = round(max([disp.haConsumo for disp in stanza.haDispositivo if isinstance(disp, onto.Riscaldamento)], default=0), 2)
                    consumo_climatizzatore = round(max([disp.haConsumo for disp in stanza.haDispositivo if isinstance(disp, onto.Climatizzatore)], default=0), 2)
                    consumo_tapparella = round(max([disp.haConsumo for disp in stanza.haDispositivo if isinstance(disp, onto.Tapparella)], default=0), 2)

                    # Record base 
                    record_base = {
                        "id": idx,
                        "casa": casa.name,
                        "stanza": stanza.name,
                        "ora_giorno": ora_giorno,
                        "temperatura": temperatura,
                        "umidita": umidita,
                        "illuminazione": illuminazione,
                        "occupazione": occupazione,
                        "consumo_luce_kW": consumo_luce,
                        "consumo_riscaldamento_kW": consumo_riscaldamento,
                        "consumo_climatizzatore_kW": consumo_climatizzatore,
                        "consumo_tapparella_kW": consumo_tapparella,
                    }
                    dataset_base.append(record_base)

                    # Record con inferenze KB avanzate
                    inferenze = {
                        "is_StanzaFredda": int(stanza in onto.StanzaFredda.instances()),
                        "is_StanzaCalda": int(stanza in onto.StanzaCalda.instances()),
                        "is_StanzaBuia": int(stanza in onto.StanzaBuia.instances()),
                        "is_StanzaLuminosissima": int(stanza in onto.StanzaLuminosissima.instances()),
                        "is_StanzaDaRiscaldare": int(stanza in onto.StanzaDaRiscaldare.instances()),
                        "is_StanzaDaClimatizzare": int(stanza in onto.StanzaDaClimatizzare.instances()),
                        "is_StanzaBuiaNotteOccupata": int(stanza in onto.StanzaBuiaNotteOccupata.instances()),
                        "is_StanzaDaClimatizzareELuminare": int(stanza in onto.StanzaDaClimatizzareELuminare.instances()),
                        "is_StanzaDispendiosa": int(stanza in onto.StanzaDispendiosa.instances())
                    }
                    record_enhanced = {**record_base, **inferenze}
                    dataset_enhanced.append(record_enhanced)

                    idx += 1

    df_base = pd.DataFrame(dataset_base)
    df_enhanced = pd.DataFrame(dataset_enhanced)

    path_base = os.path.join(output_dir, "SmartHome_base.csv")
    path_enhanced = os.path.join(output_dir, "SmartHome_KB_enhanced.csv")

    df_base.to_csv(path_base, index=False)
    df_enhanced.to_csv(path_enhanced, index=False)

    print(f"Dataset base generato in '{os.path.relpath(path_base)}' ({len(df_base)} righe).")
    print(f"Dataset KB-enhanced generato in '{os.path.relpath(path_enhanced)}' ({len(df_enhanced)} righe).")

if __name__ == "__main__":
    main()
