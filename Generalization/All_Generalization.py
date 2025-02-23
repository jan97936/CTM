#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ambe3073
#
# Created:     07/04/2015
# Copyright:   (c) ambe3073 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import arcpy
import datetime


def create_backup(backup, gen_workspace, output_folder, model, count):
    if backup == 'true':
        arcpy.AddMessage("Creating Backup")
        out = output_folder + '\\after_' + str(count) + '_' + model + '.gdb'
        arcpy.Copy_management(gen_workspace, out)
    count += 1
    return count

def main():

    arcpy.env.overwriteOutput = True

    if arcpy.CheckExtension("Spatial") != "Available":

        arcpy.AddError("The Spatial Analyst Extension is not available.")
        raise arcpy.ExecuteError

    if arcpy.CheckExtension("foundation") != "Available":

        arcpy.AddError("The Production Mapping Extension is not available.")
        raise arcpy.ExecuteError


    #get the path of the script being run to determine path of toolbox
    tbx_path = os.path.dirname(__file__)
    tbx = tbx_path + '\\CTM50KGeneralization.tbx'

    arcpy.AddMessage("Toolbox path is: " + tbx)

    #import the toolbox
    arcpy.ImportToolbox(tbx)

    #get the inputs
    input_workspace = arcpy.GetParameterAsText(0)
    aoi_fc = arcpy.GetParameterAsText(1)
    output_folder = arcpy.GetParameterAsText(2)
    output_name = arcpy.GetParameterAsText(3)
    product_library = arcpy.GetParameterAsText(4)
    vvs = arcpy.GetParameterAsText(5)
    backup = arcpy.GetParameterAsText(6)

    count = 0

    #input_path = os.path.dirname(input_workspace)

    start_start = datetime.datetime.now().replace(microsecond=0)
    try:
        scratch_db_name = 'scratch'
        scratch_db = output_folder + '\\' + scratch_db_name + '.gdb'
        if not arcpy.Exists(scratch_db):
            arcpy.CreateFileGDB_management(output_folder, scratch_db_name)

        if arcpy.Exists(scratch_db):
            arcpy.AddMessage("Scratch database: " + str(scratch_db))

        #create the output database
        arcpy.AddMessage("Creating generalization database")
        gen_workspace = output_folder + '\\' + output_name + '.gdb'
        arcpy.Copy_management(input_workspace, gen_workspace)

        #Creating the Scratch workspace
        #scratch_workspace = arcpy.CreateFileGDB_management(output_folder, "Scratch")
        scratch_workspace = 'in_memory'

        #Run the prepare script
        arcpy.AddMessage("Running Prepare Model")

        start = datetime.datetime.now().replace(microsecond=0)

        arcpy.PrepareData_CTM50KGeneralization(gen_workspace, scratch_workspace, aoi_fc, vvs)
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'PrepareData', count)

        #Run the transportation script
        arcpy.AddMessage("Running Transportation Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.Transportation_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'Transportation', count)

        #Run the buildings script
        arcpy.AddMessage("Running Building Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.Buildings_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'Building', count)

        #Run the hydro script
        arcpy.AddMessage("Running Hydrography Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.Hydro_CTM50KGeneralization(gen_workspace, scratch_workspace, scratch_db)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'Hydro', count)

        #Run the Land Cover script
        arcpy.AddMessage("Running Land Cover Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.arcpy.LandCov_CTM50KGeneralization(gen_workspace, scratch_workspace, scratch_db)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'LandCov', count)

        #Run the Elev script
        arcpy.AddMessage("Running Elevation Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.Elev_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'Elev', count)

        #Run the Symbology script
        arcpy.AddMessage("Running Apply Symbology Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.ApplySymbology_CTM50KGeneralization(gen_workspace, product_library, vvs)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'Symbology', count)

        #Run the line conflicts script
        arcpy.AddMessage("Running Line Conflicts Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.ResolveLine_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'ResolveLine', count)

        #Run the point conflicts script
        arcpy.AddMessage("Running Structure Conflicts Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.ResolveStructure_CTM50KGeneralization(gen_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'ResolveStructure', count)

        #Run the hydro conflicts script
        arcpy.AddMessage("Running Hydro Conflicts Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.ResolveHydro_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'ResolveHydro', count)

        #Run the veg conflicts script
        arcpy.AddMessage("Running Vegetation Conflicts Model")
        start = datetime.datetime.now().replace(microsecond=0)
        arcpy.ResolveVeg_CTM50KGeneralization(gen_workspace, scratch_workspace)
        arcpy.AddMessage(arcpy.GetMessages())
        end = datetime.datetime.now().replace(microsecond=0)
        arcpy.AddMessage(arcpy.GetMessages())
        arcpy.AddMessage("Took " + str(end - start))

        count = create_backup(backup, gen_workspace, output_folder, 'ResolveVeg', count)

    finally:
        if arcpy.Exists(scratch_workspace):
            try:
                arcpy.Delete_management(scratch_workspace)
            except:
                arcpy.AddWarning("Unable to delete scratch workspace " + str(scratch_workspace))
        #Clean up the final database
        if arcpy.Exists(os.path.join(gen_workspace, "AOI_Boundary_line")) == True:
            arcpy.Delete_management(os.path.join(gen_workspace, "AOI_Boundary_line"))
        if arcpy.Exists(os.path.join(gen_workspace, "Partition")) == True:
            arcpy.Delete_management(os.path.join(gen_workspace, "Partition"))

        end_end = datetime.datetime.now().replace(microsecond=0)



        arcpy.AddMessage("Took Total " + str(end_end - start_start))
        arcpy.SetParameter(7, gen_workspace)
    pass

if __name__ == '__main__':
    main()
