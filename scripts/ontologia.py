from owlready2 import *
import os

def main():
    print("Creazione ontologia SmartHome avanzata...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(base_dir, "ontology")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "smarthome.owl")

    onto = get_ontology("http://example.org/ontology/smarthome.owl")

    with onto:
        # --- CLASSI BASE ---
        class Casa(Thing): pass
        class Stanza(Thing): pass
        class Persona(Thing): pass
        class Dispositivo(Thing): pass
        class Sensore(Thing): pass
        class StatoAmbientale(Thing): pass
        class Azione(Thing): pass

        # --- SOTTOCLASSI STANZA ---
        class Soggiorno(Stanza): pass
        class Camera(Stanza): pass
        class Cucina(Stanza): pass
        class Bagno(Stanza): pass

        # --- SOTTOCLASSI DISPOSITIVO ---
        class Luce(Dispositivo): pass
        class Riscaldamento(Dispositivo): pass
        class Climatizzatore(Dispositivo): pass
        class Tapparella(Dispositivo): pass
        class Frigorifero(Dispositivo): pass
        class Forno(Dispositivo): pass

        # --- SOTTOCLASSI AZIONE ---
        class AccendiLuce(Azione): pass
        class SpegniLuce(Azione): pass
        class AccendiRiscaldamento(Azione): pass
        class SpegniRiscaldamento(Azione): pass
        class AccendiClimatizzatore(Azione): pass
        class SpegniClimatizzatore(Azione): pass
        class AlzaTapparelle(Azione): pass
        class AbbassaTapparelle(Azione): pass

        # --- PROPRIETÀ DATI ---
        class haConsumo(Dispositivo >> float, DataProperty, FunctionalProperty): pass
        class haTemperatura(StatoAmbientale >> float, DataProperty, FunctionalProperty): pass
        class haIlluminazione(StatoAmbientale >> float, DataProperty, FunctionalProperty): pass
        class haOccupazione(StatoAmbientale >> bool, DataProperty, FunctionalProperty): pass
        class haUmidita(StatoAmbientale >> float, DataProperty, FunctionalProperty): pass
        class haOrario(StatoAmbientale >> str, DataProperty): pass

        # --- PROPRIETÀ OGGETTO ---
        class haStanza(Casa >> Stanza, ObjectProperty): pass
        class haDispositivo(Stanza >> Dispositivo, ObjectProperty): pass
        class haSensore(Stanza >> Sensore, ObjectProperty): pass
        class haStato(Stanza >> StatoAmbientale, ObjectProperty): pass
        class haPresenza(Stanza >> Persona, ObjectProperty): pass
        class suggerisceAzione(StatoAmbientale >> Azione, ObjectProperty): pass
        class controllaDispositivo(Azione >> Dispositivo, ObjectProperty): pass

        # --- CLASSI DERIVATE PER REASONING ---
        # Stato stanza
        class StanzaFredda(Stanza):
            equivalent_to = [Stanza & haStato.some(StatoAmbientale & (haTemperatura < 20.0))]
        class StanzaCalda(Stanza):
            equivalent_to = [Stanza & haStato.some(StatoAmbientale & (haTemperatura > 28.0))]
        class StanzaBuia(Stanza):
            equivalent_to = [Stanza & haStato.some(StatoAmbientale & (haIlluminazione < 200.0))]
        class StanzaLuminosissima(Stanza):
            equivalent_to = [Stanza & haStato.some(StatoAmbientale & (haIlluminazione > 800.0))]
        class StanzaDispendiosa(Stanza):
            equivalent_to = [Stanza & haDispositivo.some(Dispositivo & (haConsumo > 1.5))]

        # Profili stanza combinati
        class StanzaDaRiscaldare(Stanza):
            equivalent_to = [StanzaFredda & haPresenza.some(Persona)]

        class StanzaEnergiaAlta(Stanza):
            equivalent_to = [Stanza & haDispositivo.some(Luce | Riscaldamento | Climatizzatore)]

        class StanzaDaClimatizzare(Stanza):
            equivalent_to = [StanzaCalda & haPresenza.some(Persona)]

        class CasaAltaOccupazione(Casa):
            equivalent_to = [Casa & haStanza.some(Stanza & haPresenza.min(2, Persona))]

    onto.save(file=output_path, format="rdfxml")
    print(f"Ontologia salvata in '{os.path.relpath(output_path)}'.")

    # --- ESEGUI REASONER ---
    print("\nAvvio reasoner Pellet per inferenze...")
    sync_reasoner_pellet(infer_property_values=True, debug=0)
    print("Reasoning completato.")

    # --- Stampa stanze con profili dedotti ---
    for cls in [StanzaFredda, StanzaCalda, StanzaBuia, StanzaLuminosissima, StanzaDaRiscaldare, StanzaEnergiaAlta]:
        instances = list(cls.instances())
        if instances:
            print(f"\nClassi dedotte '{cls.__name__}':")
            for s in instances:
                print(f"- {s.name}")

if __name__ == "__main__":
    main()
