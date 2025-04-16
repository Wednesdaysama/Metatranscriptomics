##### Launch an interactive session on ARC
    salloc --mem=20G -c 1 -N 1 -n 1  -t 04:00:00

<details>
<summary> 

## Reads quality control </summary>

### Reads quality control report - [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/) and [multiqc](https://github.com/MultiQC/MultiQC)
#### Installation
    conda create --prefix ~/bio/bin/fastqc_env
    conda activate ~/bio/bin/fastqc_env
    conda install -c bioconda fastqc
    conda install -c bioconda multiqc
    fastqc -h
    multiqc -h
    
#### Slurm - fastqc.slurm
    
    #!/bin/bash
    #SBATCH --job-name=fastqc      # Job name
    #SBATCH --output=%x.log  # Job's standard output and error log
    #SBATCH --nodes=1             # Run all processes on a single node
    #SBATCH --ntasks=1            # Run 1 tasks
    #SBATCH --cpus-per-task=30    # Number of CPU cores per task
    #SBATCH --mem=50G            # Job memory request
    #SBATCH --time=50:00:00       #
    #SBATCH --mail-user=lianchun.yi1@ucalgary.ca  # Send the job information to this email
    #SBATCH --mail-type=ALL                       # Send the type: <BEGIN><FAIL><END>
    pwd; hostname; date

    conda activate /home/lianchun.yi1/bio/bin/fastqc_env
    cd /work/ebg_lab/eb/250409_A00906_0696_AH3LM3DMX2-BaseCalls/Shotgun-metatranscri
    fastqc Li5245{1..8}/*.gz Li5247{1..6}/*.gz -o /work/ebg_lab/eb/overwinter/2025Apr/fastqc --svg --noextract -t 30 -k 10
    cd /work/ebg_lab/eb/overwinter/2025Apr/fastqc
    multiqc -o ./ -n rawReads ./

</details>

<details>
<summary>

## Raw reads filtration </summary>
### Installation
    wget https://sourceforge.net/projects/bbmap/files/BBMap_39.10.tar.gz/download -O BBMap.tar.gz
    tar -xvzf BBMap.tar.gz
    rm BBMap.tar.gz
    nano ~/.bashrc # export PATH=$PATH:/home/lianchun.yi1/software/bbmap
    source ~/.bashrc
    bbmap.sh --version

### bbduk.slurm
    #!/bin/bash
    #SBATCH --job-name=bbduk
    #SBATCH --output=%x.log
    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=32    # Number of CPU cores per task
    #SBATCH --mem=100G            # Job memory request
    #SBATCH --time=150:00:00
    #SBATCH --mail-user=lianchun.yi1@ucalgary.ca  # Send the job information to this email
    #SBATCH --mail-type=ALL                       # Send the type: <BEGIN><FAIL><END>
    pwd; hostname; date

    INPUT_DIR="/work/ebg_lab/eb/250409_A00906_0696_AH3LM3DMX2-BaseCalls/Shotgun-metatranscri/"
    OUTPUT_DIR="/work/ebg_lab/eb/overwinter/2025Apr/"

    SAMPLES=$(ls ${INPUT_DIR}/*/LY-*_R1_001.fastq.gz | sed 's/_L00.*_R1_001.fastq.gz//' | sort -u)

    for SAMPLE_PREFIX in $SAMPLES; do

        BASENAME=$(basename $SAMPLE_PREFIX | awk -F'LY-' '{print $2}')
        echo "Processing $BASENAME ..."

        MERGED_R1=${OUTPUT_DIR}/${BASENAME}_merged_R1.fastq.gz
        MERGED_R2=${OUTPUT_DIR}/${BASENAME}_merged_R2.fastq.gz

        cat ${SAMPLE_PREFIX}_L00*_R1_001.fastq.gz > $MERGED_R1
        cat ${SAMPLE_PREFIX}_L00*_R2_001.fastq.gz > $MERGED_R2

        # Step 1: trimming
        bbduk.sh \
            in1=$MERGED_R1 \
            in2=$MERGED_R2 \
            out1=${OUTPUT_DIR}/${BASENAME}_trimmed_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${BASENAME}_trimmed_R2.fastq.gz \
            ftm=5 \
            t=32

        # Step 2: adapter trimming
        bbduk.sh \
            in1=${OUTPUT_DIR}/${BASENAME}_trimmed_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${BASENAME}_trimmed_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${BASENAME}_tbo_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${BASENAME}_tbo_R2.fastq.gz \
            tbo tpe k=23 mink=11 hdist=1 ktrim=r \
            t=32

        # Step 3: remove Phix contamination
        bbduk.sh \
            in1=${OUTPUT_DIR}/${BASENAME}_tbo_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${BASENAME}_tbo_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${BASENAME}_phix_removed_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${BASENAME}_phix_removed_R2.fastq.gz \
            ref=~/software/bbmap/resources/phix174_ill.ref.fa.gz \
            k=31 hdist=1 \
            t=32

        # Step 4: quality filtering
        bbduk.sh \
            in1=${OUTPUT_DIR}/${BASENAME}_phix_removed_R1.fastq.gz \
            in2=${OUTPUT_DIR}/${BASENAME}_phix_removed_R2.fastq.gz \
            out1=${OUTPUT_DIR}/${BASENAME}_final_R1.fastq.gz \
            out2=${OUTPUT_DIR}/${BASENAME}_final_R2.fastq.gz \
            qtrim=rl trimq=15 minlength=30 \
            t=32

        # Cleanup: delete intermediate and merged files
        rm $MERGED_R1 $MERGED_R2 \
        ${OUTPUT_DIR}/${BASENAME}_trimmed_*.fastq.gz \
        ${OUTPUT_DIR}/${BASENAME}_tbo_*.fastq.gz \
        ${OUTPUT_DIR}/${BASENAME}_phix_removed_*.fastq.gz

        echo "Finished processing $BASENAME"
    done
</details>
    
