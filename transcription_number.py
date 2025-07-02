import os
import pandas as pd
import re
import chardet


group_by = 'genus'

os.chdir(r"D:\OneDrive - University of Calgary\Exp_Sediment\Experiments\Molecular_biology\2025_Apr\seal")

print('Reading tpm_all.xlsx...')
tpm_all = pd.read_excel("tpm_all.xlsx")


accession_species_dict = {}
accession_phylum_dict = {}
accession_genus_dict = {}

for name in tpm_all['#Name']:
    name_str = str(name)
    accession = name_str[:13] if len(name_str) >= 13 else name_str
    accession_species_dict[accession] = None
    accession_phylum_dict[accession] = None
    accession_genus_dict[accession] = None


print('Reading bin_data.csv...')
with open("bin_data.csv", 'rb') as f:
    result = chardet.detect(f.read(10000))
bin_data = pd.read_csv("bin_data.csv", encoding=result['encoding'])

for _, row in bin_data.iterrows():
    assembly = row['Assembly']
    if assembly == "GCA_007760615":
        continue  

    if assembly in accession_species_dict:  
        gtdb_taxonomy = str(row['gtdb_taxonomy'])

        species_match = re.search(r's__([^;]+)', gtdb_taxonomy)
        if species_match:
            accession_species_dict[assembly] = species_match.group(1)

        phylum_match = re.search(r'p__([^;]+)', gtdb_taxonomy)
        if phylum_match:
            accession_phylum_dict[assembly] = phylum_match.group(1)

        genus_match = re.search(r'g__([^;]+)', gtdb_taxonomy)
        if genus_match:
            accession_genus_dict[assembly] = genus_match.group(1)


non_ly_columns = [col for col in tpm_all.columns if 'LY' not in str(col)]
filtered_df = tpm_all[non_ly_columns].copy()

filtered_df = tpm_all.copy()

filtered_df['accession'] = filtered_df['#Name'].apply(lambda x: str(x)[:13] if len(str(x)) >= 13 else str(x))
filtered_df['phyla'] = filtered_df['accession'].map(accession_phylum_dict)
filtered_df['genus'] = filtered_df['accession'].map(accession_genus_dict)
filtered_df['species'] = filtered_df['accession'].map(accession_species_dict)

numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns
sum_by_genus = filtered_df.groupby(f'{group_by}')[numeric_cols].sum()

genus_phylum_map = filtered_df.drop_duplicates('genus').set_index('genus')['phyla']
sum_by_genus['phyla'] = genus_phylum_map

sum_by_genus.to_csv(f"{group_by}_transcription_species.csv")
print('Data has been saved.')
