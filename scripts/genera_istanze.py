import os
import uuid
import random
from owlready2 import *
from regole import azioni_da_regole

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
TEMPERATURE_RANGE = [(15, 18), (19, 22), (23, 27), (28, 32)]
LUCE_RANGE = [(0, 100), (101, 300), (301, 600), (601, 900)]
UMIDITA_RANGE = [(20, 35), (36, 55), (56, 70)]

PROB_VALORI_ESTREMI = 0.25
PROB_STATO_PROLUNGATO = 0.3  # Probabilità di durata > 30 minuti

def genera_valore_con_range(ranges):
    r = random.choice(ranges)
    return round(random.uniform(r[0], r[1]), 1)

def main():
    print("Generazione istanze SmartHome avanzata...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ont_path = os.path.join(base_dir, "ontology", "smarthome.owl")
    output_path = os.path.join(base_dir, "ontology", "smarthome_popolata.owl")

    if not os.path.exists(ont_path):
        print(f"ERRORE: file ontologia non trovato: '{os.path.relpath(ont_path)}'")
        return

    onto = get_ontology(ont_path).load()
    case = []

    # Mappatura azione -> classe ontologia
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

        # ----------------- CREAZIONE DISPOSITIVI E PERSONE -----------------
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

                # Consumi realistici
                for disp in stanza.haDispositivo:
                    tipo = disp.__class__.__name__
                    low, high = CONSUMO_DISPOSITIVI.get(tipo, (0.1, 1.0))
                    disp.haConsumo = round(random.uniform(low, high), 2)

            # Persone
            for p in range(1, PERSONE_PER_CASA + 1):
                persona = onto.Persona(f"Persona_C{c}_{p}")
                stanza = random.choice(casa.haStanza)
                stanza.haPresenza.append(persona)

        # ----------------- STATO AMBIENTALE E AZIONI -----------------
        for casa in case:
            for stanza in casa.haStanza:
                stato = onto.StatoAmbientale(f"Stato_{stanza.name}_{uuid.uuid4().hex[:6]}")

                # Orario casuale
                orario_cls = random.choice([onto.Giorno, onto.Notte, onto.FasciaEnergeticaAlta, onto.FasciaEnergeticaBassa])
                orario_istanza = orario_cls(f"Orario_{orario_cls.__name__}_{stanza.name}_{uuid.uuid4().hex[:4]}")
                stanza.haOrario.append(orario_istanza)

                # Valori ambiente
                stato.haTemperatura = genera_valore_con_range(TEMPERATURE_RANGE)
                stato.haIlluminazione = genera_valore_con_range(LUCE_RANGE)
                stato.haUmidita = genera_valore_con_range(UMIDITA_RANGE)
                stato.haOccupazione = bool(stanza.haPresenza)

                # Durata dello stato per regole temporali
                stato.haDurata = round(random.uniform(10, 60), 1) if random.random() < PROB_STATO_PROLUNGATO else round(random.uniform(1, 29), 1)

                # Valori estremi occasionali
                if random.random() < PROB_VALORI_ESTREMI:
                    stato.haTemperatura = random.choice([15.0, 32.0])
                    stato.haIlluminazione = random.choice([0.0, 900.0])

                stanza.haStato.append(stato)

                # --- Azioni suggerite ---
                azioni_python = azioni_da_regole(
                    stato.haIlluminazione,
                    stato.haTemperatura,
                    stato.haOccupazione,
                    orario_istanza
                )

                for az in azioni_python:
                    azione_nome = f"{az}_{stanza.name}"
                    AzClasse = azione_to_classe.get(az.replace(" ", ""))
                    if AzClasse is None:
                        AzClasse = type(f"Azione_{az}_{stanza.name}", (onto.Azione,), {})
                    azione_istanza = AzClasse(azione_nome)

                    # Collega al dispositivo corretto
                    for disp in stanza.haDispositivo:
                        if "Luce" in az and isinstance(disp, onto.Luce):
                            azione_istanza.controllaDispositivo.append(disp)
                        elif "Riscaldamento" in az and isinstance(disp, onto.Riscaldamento):
                            azione_istanza.controllaDispositivo.append(disp)
                        elif "Climatizzatore" in az and isinstance(disp, onto.Climatizzatore):
                            azione_istanza.controllaDispositivo.append(disp)
                        elif "Tapparella" in az and isinstance(disp, onto.Tapparella):
                            azione_istanza.controllaDispositivo.append(disp)

                    stato.suggerisceAzione.append(azione_istanza)

        # ----------------- ESECUZIONE REASONER -----------------
        print("\nEsecuzione reasoner per inferenze sulle stanze...")
        try:
            sync_reasoner_pellet(infer_property_values=True, debug=0)
            print("Reasoner completato: inferenze eseguite su stanze e orari.")
        except Exception as e:
            print(f"ATTENZIONE: Errore nel reasoner: {e}")

    # ----------------- SALVATAGGIO ONTOLOGIA -----------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    onto.save(file=output_path, format="rdfxml")
    print(f"Ontologia popolata salvata in '{os.path.relpath(output_path)}'.")
    print(f"Totale case generate: {NUM_CASE}, stanze: {NUM_CASE * len(STANZE_PER_CASA)}, persone: {NUM_CASE * PERSONE_PER_CASA}.")

if __name__ == "__main__":
    main()
