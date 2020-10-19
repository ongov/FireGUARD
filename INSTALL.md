# Setup

## Step 1: Run the setup.bat in the setup folder

This should:
1) install SQL Server;
2) configure IIS;
3) create databases;
4) load all previous weather into databases;
5) and set up scheduled tasks.

## Step 2: Run WeatherSHIELD\reanalysis1.py

This will populate the database with hindcast data

## Step 3: Edit files in settings directory

Replace the contents of the files with the appropriate locations or settings.

## Step 4: Run WeatherSHIELD\load_previous.py

This will populate the database with previously downloaded data
