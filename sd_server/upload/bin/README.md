Species delimitation using a Poisson tree processes model

By Jiajie Zhang 10-11-2013.
Questions and bugs report please sent to bestzhangjiajie[at]gmail[dot]com.
Before reading the following text, please check: https://github.com/zhangjiajie/SpeciesCounting for latest updates


========================================================================================================================================
(1) What's in the package?

    This package contains several programs written in Python that can give species delimitation hypothesis 
    based on a gene tree inferred from molecular sequences.
    
    GMYC.py    Implements the single threshold general mixed Yule coalescent (GMYC) model which was first proposed by Pons et al 
               (Sequence-Based Species Delimitation for the DNA Taxonomy of Undescribed Insects. Systematic Biology, 55(4), 595–609)
               This model requires the input tree to be time calibrated ultrametric tree, in other words, the branch length of the 
               input ultrametric tree should represent time. 
               The most commonly used programs for getting an ultrametric tree are BEAST, DPPDIV and r8s.
               There is also an R implementation of this model called "splits" by Tomochika Fujisawa
               (http://barralab.bio.ic.ac.uk/downloads.html)
               To find out how to use it, type ./GMYC.py
             
    PTP.py     This is a newly introduced model we call it Poisson tree processes(PTP) model. In PTP, we model speciations or branching 
               events in terms of number of mutations. So it only requires a phylogenetic input tree, for example the output of RAxML. 
               To be more clear, the branch lengths should represent number of mutations. Our numerous tests show PTP outperforms GMYC. 
               Furthermore, PTP is much easier to use, since it can use the phylogenetic tree directly without needing the difficult and 
               error prone procedures of time calibration required by GMYC.
               To find out how to use it, type ./PTP.py  
             
    EPA_PTP.py This is a pipeline that uses evolutionary placement algorithm (EPA) and PTP to count species number when reference data is 
               available. For details of EPA, please read this paper: Performance, accuracy, and Web server for evolutionary placement of short 
               sequence reads under maximum likelihood. Systematic biology, 60(3), 291–302.
               The pipeline will first run USEARCH to remove the chimera sequences, then it will use EPA to place the query reads to optimal 
               position on the reference tree inferred from the reference alignment. PTP will then be applied to the reads been placed on each 
               branch, with a fixed speciation rate inferred from the reference data.  
               Similar analysis used in bacterial metagenomics studies are called OTU-picking. For discussions about OTU-picking and EPA_PTP 
               species counting, please have a look at our paper. 
               Type ./EPA_PTP.py for help and instructions.
 

(2) Which operating system is required?

    I wrote and tested all the python code under Ubuntu Linux. So everything should run well under Linux if you follow the instructions below or 
    the output of the python programs. I did not have the time and chance to test them under windows or mac yet, however, I think GMYC.py and PTP.py 
    should be able to run on windows and mac if you have properly installed the dependent python packages (see below). EPA_PTP.py was designed to 
    run with NGS data, which means the calculations might be intense if you have say 10,000 reads. So ideally it should be run on a multi-core 
    Linux server such that it can speedup using the PTHREADS version of RAxML. The biodiversity soup data in our paper, for example, will need 
    24-48 hour to finish on our 8-core i7 server. If you encounter any problems to run the program under Linux, simply drop me an e-mail.  
               


(3) Install dependent python packages

    The programs used ETE package (http://ete.cgenomics.org/) for tree manipulations, and some functions from scipy and matplotlib. I included 
    a copy of ETE package, so there is no need for seperate installation, however, ETE is dependent on some python packages, The following 
    python packages are needed:  python-setuptools python-numpy python-qt4 python-scipy python-mysqldb python-lxml python-matplotlib 
    
    if you are running Ubuntu, or Debian GNU/Linux distribution, you can try the following:
    
    sudo apt-get install python-setuptools python-numpy python-qt4 python-scipy python-mysqldb python-lxml python-matplotlib



(4) Download and compile required programs for EPA_PTP pipeline

    The EPA_PTP pipeline requires the following three programs to run, you can download, compile and put them in the included bin folder. 
    I included the binary executable of RAxML and HMMMER for 64-bit Linux in the bin folder, However, USEARCH does NOT allow for redistribution. 
    USEARCH provides a free binary 32-bit version that will also run on 64-bit platform, but must be requested per e-mail. 
    
    a. USEARCH: http://www.drive5.com/usearch/ please rename the executable file to "usearch", and copy to bin/ folder
    b. HMMER: http://hmmer.janelia.org/ please copy "hmmbuild" and "hmmalign" to bin/ folder
    c. RAxML: https://github.com/stamatak/standard-RAxML please compile the PTHREADS version, rename to "raxmlHPC-PTHREADS-SSE3" and copy to bin/



(5) Important notes on the input data

    a. All trees must be in Newwick format.
    b. All sequences must be in Fasta format.
    c. The input tree to GMYC must be strictly ultrametric (I do not check for this!). pGMYC experimentally support multifurcating input tree.
    d. The input tree to PTP should ideally be rooted with some outgroups, if an unrooted tree is used, please specify the -r option.
    e. The input to EPA_PTP.py should be two alignments, one should be the query sequences that you want to know how many species are there;
       the other should be the reference alignment, which should contain ONLY ONE sequence for each known species. The reference data represents our 
       knowledge about the speciation history, so EPA_PTP will estimate the speciation rate from it. If multiple sequences exist for a single
       species, then the speciation rate will be over-estimated.
    f. If your query sequences are not aligned, EPA_PTP.py can align them using HMMER, however, the reference sequences must be properly aligned.
       Both reference and query alignment should be of the same length, if not, please use the same option in EPA_PTP.py to align the query sequences 
       to the reference alignment.  
    

(6) Examples

    a. Delimit species using PTP:
    ./PTP.py -t example/ptp_example.tre -s
    
    b. Delimit species using GMYC on an untrametric tree:
    ./GMYC.py -t example/gmyc_example.tre -st
    
    c. Delimit species with reference data:
    ./EPA_PTP.py -step species_counting -folder full-path-to-example-folder/ -refaln full-path-to-example-folder/ref.afa -query full-path-to-example-folder/query.afa


(7) How to cite

    If you find PTP and pGMYC useful to your research, please cite: J. Zhang, P. Kapli, P. Pavlidis, A. Stamatakis: "A General Species Delimitation Method 
    with Applications to Phylogenetic Placements". In Bioinformatics (2013), 29 (22): 2869-2876.
    
    
(8) Web server

    There is also a simple and experimental web server available for PTP:
    http://species.h-its.org/ptp/
    For the moment, I can not gurantee the web server is using the latest PTP implementation. So whenever possible, I encourage you to try this python program.
    
