import os
import pandas as pd
from pandas import ExcelWriter

species = 'RECH01'

os.chdir(r"D:\OneDrive - University of Calgary\Exp_Sediment\Experiments\Molecular_biology\2025_Apr\seal")
print('Reading tpm file...')
tpm_all = pd.read_excel("tpm_all.xlsx")[lambda df: df['#Name'].str.contains(species, na=False)]

print('Making categories...')
keyword_categories = {
    "Cell_Envelope": [r"porin", r"D-alanine-D-alanine", r"Alanine racemase", r"Mur", r"Mra", r"Peptidoglycan"],
    "PS": [r"Photosystem", r"Bacteriorhodopsin", r"psb", r"psa", "petA", "petB", "petC", "petD", "petE", "petF", "petH",
           "puhA","pufA", "pufB", "pufC", "pufM", "pufL"],
    "Citric_acid": [r"Pyruvate dehydrogenase", r"Pyruvate/2-oxoglutarate dehydrogenase", r'Citrate synthase',
                    r'Aconitase', r'Isocitrate dehydrogenase', r'2-Oxoglutarate dehydrogenas', r'Succinyl-CoA synthetase',
                    r'Succinate dehydrogenase', r'Fumarate hydratase', r'Malate', r'Isocitrate Lyase'],
    "Aminoacid_biosynthesis": [r"Alanine transaminase", r"aminotransferase", r'Asparagine', r'Glutamate', r'Glutamine',
                               r'Phosphoglycerate', r'Phosphoserine', r'Serine', r'Cysteine', r'Selenocysteine',
                               r'serine hydroxymethyltransferase', r'Threonine aldolase', r'Acetolactate', r'Ketol-acid',
                               r'Dihydroxyacid', r'transaminase', r'Isopropylmalate'],
    "Fatty_acid": [r"acyl-carrier-protein", r'Acetyl-CoA C-acyltransferase', r'Fatty'],
    "Glycolysis": [r"Hexokinase", r"glucokinase", r'Glucose-6-phosphate-isomerase', r'Phosphofructokinase',
                   r'Fructose-bisphosphate', r'Triosephosphate isomerase', r'Glyceraldehyde-3-phosphate', r'Phosphoglycerate',
                   r'Phosphopyruvate', r'Pyruvate'],
    'Carbon_fixation': [r'rbcL', r"rbcS"],
    "Heme": [r"Heme", r"ferrochelatase", r'Polyprenyltransferase', r'Uroporphyrinogen-III methylase'],
    "Inositol_phosphate_biosynthesis": [r"Phosphoinositide phospholipase", r"Inositol", r'Triosephosphate', r'Fructose-1,6-bisphosphate',
                                       r'Phospholipase', r'phosphocholine'],
    "Iron_storage": [r"Bacterioferritin", r"Ferritin"],
    "Motility": [r"Flagellar", r"flagellin", r'pilin', r'Pilus', r'PilM'],
    'Hydrogen_oxidation': [r'NiFe Hydrogenase', r"FeFe Hydrogenase", r'hox', r'ech Hydrogenase'],
    "Nitrogen_cycle": [r"Hydrazine", r"nitrate", r'Nitrite', r'Heme-copper', r'nitric', r'Nitrous',
                       r'Pmo', r'Smmo', r'hao', r'Nitrogenase', r'Urease', r'Urea', r'Cyanate lyase', r'Nitrile', r'nif', r'ure', r'urt', r'nap', r'octR', r'nrf'],
    "Respiration": [r"F0F1", r"Vacuolar", r'ATP synthase', r'NADH:ubiquinone', r'Cytochrome b6/f', r'Plastocyanin', r'Rieske Fe-S', r'quinol dependent', r'Heme/copper oxidase', r'Cyrochrome bd', r'Electron transport',
                    r'Proton/sodium translocating pyrophosphatase', r"ndh", r"nuo", r"nqr"],
    "Translation": [r"RNA polymerase", r"Ribosomal"],
    "Transport": [r"Twin arginine-target", r"translocase", r"Signal recognition", r"TolC", r"Periplasmic linker", r"HlyB",
                 r"Autotransported effector", r"secretion", r"Periplasmic", r"ExbB", r"TonB", r"ExbD", r'porter'],
    "Defense": [r"Defense", r"cas"],
    "Sulfur_cycle": [r"Adenylylsulfate", r"Sulfate", r"3-phosphoadenosine", r"phosphosulfate", r"Sulfite", r"Sulfur",
                     r"Thiosulfate", r"Sulfide", r"Thiosulfohydrolase", r"S-disulfanyl-L-cysteine", r"Thiosulfate",
                     r"Quinoprotein dehydrogenase", r'apr', r'dsr', r'sqr', r'fcc', r'sox'],
    "Secondary_metabolites": [r"Secondary"],
    "Other_elements": [r"Arsenite", r'Tetrachloroethene', r'PceA', r'Rdh', r'2-Haloacid', r"Decaheme", r'DMSO',
                       r'Selenate', r'chlorate', r'selenate'],
    "Toxin_antitoxin": [r"antitoxin"]
}

print('Saving resluts...')
results = {}
for category, keywords in keyword_categories.items():
    pattern = '|'.join(keywords)
    results[category] = tpm_all[tpm_all['#Name'].str.contains(pattern, case=False, na=False)]

output_excel = f"{species}_categories.xlsx"

with ExcelWriter(output_excel, engine='openpyxl') as writer:
    for category, df in results.items():
        if not df.empty:
            df.to_excel(writer, sheet_name=category, index=False)
        else:
            print(f"{category} skipped.")

print(f"Detailed data has been saved to {output_excel}！")

data = pd.DataFrame(columns=["Category"] + tpm_all.columns[1:].tolist())  
for category, keywords in keyword_categories.items():
    pattern = '|'.join(keywords)
    filtered_df = tpm_all[tpm_all['#Name'].str.contains(pattern, case=False, na=False)]
    row_data = {"Category": category}
    for col in tpm_all.columns[1:]:  
        row_data[col] = filtered_df[col].sum()

    data = pd.concat([data, pd.DataFrame([row_data])], ignore_index=True)

data.to_excel(f"{species}_category_sums.xlsx", index=False)
print(f"Summaries has been saved to {species}_category_sums.xlsx")
