# Financial Security System - Support Layer

This repository implements a **Support Layer** for a financial security system, featuring three advanced AI components: Generative AI (GANs), Federated Learning (FL), and Explainable AI (XAI).

## System Architecture

The system is designed to enhance fraud detection while preserving privacy and providing transparency.

### Components

#### 1. Generative AI (GANs) - The Data Layer
*   **Goal:** Generate realistic synthetic fraud data for adversarial training.
*   **Technique:** Conditional Tabular GAN (CTGAN).
*   **Script:** `research/data_generation/train_gan.py`
*   **Input:** `research/data/user_logins.csv` (Seed data)
*   **Output:** `research/data/synthetic_logins.csv`

#### 2. Federated Learning (FL) - The Training Layer
*   **Goal:** Train a global fraud detection model across multiple banks (clients) without sharing raw data.
*   **Technique:** Flower (`flwr`) framework with Ray backend for simulation.
*   **Model:** Autoencoder (Deep Learning for Anomaly Detection).
*   **Script:** `research/phase1/fl_simulation.py`
*   **Process:**
    1.  Data is partitioned into 3 subsets (simulating 3 banks).
    2.  Each client trains the Autoencoder locally.
    3.  Weights are aggregated to form a global model.
*   **Output:** `backend/ml_artifacts/model_autoencoder_federated.h5`

#### 3. Explainable AI (XAI) - The Validation Layer
*   **Goal:** Provide human-readable explanations for risk scores to support manual review.
*   **Technique:** SHAP (SHapley Additive exPlanations).
*   **Script:** `research/phase2/explainability.py`
*   **Process:**
    *   **Isolation Forest:** Uses `TreeExplainer` to show which features contributed to the anomaly score.
    *   **Autoencoder:** Uses `KernelExplainer` to explain the reconstruction error (loss).
*   **Output:** Visualization plots in `research/output/`:
    *   `shap_isolation_forest.png`
    *   `shap_autoencoder.png`

#### 4. Inference & Scoring - The Application Layer
*   **Goal:** Detect fraud in new transaction data using the trained global model.
*   **Script:** `research/phase1/predict.py`
*   **Input:** `research/data/user_logins.csv` (or any new transaction file).
*   **Process:**
    1.  Loads the trained Federated Autoencoder.
    2.  Preprocesses data (feature engineering).
    3.  Calculates Reconstruction Error (MSE) as the Risk Score.
    4.  Flags transactions exceeding the 95th percentile as potential fraud.
*   **Output:** `research/output/scored_transactions.csv` containing:
    *   Original transaction details.
    *   `risk_score`: The anomaly score.
    *   `predicted_fraud`: 1 if high risk, 0 otherwise.

## Project Structure

```
.
├── backend/
│   ├── ml_artifacts/       # Stores trained models (local & federated)
│   └── app/                # Application backend (if applicable)
├── research/
│   ├── data/               # Seed and synthetic data
│   ├── data_generation/    # GAN training scripts
│   │   └── train_gan.py
│   ├── phase1/             # Feature engineering, FL Training, & Inference
│   │   ├── feature_engine.py   # Shared preprocessing logic
│   │   ├── models.py           # Shared model definitions
│   │   ├── fl_simulation.py    # Federated Learning simulation
│   │   ├── predict.py          # Inference engine
│   │   └── ...
│   ├── phase2/             # Explainability
│   │   ├── explainability.py   # SHAP analysis script
│   │   └── ...
│   ├── output/             # Generated plots and report files
│   └── full_pipeline_demo.ipynb # End-to-end demo notebook
└── requirements.txt
```

## Setup & Usage

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Full Pipeline:**
    Open and run `research/full_pipeline_demo.ipynb` in Jupyter/Lab.

    *OR run manually via CLI:*

    ```bash
    # Step 1: Generate Data
    python research/data_generation/train_gan.py

    # Step 2: Run Federated Learning
    # Note: Requires PYTHONPATH to include repo root for Ray workers
    PYTHONPATH=. python research/phase1/fl_simulation.py

    # Step 3: Generate Explanations
    python research/phase2/explainability.py

    # Step 4: Run Inference (Scoring)
    python research/phase1/predict.py
    ```

## Technologies
*   **CTGAN:** Synthetic data generation.
*   **Flower (flwr):** Federated Learning framework.
*   **TensorFlow/Keras:** Deep Learning models.
*   **SHAP:** Model explainability.
*   **Ray:** Distributed processing for simulation.
