'''
Requirement: seal.sh output rpkm files sealrpkm_LY-*.txt
'''

import os
import pandas as pd

work_dir = os.path.dirname(os.path.abspath(__file__))
#work_dir = r"D:\OneDrive - University of Calgary\Exp_Sediment\Experiments\Molecular_biology\2025_Apr\seal"

for filename in os.listdir(work_dir):
    if filename.startswith("sealrpkm_LY-") and filename.endswith(".txt"):
        filepath = os.path.join(work_dir, filename)
        df = pd.read_csv(filepath, sep='\t', skiprows=4)
        required_columns = ['#Name', 'Length', 'Reads']
        if not all(col in df.columns for col in required_columns):
            continue

        df['RPK'] = (df['Reads'] / df['Length']) * 1000

        per_million_scaling_factor = df['RPK'].sum() / 1e6

        df['TPM'] = df['RPK'] / per_million_scaling_factor

        result_df = df[['#Name', 'TPM']].copy()

        output_filename = filename.replace("sealrpkm_LY-", "tpm_")
        output_path = os.path.join(work_dir, output_filename)
        result_df.to_csv(output_path, sep='\t', index=False)
        print(f"Results has been saved to {output_path}")

        del df, result_df

print("\nDone")
