import os
import warnings
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from joblib import dump

# ---------------- CONFIGURAZIONE MODELLI ----------------
MODELLI = {
    "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=5000, solver='lbfgs'),
}

# SVM sarà ottimizzata separatamente
SVM_PARAMS = {'C':[0.1, 1, 10], 'gamma':[0.01, 0.1, 1]}

# ---------------- FUNZIONI UTILI ----------------
def carica_dataset(percorso):
    if not os.path.exists(percorso):
        print(f"ERRORE: file dataset '{percorso}' non trovato.")
        return None
    df = pd.read_csv(percorso)
    print(f"\nDataset '{os.path.basename(percorso)}' caricato: {len(df)} righe.")
    return df

def prepara_dati(df, features, target):
    X = df[features]
    y = df[target]
    return X, y

def valuta_modello_cv(model, X, y, cv=5):
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        scores = cross_val_score(model, X, y, cv=skf, scoring='f1')
    return scores

def salva_modello(model, base_dir, nome_modello, dataset_label):
    os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)
    percorso_specifico = os.path.join(base_dir, "data", f"{dataset_label}_{nome_modello}.joblib")
    dump(model, percorso_specifico)
    print(f"Modello salvato in: {os.path.relpath(percorso_specifico)}")

# ---------------- MAIN ----------------
def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dataset_files = {
        "Base": os.path.join(base_dir, "data", "SmartHome_base.csv"),
        "KB": os.path.join(base_dir, "data", "SmartHome_KB_enhanced.csv")
    }

    # Feature base
    features_base = [
        'ora_giorno', 'temperatura', 'umidita', 'illuminazione',
        'consumo_luce_kW', 'consumo_riscaldamento_kW',
        'consumo_climatizzatore_kW', 'consumo_tapparella_kW'
    ]

    # Feature aggiuntive derivanti dalla KB
    features_kb_extra = [
        'is_StanzaDaRiscaldare', 'is_StanzaDaClimatizzare',
        'is_StanzaAltaOccupazione', 'is_StanzaLuminosissima',
        'is_StanzaBuiaNotteOccupata', 'is_StanzaDaClimatizzareELuminare'
    ]

    target = 'occupazione'
    risultati_comparativi = {}

    for label, file in dataset_files.items():
        df = carica_dataset(file)
        if df is None:
            continue

        # Feature dataset
        features = features_base + features_kb_extra if label=="KB" else features_base
        X, y = prepara_dati(df, features, target)
        if len(np.unique(y)) < 2:
            print(f"ERRORE: il target 'occupazione' nel dataset '{label}' ha una sola classe.")
            continue

        # --- SCALING per SVM ---
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        print(f"Valutazione modelli sul dataset '{label}':")
        risultati_dataset = {}

        # RandomForest e LogisticRegression
        for nome_modello, modello in MODELLI.items():
            scores = valuta_modello_cv(modello, X, y)
            f1_mean = scores.mean()
            f1_std = scores.std()
            modello.fit(X, y)
            salva_modello(modello, base_dir, nome_modello, dataset_label=label)
            risultati_dataset[nome_modello] = (f1_mean, f1_std)
            print(f"▶ {nome_modello}: F1 = {f1_mean:.4f} ± {f1_std:.4f}")

        # --- SVM con GridSearch ---
        svm = SVC(probability=True, kernel='rbf', random_state=42)
        grid = GridSearchCV(svm, SVM_PARAMS, scoring='f1', cv=5)
        grid.fit(X_scaled, y)
        best_svm = grid.best_estimator_
        scores = cross_val_score(best_svm, X_scaled, y, cv=5, scoring='f1')
        f1_mean = scores.mean()
        f1_std = scores.std()
        salva_modello(best_svm, base_dir, "SVM", dataset_label=label)
        risultati_dataset["SVM"] = (f1_mean, f1_std)
        print(f"▶ SVM (GridSearch): F1 = {f1_mean:.4f} ± {f1_std:.4f}")

        risultati_comparativi[label] = risultati_dataset

    # --- Tabella comparativa finale ---
    print("\n=== Tabella comparativa modelli ===")
    rows = []
    for modello in list(MODELLI.keys()) + ["SVM"]:
        f1_base_mean, f1_base_std = risultati_comparativi.get("Base", {}).get(modello, (np.nan, np.nan))
        f1_kb_mean, f1_kb_std = risultati_comparativi.get("KB", {}).get(modello, (np.nan, np.nan))
        differenza = f1_kb_mean - f1_base_mean if not np.isnan(f1_base_mean) and not np.isnan(f1_kb_mean) else np.nan
        rows.append({
            "Modello": modello,
            "F1 Base": f"{f1_base_mean:.2f} ± {f1_base_std:.2f}",
            "F1 KB": f"{f1_kb_mean:.2f} ± {f1_kb_std:.2f}",
            "Delta KB-Base": f"{differenza:.2f}" if not np.isnan(differenza) else "N/A"
        })

    df_tabella = pd.DataFrame(rows)
    print(df_tabella.to_string(index=False))

if __name__ == "__main__":
    main()
