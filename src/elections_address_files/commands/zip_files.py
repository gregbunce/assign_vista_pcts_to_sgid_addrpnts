import os, zipfile, glob, shutil

def zipfiles(directory):
  
    # File extension to zip.
    #ext = ('.gdb', '.csv')
    ext = ('.gdb')
    
    # Iterate over all files and check for desired extentions for zipping.
    for file in os.listdir(directory):
        if file.endswith(ext):
            #: Zip it.
            input_fgdb_name = file.rsplit( ".", 1)[0]
            output_zipped_fgdb_name = input_fgdb_name + "_gdb.zip"
            zip_file_geodatabase(directory + "\\" + file, directory + "\\" + output_zipped_fgdb_name)



            # newZipFN = directory + "\\" + file
            # inFileGeodatabase = directory + "\\" + output_zipped_fgdb_name

            # zipobj = zipfile.ZipFile(newZipFN,'w')

            # for infile in glob.glob(inFileGeodatabase+"/*"):
            #     zipobj.write(infile, os.path.basename(inFileGeodatabase)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)
            #     print ("Zipping: " + infile)

            # zipobj.close()

        else:
            continue


#### BEGIN >>> Zip File Geodatabase function ####
def zip_file_geodatabase(inFileGeodatabase, newZipFN):
   if not (os.path.exists(inFileGeodatabase)):
      return False

   if (os.path.exists(newZipFN)):
      os.remove(newZipFN)

   zipobj = zipfile.ZipFile(newZipFN,'w')

   for infile in glob.glob(inFileGeodatabase+"/*"):
      zipobj.write(infile, os.path.basename(inFileGeodatabase)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)
      print ("Zipping: " + infile)

   zipobj.close()
   return True
#### Zip File Geodatabase function <<< END ####
