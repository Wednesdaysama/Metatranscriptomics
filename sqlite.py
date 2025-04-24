from pathlib import Path
from metaerg.datatypes import sqlite
import os

# the working_dir is /work/ebg_lab/eb/overwinter/2025Apr/soda_lake_mags
working_dir = Path(os.getcwd())
annotations_dir = working_dir / "annotations.sqlite"

for sqlite_file in annotations_dir.glob("G*"):
    print(f"\nProcessing file: {sqlite_file.name}")
    fa_filename = sqlite_file.with_suffix('.fa')
    print(f"Creating FASTA file: {fa_filename.name}")
    try:
        db_connection = sqlite.connect_to_db(sqlite_file)
        with open(fa_filename, 'w') as fa_file:
            for feature in sqlite.read_all_features(db_connection):
                fa_file.write(f">{feature.id} ({feature.descr}) ({feature.taxon})\n")
                fa_file.write(f"{feature.nt_seq}\n\n")

        print(f"Successfully wrote {fa_filename.name}")

    except Exception as e:
        print(f"Error processing {sqlite_file.name}: {str(e)}")
    finally:
        if 'db_connection' in locals():
            db_connection.close()
        del db_connection

print("\nProcessing complete.")
