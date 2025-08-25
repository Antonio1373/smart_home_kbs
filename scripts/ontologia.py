from owlready2 import *
import os

def main():
    print(" Creazione ontologia SmartHome...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_path = os.path.join(base_dir, "ontology", "smarthome.owl")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        relative_path = os.path.relpath(output_path, os.getcwd())
        risposta = input(f" ATTENZIONE: Il file '{relative_path}' esiste già. Sovrascrivere? (s/n): ").strip().lower()
        if risposta != 's':
            print(" Operazione annullata.")
            return

    # Crea una nuova ontologia partendo da zero
    onto = get_ontology("http://example.org/ontology/smarthome.owl")

    with onto:
        # === CLASSI PRINCIPALI ===
        class Stanza(Thing): pass
        class Soggiorno(Stanza): pass
        class Camera(Stanza): pass  
        class Cucina(Stanza): pass  

        class Azione(Thing): pass
        # Sottoclassi di Azione
        class AccendiLuce(Azione): pass
        class SpegniLuce(Azione): pass
        class AccendiRiscaldamento(Azione): pass
        class SpegniRiscaldamento(Azione): pass
        class AlzaTapparelle(Azione): pass
        class AbbassaTapparelle(Azione): pass
        class AccendiClimatizzatore(Azione): pass
        class SpegniClimatizzatore(Azione): pass

        class Dispositivo(Thing): pass
        # Tipi di dispositivi
        class Tapparella(Dispositivo): pass
        class Luce(Dispositivo): pass
        class Riscaldamento(Dispositivo): pass
        class Climatizzatore(Dispositivo): pass
        class Forno(Dispositivo): pass
        class Frigorifero(Dispositivo): pass

        # Proprietà dei dispositivi
        class haConsumo(Dispositivo >> float, DataProperty): pass  # Consumo energetico

        class Persona(Thing): pass
        class StatoAmbientale(Thing): pass  # Rappresenta le condizioni della stanza

        # === RELAZIONI ===
        class haDispositivo(Stanza >> Dispositivo): pass
        class haStato(Stanza >> StatoAmbientale): pass
        class haPresenza(Stanza >> Persona): pass

        # Stato ambientale → dati numerici
        class haTemperatura(StatoAmbientale >> float, DataProperty): pass
        class haIlluminazione(StatoAmbientale >> float, DataProperty): pass
        class haOccupazione(StatoAmbientale >> bool, DataProperty): pass

        # Relazione tra stato ambientale e azione suggerita
        class suggerisceAzione(StatoAmbientale >> Azione): pass

        # Relazioni azione → dispositivo controllato
        class controllaDispositivo(Azione >> Dispositivo): pass
        class controllaTapparella(Azione >> Tapparella): pass
        class controllaLuce(Azione >> Luce): pass
        class controllaRiscaldamento(Azione >> Riscaldamento): pass
        class controllaClimatizzatore(Azione >> Climatizzatore): pass

        # DATA PROPERTY (con range/functional)
        class haConsumo(Dispositivo >> float, DataProperty, FunctionalProperty): pass
        class haTemperatura(Dispositivo >> float, DataProperty, FunctionalProperty): pass
        class haIlluminazione(Dispositivo >> float, DataProperty, FunctionalProperty): pass
        class haOccupazione(StatoAmbientale >> bool, DataProperty, FunctionalProperty): pass

    onto.save(file=output_path, format="rdfxml")
    relative_path = os.path.relpath(output_path, os.getcwd())
    print(f" Ontologia salvata in '{relative_path}'.")

if __name__ == "__main__":
    main()
