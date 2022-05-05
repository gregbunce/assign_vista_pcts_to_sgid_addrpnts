RUN THE PROJECT
Run: C:\Users\gbunce\Documents\projects\batch_files\run_county_election_files.bat
Move output from here: C:\Temp\county_election_files
To Google Drive public share: G:\My Drive\agrc_public_share\long_term_share\voting_elections\sgid_address_pnts_with_vista_pcts
Notify Mark


SET UP PROJECT
create conda env for project
-- conda create --clone arcgispro-py3 --name election_address_files

-- conda create --name election_files
-- activate election_files
-- conda install -c esri arcpy
-- pip install docopt

requirements: python env, 
access to state network for internal datasets, arcpy, os, 
