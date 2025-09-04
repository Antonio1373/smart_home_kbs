import os
import pandas as pd
from owlready2 import get_ontology

# ---------------- CONFIGURAZIONE ----------------
ONTO_FILE = "ontology/smarthome_popolata.owl"
OUTPUT_FILE = "data/SmartHome.csv"
RIGHE_PER_STANZA = 1  # Numero di campioni per stanza
# ------------------------------------------------

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, ONTO_FILE)
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(ont_path):
        print(f"ERRORE : File ontologia non trovato: {os.path.relpath(ont_path)}")
        return

    print(f"Caricamento ontologia da: {os.path.relpath(ont_path)}")

    onto = get_ontology(ont_path).load()
    dataset = []
    idx = 0

    for casa in onto.Casa.instances():
        for stanza in casa.haStanza:
            for stato in stanza.haStato:
                for _ in range(RIGHE_PER_STANZA):
                    occupazione = 1 if len(stanza.haPresenza) > 0 else 0

                    # Valori già presenti nella KB
                    temperatura = getattr(stato, "haTemperatura", 22)
                    illuminazione = getattr(stato, "haIlluminazione", 400)
                    umidita = getattr(stato, "haUmidita", 45)

                    # Consumi basati sull’occupazione
                    consumo_luce = round(max(disp.haConsumo for disp in stanza.haDispositivo if disp.__class__.__name__=="Luce"),2)
                    consumo_riscaldamento = round(max(disp.haConsumo for disp in stanza.haDispositivo if disp.__class__.__name__=="Riscaldamento"),2)
                    consumo_climatizzatore = round(max(disp.haConsumo for disp in stanza.haDispositivo if disp.__class__.__name__=="Climatizzatore"),2)
                    consumo_tapparella = round(max(disp.haConsumo for disp in stanza.haDispositivo if disp.__class__.__name__=="Tapparella"),2)

                    dataset.append({
                        "id": idx,
                        "casa": casa.name,
                        "stanza": stanza.name,
                        "temperatura": temperatura,
                        "umidita": umidita,
                        "illuminazione": illuminazione,
                        "occupazione": occupazione,
                        "consumo_luce_kW": consumo_luce,
                        "consumo_riscaldamento_kW": consumo_riscaldamento,
                        "consumo_climatizzatore_kW": consumo_climatizzatore,
                        "consumo_tapparella_kW": consumo_tapparella
                    })
                    idx += 1

    df = pd.DataFrame(dataset)
    df.to_csv(output_path, index=False)
    print(f"Dataset generato in '{os.path.relpath(output_path)}' ({len(df)} righe).")

if __name__ == "__main__":
    main()
