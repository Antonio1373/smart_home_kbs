# genera_istanze.py - Versione aggiornata per ontologia SmartHome con reasoner intelligente
from owlready2 import *
import uuid
import os
import random

# ----------------- PARAMETRI DI PROGETTO -----------------
NUM_CASE = 50                   # Numero di case simulate
STANZE_PER_CASA = ["Soggiorno", "Cucina", "Camera", "Bagno"]
PERSONE_PER_CASA = 3            # Numero medio di persone per casa

# Intervalli di consumo realistici per i dispositivi (kW)
CONSUMO_DISPOSITIVI = {
    "Luce": (0.05, 0.2),
    "Riscaldamento": (0.5, 2.0),
    "Climatizzatore": (0.5, 2.0),
    "Tapparella": (0.05, 0.1),
}

# Parametri per stato ambientale
TEMPERATURA_MEDIA = 22
TEMPERATURA_STD = 2
ILLUMINAZIONE_MEDIA = 400
ILLUMINAZIONE_STD = 150
UMIDITA_MEDIA = 45
UMIDITA_STD = 10

# Probabilità di valori estremi intenzionali (per test reasoner)
PROB_VALORI_ESTREMI = 0.35

# ----------------- FUNZIONE PRINCIPALE -----------------
def main():
    print("Generazione istanze SmartHome avanzata...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome.owl")
    output_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")

    if not os.path.exists(ont_path):
        print(f"Errore: file ontologia non trovato: '{os.path.relpath(ont_path)}'")
        return

    # Carica ontologia esistente
    onto = get_ontology(ont_path).load()

    case = []
    with onto:
        # ----------------- CREAZIONE CASE E STANZE -----------------
        for c in range(1, NUM_CASE + 1):
            casa = onto.Casa(f"Casa{c}")
            case.append(casa)
            
            stanze = []
            for st_nome in STANZE_PER_CASA:
                st_class = getattr(onto, st_nome)
                stanza = st_class(f"{st_nome}_C{c}")
                stanze.append(stanza)
            casa.haStanza.extend(stanze)

        # ----------------- CREAZIONE DISPOSITIVI E SENSORI -----------------
        for casa in case:
            for stanza in casa.haStanza:
                # Sensori
                sensori = [onto.Sensore(f"{nome}Sensor_{stanza.name}") 
                           for nome in ["Temp", "Light", "Occupancy"]]
                stanza.haSensore.extend(sensori)

                # Dispositivi
                dispositivi = [
                    onto.Luce(f"Luce_{stanza.name}"),
                    onto.Riscaldamento(f"Riscaldamento_{stanza.name}"),
                    onto.Climatizzatore(f"Climatizzatore_{stanza.name}"),
                    onto.Tapparella(f"Tapparella_{stanza.name}")
                ]
                stanza.haDispositivo.extend(dispositivi)

                # Consumo realistico dei dispositivi
                for disp in stanza.haDispositivo:
                    if isinstance(disp, onto.Luce):
                        low, high = CONSUMO_DISPOSITIVI["Luce"]
                    elif isinstance(disp, onto.Riscaldamento):
                        low, high = CONSUMO_DISPOSITIVI["Riscaldamento"]
                    elif isinstance(disp, onto.Climatizzatore):
                        low, high = CONSUMO_DISPOSITIVI["Climatizzatore"]
                    elif isinstance(disp, onto.Tapparella):
                        low, high = CONSUMO_DISPOSITIVI["Tapparella"]
                    disp.haConsumo = round(random.uniform(low, high), 2)

        # ----------------- CREAZIONE PERSONE -----------------
        for idx, casa in enumerate(case, start=1):
            for p in range(1, PERSONE_PER_CASA + 1):
                persona = onto.Persona(f"Persona_C{idx}_{p}")
                stanza = random.choice(casa.haStanza)
                stanza.haPresenza.append(persona)

        # ----------------- STATO AMBIENTALE -----------------
        for casa in case:
            for stanza in casa.haStanza:
                stato = onto.StatoAmbientale(f"Stato_{stanza.name}_{uuid.uuid4().hex[:6]}")
        
                # Generazione valori realistici
                stato.haTemperatura = round(random.gauss(TEMPERATURA_MEDIA, TEMPERATURA_STD), 1)
                stato.haIlluminazione = round(random.gauss(ILLUMINAZIONE_MEDIA, ILLUMINAZIONE_STD), 1)
                stato.haUmidita = round(random.gauss(UMIDITA_MEDIA, UMIDITA_STD), 1)
                stato.haOccupazione = bool(stanza.haPresenza)

                # Introduci casi estremi intenzionali
                if random.random() < PROB_VALORI_ESTREMI:
                    ext_temp = [17.0, 29.0]
                    stato.haTemperatura = ext_temp[(c + len(stanza.name)) % 2]

                    ext_light = [50.0, 850.0]
                    stato.haIlluminazione = ext_light[(c + len(stanza.name)) % 2]

                stanza.haStato.append(stato)
        
    # ----------------- ESECUZIONE REASONER -----------------
    print("\n🔹 Esecuzione reasoner per inferenze sulle stanze...")
    try:
        sync_reasoner_pellet(infer_property_values=True)  # Pellete più affidabile con valori numerici
        print("✅ Reasoner completato: stanze fredde, calde, buie e luminosissime inferite.")
    except Exception as e:
        print(f"⚠ Errore nel reasoner: {e}")

    # ----------------- STAMPA CLASSI DERIVATE -----------------
    for cls in [onto.StanzaCalda, onto.StanzaFredda, onto.StanzaBuia, onto.StanzaLuminosissima,
            onto.StanzaDaRiscaldare, onto.StanzaDaSpegnereLuce, onto.StanzaEnergiaAlta]:
        instances = list(cls.instances())
        print(f"\nClassi dedotte '{cls.__name__}': {len(instances)} istanze")
        for s in instances:
            print(f"- {s.name}")



    # ----------------- SALVATAGGIO ONTOLOGIA -----------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"✅ Ontologia popolata salvata in '{os.path.relpath(output_path)}'")
    print(f"Totale case generate: {NUM_CASE}, stanze: {NUM_CASE * len(STANZE_PER_CASA)}, persone: {NUM_CASE * PERSONE_PER_CASA}")

# ----------------- ENTRY POINT -----------------
if __name__ == "__main__":
    main()
