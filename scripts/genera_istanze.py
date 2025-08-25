from owlready2 import *     
import pandas as pd         
import os                   

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ontology_path = os.path.join(base_dir, "ontology", "smarthome.owl")
csv_path = os.path.join(base_dir, "data", "HomeC_with_occupancy.csv")
output_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")

if not os.path.exists(ontology_path) or not os.path.exists(csv_path):
    print(" File necessari mancanti. Verifica la presenza di:")
    print(f"- Ontologia: {'PRESENTE' if os.path.exists(ontology_path) else 'ASSENTE'}")
    print(f"- CSV: {'PRESENTE' if os.path.exists(csv_path) else 'ASSENTE'}")
    exit()

if os.path.exists(output_path):
    risposta = input(f"ATTENZIONE: Il file '{os.path.relpath(output_path)}' esiste già. Sovrascrivere? (s/n): ").strip().lower()
    if risposta != "s":
        print(" Operazione annullata.")
        exit()

onto = get_ontology(ontology_path).load()

# Legge il file CSV con i dati, rimuove righe che non hanno temperatura, visibilità o occupazione e prende solo le prime 100 righe per velocità.
df = pd.read_csv(csv_path, low_memory=False).dropna(subset=['temperature','visibility','occupancy']).head(100)

soggiorno1 = onto.Soggiorno("Soggiorno_Principale")
soggiorno2 = onto.Soggiorno("Soggiorno_Secondario")
camera1 = onto.Camera("Camera_Principale")
cucina1 = onto.Cucina("Cucina_Principale")
stanze = [soggiorno1, soggiorno2, camera1, cucina1]

# Definisce un dizionario per associare le colonne del CSV ai tipi di dispositivi e alla stanza
mappa_dispositivi = {
    "Living room [kW]": onto.Luce,
    "Furnace 1 [kW]": onto.Riscaldamento,
    "Furnace 2 [kW]": onto.Riscaldamento, 
    "AC [kW]": onto.Climatizzatore,
    "Sun blind [kW]": onto.Tapparella,
}
with onto:
    for i, row in df.iterrows():
        temp = float(row.get("temperature", float('nan')))
        light = float(row.get("visibility", float('nan')))
        occ = bool(int(row.get("occupancy", 0)))

        # round-robin fra le stanze
        stanza = stanze[i % len(stanze)]

        stato = onto.StatoAmbientale(f"Stato_{stanza.name}_{i}")
        stato.haTemperatura = float(temp)
        stato.haVisibilita = float(light)
        stato.haOccupazione = int(occ)
        stanza.haStato.append(stato)

        for col, classe_dispositivo in mappa_dispositivi.items():
            if col in row and pd.notna(row[col]):
                try:
                    consumo = float(row[col])
                except Exception:
                    consumo = None
                # crea un dispositivo per stanza/indice per evitare conflitti nomi
                disp = classe_dispositivo(f"{classe_dispositivo.name}_{stanza.name}_{i}")
                if consumo is not None:
                    disp.haConsumo = consumo
                stanza.haDispositivo.append(disp)

onto.save(file=output_path, format="rdfxml")
print(f" Ontologia popolata e salvata in '{os.path.relpath(output_path)}'")


