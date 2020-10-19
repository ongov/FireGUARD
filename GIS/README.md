This group of tools processes eFRI and other data to create fuel, slope, aspect and
elevation rasters, as well as RamPART geodatabases

# Introduction        {#gis_intro_sec}

This relies on ArcGIS to process the inputs

# Setup               {#gis_setup_sec}

## Step 1: Install ArcGIS                   {#gis_step1}

This is required for the scripts to work. You need a Spatial Analyst licence


## Step 2: Run the WeatherSHIELD setup     {#gis_step2}

This should properly set up a python environment


## Step 3: Download the eFRI data for the LIO Data warehouse      {#gis_step3}

This will arrive as a nested .zip file


## Step 4: Run unEFRI.py        {#gis_step4}

This will unpackge the eFRI data into a common geodatabase


## Step 5: Run fbp_convert\fuelconversion.py        {#gis_step5}

This will process the unpackged eFRI data and assign FBP fuel types to the polygons


## Step 6: Run fixWater.py        {#gis_step6}

This will create the fuel, slope, and aspect rasters

## Step 7: Run rampart.python           {#gis_step7}

This will create the RamPART rasters and geodatabases

## Step 8: Run updateADDI.py (Optional) {#gis_step8}

This will create an updated AROD/ADDI grid with the new FBP classifications for the cells
