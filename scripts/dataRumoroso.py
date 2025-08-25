import pandas as pd   
import numpy as np    
import os             

def aggiungi_rumore(df, errore_occupancy=0.25, random_state=42):
    """
    Aggiunge rumore ai dati simulando errori di misura e sensori imperfetti.
    - df: DataFrame originale
    - errore_occupancy: probabilità di invertire il valore di 'occupancy'
    - random_state: seme per la riproducibilità
    """
    
    np.random.seed(random_state)  
    df_noisy = df.copy()  

    # ---- TEMPERATURA ----
    if 'temperature' in df_noisy.columns:
        df_noisy['temperature'] = np.random.uniform(10, 35, size=len(df_noisy))

    # ---- VISIBILITÀ / LUCE ----
    if 'visibility' in df_noisy.columns:
        df_noisy['visibility'] = np.random.uniform(0, 1000, size=len(df_noisy))

    # ---- UMIDITÀ ----
    if 'humidity' in df_noisy.columns:
        df_noisy['humidity'] = np.random.uniform(0, 100, size=len(df_noisy))

    # ---- CONSUMO ENERGETICO ----
    if 'use [kW]' in df_noisy.columns:
        df_noisy['use [kW]'] = np.random.uniform(0.0, 5.0, size=len(df_noisy))

    # ---- OCCUPAZIONE ----
    if 'occupancy' in df_noisy.columns:
        flip_mask = np.random.rand(len(df_noisy)) < errore_occupancy
        df_noisy.loc[flip_mask, 'occupancy'] = 1 - df_noisy.loc[flip_mask, 'occupancy']
        df_noisy['occupancy'] = df_noisy['occupancy'].astype(int)

    return df_noisy 

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(base_dir, "data", "HomeC_with_occupancy.csv")  
    output_path = os.path.join(base_dir, "data", "HomeC_noisy.csv")          

    if not os.path.exists(input_path):
        print(f"ATTENZIONE: File non trovato: {os.path.relpath(input_path)}")
        print("Esegui prima il punto 1 per generarlo.")
        return
    
    if os.path.exists(output_path):
        risposta = input(f" Il file '{os.path.relpath(output_path)}' esiste già. Vuoi rigenerarlo e sovrascriverlo? (s/n): ").strip().lower()
        if risposta != 's':
            print(" Operazione annullata. Il file esistente non è stato modificato.")
            return

    df = pd.read_csv(input_path, low_memory=False)

    df_noisy = aggiungi_rumore(df, errore_occupancy=0.3)

    df_noisy.to_csv(output_path, index=False)
    print(f" Dataset rumoroso salvato in: {os.path.relpath(output_path)}")

if __name__ == "__main__":
    main()