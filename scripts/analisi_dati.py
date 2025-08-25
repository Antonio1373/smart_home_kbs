import os
import pandas as pd

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    
    
    file_path = os.path.join(data_dir, "HomeC.csv")                  
    file_output = os.path.join(data_dir, "HomeC_with_occupancy.csv") 

    
    if not os.path.exists(file_path):
        print(f"ERRORE: file {file_path} non trovato.")
        print("Assicurati che il file sia presente nella cartella 'data'.")
        return

    
    if os.path.exists(file_output):
        relative_path = os.path.relpath(file_output, os.getcwd())
        print(f" Il file '{relative_path}' esiste già. Nessuna analisi necessaria.")
        return

    
    print("Caricamento dataset HomeC.csv...")
    df = pd.read_csv(file_path, low_memory=False)
    
    df.dropna(inplace=True)

    print("\n--- Anteprima dataset (prime 5 righe) ---")
    print(df.head())

    print("\n--- Colonne nel dataset ---")
    print(df.columns.tolist())

    print("\n--- Statistiche descrittive ---")
    print(df.describe())

    # Aggiunta della colonna "occupancy"
    # Regola empirica: occupato se consumo > 0.3 kW e temperatura > 15°C
    df['occupancy'] = ((df['use [kW]'] > 0.3) & (df['temperature'] > 15)).astype(int)

    df.to_csv(file_output, index=False)
    print(f"\nFile '{os.path.relpath(file_output)}' creato con colonna 'occupancy'.")

    print("Caricamento dataset HomeC_with_occupancy.csv...")
    df = pd.read_csv(file_output, low_memory=False)

    print("\n--- Anteprima dataset (prime 5 righe) ---")
    print(df.head())

    print("\n--- Colonne nel dataset ---")
    print(df.columns.tolist())

    print("\n--- Statistiche descrittive ---")
    print(df.describe())

if __name__ == "__main__":
    main()
