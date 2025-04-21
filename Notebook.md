##### Launch an interactive session on ARC
    salloc --mem=20G -c 1 -N 1 -n 1  -t 04:00:00

<details>
<summary> 

## Reads quality control report - [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/) and [multiqc](https://github.com/MultiQC/MultiQC) </summary>

### Reads quality control report 
#### Installation
    conda create --prefix ~/bio/bin/fastqc_env
    conda activate ~/bio/bin/fastqc_env
    conda install -c bioconda fastqc
    conda install -c bioconda multiqc
    fastqc -h
    multiqc -h
    
#### Slurm - fastqc_multiqc.slurm
    conda activate /home/lianchun.yi1/bio/bin/fastqc_env
For some reason, I have to activate the fastqc_env before submitting the slurm work. To avoid the OUT_OF_MEMORY error, do not use a for loop and run FastQC commands individually.
    
    #!/bin/bash
    #SBATCH --job-name=fastqc_multiqc     
    #SBATCH --output=%x.log  
    #SBATCH --nodes=1          
    #SBATCH --ntasks=1           
    #SBATCH --cpus-per-task=30    
    #SBATCH --mem=50G            
    #SBATCH --time=50:00:00       # 5.5 hours for 54 samples
    #SBATCH --mail-user=lianchun.yi1@ucalgary.ca  
    #SBATCH --mail-type=ALL                       
    pwd; hostname; date

    conda activate /home/lianchun.yi1/bio/bin/fastqc_env
    cd /work/ebg_lab/eb/250409_A00906_0696_AH3LM3DMX2-BaseCalls/Shotgun-metatranscri
    fastqc LY-SumRNA-MatSite6_S3_L001_R1_001.fastq.gz -o /work/ebg_lab/eb/overwinter/2025Apr/fastqc --svg --noextract -t 30 -k 10
    fastqc LY-SumRNA-MatSite6_S3_L001_R2_001.fastq.gz -o /work/ebg_lab/eb/overwinter/2025Apr/fastqc --svg --noextract -t 30 -k 10
    fastqc LY-SumRNA-MatSite6_S3_L002_R1_001.fastq.gz -o /work/ebg_lab/eb/overwinter/2025Apr/fastqc --svg --noextract -t 30 -k 10
    fastqc LY-SumRNA-MatSite6_S3_L002_R2_001.fastq.gz -o /work/ebg_lab/eb/overwinter/2025Apr/fastqc --svg --noextract -t 30 -k 10

    cd /work/ebg_lab/eb/overwinter/2025Apr/fastqc
    multiqc -o ./ -n rawReads ./

</details>

<details>
<summary>

## Raw reads filtration - BBmap </summary>
### Installation
    wget https://sourceforge.net/projects/bbmap/files/BBMap_39.10.tar.gz/download -O BBMap.tar.gz
    tar -xvzf BBMap.tar.gz
    rm BBMap.tar.gz
    nano ~/.bashrc # export PATH=$PATH:/home/lianchun.yi1/software/bbmap
    source ~/.bashrc
    bbmap.sh --version

### bbduk.slurm
Processing reads from different lanes separately.

    #!/bin/bash
    #SBATCH --job-name=bbduk
    #SBATCH --output=%x.log
    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=32    # Number of CPU cores per task
    #SBATCH --mem=100G            # Job memory request
    #SBATCH --time=150:00:00      # run for 7 hours
    #SBATCH --mail-user=lianchun.yi1@ucalgary.ca  # Send the job information to this email
    #SBATCH --mail-type=ALL                       # Send the type: <BEGIN><FAIL><END>
    pwd; hostname; date

    INPUT_DIR="/work/ebg_lab/eb/250409_A00906_0696_AH3LM3DMX2-BaseCalls/Shotgun-metatranscri/"
    OUTPUT_DIR="/work/ebg_lab/eb/overwinter/2025Apr/seperate_lanes_bbduk"

    # Get all R1 files (including lane information)
    R1_FILES=$(ls ${INPUT_DIR}/*/LY-*_L00*_R1_001.fastq.gz | sort)

    for R1_FILE in $R1_FILES; do
        # Extract the corresponding R2 file
        R2_FILE=$(echo $R1_FILE | sed 's/_R1_/_R2_/')

        # Extract sample name with lane information
        SAMPLE_NAME=$(basename $R1_FILE | awk -F'_' '{print $1 "_" $2 "_" $3}')  # Keeps LY-XXXXX_L00X
        BASENAME=$(basename $R1_FILE | awk -F'LY-' '{print $2}' | awk -F'_L00' '{print $1}')  # Just the LY-XXXXX part

        LANE=$(basename $R1_FILE | awk -F'_L00' '{print $2}' | awk -F'_' '{print $1}')

        echo "Processing $SAMPLE_NAME (Lane $LANE) ..."

        # Create output filenames with lane information
        MERGED_R1=${OUTPUT_DIR}/${SAMPLE_NAME}_R1.fastq.gz
        MERGED_R2=${OUTPUT_DIR}/${SAMPLE_NAME}_R2.fastq.gz

        # Since we're processing lanes separately, we don't need to cat files
        # Just copy or rename the files (in case they need to be in a different directory)
        cp $R1_FILE $MERGED_R1
        cp $R2_FILE $MERGED_R2

        # trimming - include lane in output names
        bbduk.sh \
            in1=$MERGED_R1 \
            in2=$MERGED_R2 \
            out1=${OUTPUT_DIR}/${SAMPLE_NAME}_trimmed_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${SAMPLE_NAME}_trimmed_R2.fastq.gz \
            ftm=5 \
            t=32

        bbduk.sh \
            in1=${OUTPUT_DIR}/${SAMPLE_NAME}_trimmed_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${SAMPLE_NAME}_trimmed_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${SAMPLE_NAME}_tbo_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${SAMPLE_NAME}_tbo_R2.fastq.gz \
            tbo tpe k=23 mink=11 hdist=1 ktrim=r \
            t=32

        # remove Phix contamination
        bbduk.sh \
            in1=${OUTPUT_DIR}/${SAMPLE_NAME}_tbo_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${SAMPLE_NAME}_tbo_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${SAMPLE_NAME}_phix_removed_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${SAMPLE_NAME}_phix_removed_R2.fastq.gz \
            ref=~/software/bbmap/resources/phix174_ill.ref.fa.gz \
            k=31 hdist=1 \
            t=32

        # filter low quality reads
        bbduk.sh \
            in1=${OUTPUT_DIR}/${SAMPLE_NAME}_phix_removed_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${SAMPLE_NAME}_phix_removed_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${SAMPLE_NAME}_final_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${SAMPLE_NAME}_final_R2.fastq.gz \
            qtrim=rl trimq=15 minlength=30 \
            t=32

        # delete intermediate files
        rm ${OUTPUT_DIR}/${SAMPLE_NAME}_trimmed_*.fastq.gz \
           ${OUTPUT_DIR}/${SAMPLE_NAME}_tbo_*.fastq.gz \
           ${OUTPUT_DIR}/${SAMPLE_NAME}_phix_removed_*.fastq.gz

        echo "Finished processing $SAMPLE_NAME (Lane $LANE)"
    done

Only keeping the **_final_** files from quality filtering. These files will be used as input files for rRNA cleanup.
    
</details>

<details>
<summary>

## Removing rRNA sequences - [Sortmerna](https://github.com/sortmerna/sortmerna) </summary>
### Installation
    conda create -n sortmerna
    conda activate sortmerna
    conda install sortmerna

### sortmerna.slurm
    conda activate sortmerna
Again, I have to submit this Slurm job after activating a conda env. Also, do not use a for loop and run sortmerna commands individually.

    #!/bin/bash
    #SBATCH --job-name=sortmerna
    #SBATCH --output=%x.log
    #SBATCH --nodes=1        
    #SBATCH --ntasks=1         
    #SBATCH --cpus-per-task=40   
    #SBATCH --mem=150G      
    #SBATCH --time=150:00:00      # 10 hours for 4 paired-end reads (8 .gz files in total)
    #SBATCH --mail-user=lianchun.yi1@ucalgary.ca  # Send the job information to this email
    #SBATCH --mail-type=ALL                       # Send the type: <BEGIN><FAIL><END>
    pwd; hostname; date

    conda activate sortmerna
    sortmerna --ref /work/ebg_lab/referenceDatabases/sortmerna_db/smr_v4.3_default_db.fasta \
        --workdir ./sortmerna/ \
        --reads LY-FallRNA-MatSite3_S23_L001_final_R1.fastq.gz \
        --reads LY-FallRNA-MatSite3_S23_L001_final_R2.fastq.gz \
        --aligned LY-FallRNA-MatSite3_S23_L001_rRNA_reads \
        --other LY-FallRNA-MatSite3_S23_L001_non_rRNA_reads \
        --sam --SQ --log --fastx --threads 40 --paired_in
    rm -r ./sortmerna/kvdb/

    sortmerna --ref /work/ebg_lab/referenceDatabases/sortmerna_db/smr_v4.3_default_db.fasta \
        --workdir ./sortmerna/ \
        --reads LY-FallRNA-MatSite3_S23_L002_final_R1.fastq.gz \
        --reads LY-FallRNA-MatSite3_S23_L002_final_R2.fastq.gz \
        --aligned LY-FallRNA-MatSite3_S23_L002_rRNA_reads \
        --other LY-FallRNA-MatSite3_S23_L002_non_rRNA_reads \
        --sam --SQ --log --fastx --threads 40 --paired_in
    rm -r ./sortmerna/kvdb/


</details>

<details>
<summary>

## Mapping </summary>
Folder /work/ebg_lab/eb/overwinter/2025Apr/soda_lake_mags contains 91 soda lake genomes.

seal.sh in=LY-FallRNA-MatSite3_S23_merged_non_rRNA_reads.fq.gz /work/ebg_lab/eb/overwinter/2025Apr/soda_lake_mags/*.fna stats=sealstats.txt rpkm=sealrpkm.txt ambig=random
