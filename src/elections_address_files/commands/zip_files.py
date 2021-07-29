import os, zipfile

# Zip files.
def zipfiles(directory):
  
    # File extension to zip.
    #ext = ('.gdb', '.csv')
    ext = ('.gdb')
    
    # Iterate over all files and check for desired extentions for zipping.
    for file in os.listdir(directory):
        if file.endswith(ext):
            #: Zip it.
            input_fgdb_name = file.rsplit( ".", 1)[0]
            output_zipped_fgdb_name = "/" + input_fgdb_name + "_gdb.zip"
            full_path_to_fgdb = directory + "/" + file

            print("   Zipping " + str(full_path_to_fgdb))

            outFile = f'{full_path_to_fgdb[0:-4]}_gdb.zip'
            gdbName = os.path.basename(full_path_to_fgdb)

            with zipfile.ZipFile(outFile,mode='w',compression=zipfile.ZIP_DEFLATED,allowZip64=True) as myzip:
                for f in os.listdir(full_path_to_fgdb):
                    if f[-5:] != '.lock':
                        myzip.write(os.path.join(full_path_to_fgdb,f),gdbName+'\\'+os.path.basename(f))

        else:
            continue
