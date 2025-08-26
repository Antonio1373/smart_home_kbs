import os
import matplotlib.pyplot as plt
import json
import sys

input_path = os.path.join("data", "risultati.json")
output_dir = "results"
output_path = os.path.join(output_dir, "valutazione.png")

if not os.path.isfile(input_path):
    print(f"Errore: file di input non trovato: {input_path}")
    print("Consiglio: esegui il punto 6.")
    sys.exit(1)

if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

if os.path.isfile(output_path):
    risposta = input(f"Il file '{output_path}' esiste già. Vuoi sovrascriverlo? (s/n): ").strip().lower()
    if risposta != 's':
        print("Operazione annullata dall'utente.")
        sys.exit(0)

with open(input_path, "r") as f:
    dati = json.load(f)

methods = list(dati.keys())
f1_scores = [dati[m]["f1"] for m in methods]
std_devs = [dati[m]["std"] for m in methods]

plt.bar(methods, f1_scores, yerr=std_devs)
plt.title("F1 Score – confronto sistemi")
plt.ylabel("F1 Score")
plt.ylim(0, 1.1)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(output_path)
plt.show()