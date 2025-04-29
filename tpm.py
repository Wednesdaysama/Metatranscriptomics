'''
Requirement: seal.sh output rpkm files sealrpkm_LY-*.txt
This script calculates TPM from seal.sh output file sealrpkm_LY-*.txt.
'''

import os
import pandas as pd

work_dir = os.path.dirname(os.path.abspath(__file__))
#work_dir = r"D:\OneDrive - University of Calgary\Exp_Sediment\Experiments\Molecular_biology\2025_Apr\seal"

all_results = []

for filename in os.listdir(work_dir):
    if filename.startswith("sealrpkm_LY-") and filename.endswith(".txt"):
        filepath = os.path.join(work_dir, filename)

        df = pd.read_csv(filepath, sep='\t', skiprows=4)
        required_columns = ['#Name', 'Length', 'Reads']
        if not all(col in df.columns for col in required_columns):
            continue

        # RPK：(Reads / Length) * 1000
        df['RPK'] = (df['Reads'] / df['Length']) * 1000
        # per_million_scaling_factor
        per_million_scaling_factor = df['RPK'].sum() / 1e6
        # TPM
        df['TPM'] = df['RPK'] / per_million_scaling_factor

        result_df = df[['#Name', 'TPM']].copy()
        sample_name = os.path.splitext(filename)[0]
        result_df = result_df.rename(columns={'TPM': sample_name})
        all_results.append(result_df)


if all_results:
    tpm_all = all_results[0]
    for df in all_results[1:]:
        tpm_all = pd.merge(tpm_all, df, on='#Name', how='outer')

    tpm_all = tpm_all.fillna(0)
    tpm_all_path = os.path.join(work_dir, "tpm_all.xlsx")
    tpm_all.to_excel(tpm_all_path, index=False)

print("Done.")
