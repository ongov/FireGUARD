"""Convert to FBP fuels"""

import arcpy
import arcpy.da
import re
import sys

import datetime

VERBOSE = False
CURRENT_YEAR = datetime.datetime.now().year

def SPCcollection(row, fields, idx):
    ''' Create a dictionary of the species in the polygon '''
    invalid = False
    strSpcComp = row[idx['OSPCOMP']].strip().upper()
    SPCCollection = {}
    TotalSpecies = 0
    rem = strSpcComp
    while len(rem) > 0:
        # we're expecting species to be 2 letters and then a number for the pct
        m = re.search('[A-Z]* *[0-9]*', rem)
        # find the next species
        cur = m.group(0)
        # take the current species out of the string
        rem = rem.replace(cur, '').strip()
        kv = [x for x in cur.split(' ') if len(x) > 0]
        species = kv[0]
        pct = int(kv[1])
        # only use a species if it's 2 characters long or it's redbud
        if (2 == len(species) or species == 'RED'):
            # make sure things aren't in there twice
            if not SPCCollection.has_key(species):
                SPCCollection[species] = pct
            else:
                SPCCollection[species] += pct
                # output an error message but still use the values
                invalid = True
            TotalSpecies += pct
    if invalid or TotalSpecies <> 100:
        # This tests to see if Species composition is valid ie. Total not equal to 100
        print (' - '.join(["Error: Invalid OSPCOMP - POLYID", row[idx["POLYID"]], strSpcComp]))
    if TotalSpecies <> 100:
        # recalculate percentage based on total sum
        print "Corrected percentages based on sum {}".format(TotalSpecies)
        for k, v in SPCCollection.iteritems():
            SPCCollection[k] = int(v * 100.0 / TotalSpecies)
            print SPCCollection[k]
    return SPCCollection


def SPCsum(dictSPC, *fuels):
    ''' Find the sum of the percent of the polygon composed of the given species '''
    result = 0
    for f in fuels:
        if dictSPC.has_key(f):
            result += dictSPC[f]
    return result


def SeekMatch(row, fields, idx, dictSpecies):
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Looking for an ideal match
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    pctSW = SPCsum(dictSpecies, "SW")
    pctBF = SPCsum(dictSpecies, "BF")
    pctPJ = SPCsum(dictSpecies, "PJ")
    pctSB = SPCsum(dictSpecies, "SB")
    pctSB_SX_SW = pctSB + pctSW + SPCsum(dictSpecies, "SX")
    pctSB_SX_SW_BF = pctSB_SX_SW + SPCsum(dictSpecies, "BF")
    pctPW_PR = SPCsum(dictSpecies, "PW", "PR")
    pctConifer = (SPCsum(dictSpecies,
                         "CE", "CR", "CW", "HE", "LA", "LE", "LJ", "OC", "PS", "PX", "PN", "SC",
                         "SK", "SN", "SR") + pctSB_SX_SW_BF + pctPJ + pctPW_PR)
    pctBW = SPCsum(dictSpecies, "BW")
    pctPoplar = SPCsum(dictSpecies, "PB", "PD", "PE", "PH", "PO", "PL", "PT")
    pctDeciduous = SPCsum(dictSpecies,
                          "AB", "AG", "AL", "AW", "AX", "BB", "BC", "BD", "BE", "BG", "BL", "BN",
                          "BP", "BY", "CB", "CD", "CH", "CS", "CT", "ER", "EW", "EX", "HB", "HC",
                          "HI", "HM", "HS", "IW", "KK", "LB", "LO", "MB", "MF", "MH", "MM", "MN",
                          "MO", "MP", "MR", "MS", "MT", "MX", "OB", "OH", "OP", "OR", "OS", "OW",
                          "OX", "PA", "RED", "SS", "TP", "WB", "WI") + pctPoplar + pctBW
    # do this no matter what so we have some more quality control
    if 100 <> (pctDeciduous + pctConifer):
        if abs(100 - pctConifer - pctDeciduous) == 1:
            # was corrected before but the percentages don't quite add up
            if pctConifer > pctDeciduous:
                pctConifer = 100 - pctDeciduous
            else:
                 pctDeciduous = 100 - pctConifer
        else:
            print "Invalid mix {} {} - {}".format(pctDeciduous, pctConifer, row[idx['OSPCOMP']].strip().upper())
            if 100 < (pctDeciduous + pctConifer):
                pctDeciduous /= int((pctDeciduous + pctConifer) * 100)
                pctConifer /= int((pctDeciduous + pctConifer) * 100)
                print "Corrected mix {} {}".format(pctDeciduous, pctConifer)
    if (('DEPTYPE' not in fields or row[idx["DEPTYPE"]] == "INSECTS")
            and (row[idx["YRDEP"]] < 10)
            and (row[idx["MGMTCON1"]] == "DAMG")):
        if pctConifer > 90:
            return 995                                          # M3/M4 95% PDF
        else:
            return 900 + pctConifer                             # M3/M4 PDF%
    occlo = row[idx["OCCLO"]]
    horiz = row[idx["HORIZ"]]
    horizOpen = horiz in ["OC", "OU"]
    horizCont = horiz in ["SS" , "SP", "FP", "MP"]
    if (pctSB >= 80):
        # there shouldn't be C1
        if ((horizOpen) and (occlo < 30)):
            return 105                                          # Vegetated non-fuel
            #~ return 1                                            # C1
        if ((horizCont) and (occlo >= 50)):
            return 2                                            # C2
    # calculate this instead of using OAGE field so it updates over time
    oage = CURRENT_YEAR - row[idx["OYRORG"]]
    if (pctPJ >= 80 and occlo >= 70):
        if oage >= 40:
            return 3                                            # C3
        # must be < 40
        return 4                                                # C4
    if (pctPW_PR >= 80) and (oage > 100):
        return 5                                                # C5
    is_planted = row[idx["DEVSTAGE"]] in ["NEWPLANT", "NEWSEED", "FTGPLANT", "FTGSEED"]
    if (is_planted and occlo >= 80 and row[idx["VERT"]] in ["SI", "SV"]):
        return 6                                                # C6
    if (pctPoplar >= 80):
        return 13                                               # D1/D2
    # round it to nearest 25
    fixedConifer = int(round(pctConifer / 25.0) * 25)
    if ((pctPoplar + pctBW) > 0):
        if ((fixedConifer >= 10 and fixedConifer < 80 and pctConifer < 80)):
            return 600 + fixedConifer                           # M1/M2 Conifer %
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Looking for a fair match
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    if (pctSB_SX_SW >= 80 and horizOpen and occlo >= 30 and occlo <= 50):
        # there shouldn't be C1
        return 105                                              # Vegetated non-fuel
        #~ return 1001                                             # C1 - Fair Match
    if (pctSB_SX_SW_BF >= 70 and horizCont and occlo >= 50):
        return 1002                                             # C2 - Fair Match
    if (pctPJ >= 50 and pctPJ <= 80 and occlo >= 70):
        if oage >= 40:
            return 1003                                         # C3 - Fair Match
        # must be < 40
        return 1004                                             # C4 - Fair Match
    if (pctPW_PR >= 40 and pctPW_PR <= 80 and oage >= 100):
        return 1005                                             # C5 - Fair Match
    if is_planted:
        return 1006                                             # C6 - Fair Match
    if (pctDeciduous >= 80):
        return 1013                                             # D1/D2 - Fair Match
    if pctSB >= 80:
        return 2002                                             # C2 - Bad Match
    if (pctDeciduous > 0):
        if ((fixedConifer > 0) and (pctConifer < 80) and fixedConifer < 100):
            return 1600 + fixedConifer                          # M1/M2 Conifer % - Fair Match
    if pctDeciduous >= 10 and fixedConifer > 0 and pctConifer < 80 and fixedConifer < 100 and 100 == (pctDeciduous + pctConifer):
        return 2600 + fixedConifer                              # M1/M2 Conifer % - Bad Match
    if pctConifer >= 80:
        # look at just basic conifer types
        pctBasicConifer = sum([pctPJ, pctSB_SX_SW, pctPW_PR, pctBF])
        pctBasicDeciduous = sum([pctPoplar, pctBW])
        pctBasic = pctBasicConifer + pctBasicDeciduous
        # if we're mostly regular tree types
        if pctBasic >= 50:
            if pctBasicConifer >= 70:
                # ignore BF content for all of these
                highest = max(pctPJ, pctSB_SX_SW, pctPW_PR)
                if highest == pctSB_SX_SW:
                    return 2002                                 # C2 - Bad Match
                elif highest == pctPW_PR:
                    return 5                                    # C5 - Bad Match
                elif highest == pctPJ:
                    if oage >= 40:
                        return 3                                # C3 - Bad Match
                    # must be < 40
                    return 4                                    # C4 - Bad Match
            # no conifer species is really dominant, so default to mixedwood
            # make sure its between 10 and 90%
            if fixedConifer == 0:
                return 13                                       # D1/D2
            elif fixedConifer < 100:
                return 2600 + fixedConifer                      # M1/M2 Conifer % - Bad Match
        # else it's some weird fuel (e.g. CW or LA) so don't classify it
    return 1104                                                 # Unclassified Forested

fields = None

def FRI2FBP2016(GDBPath, layers=None):
    global fields
    arcpy.env.workspace = GDBPath
    # get the list of layers from the geodatabase
    colFRILayers = sorted(arcpy.ListFeatureClasses())
    # filter down to requested layers
    if layers:
        colFRILayers = [x for x in colFRILayers if x in layers]
    # fields that are necessary to determine FBP typ
    arrFieldNames = ["YRDEP", "MGMTCON1", "HORIZ", "OCCLO", "DEVSTAGE", "VERT", "OYRORG", "OSPCOMP", "POLYTYPE", "POLYID", "SHAPE_AREA"]
    # optional field for type of damage
    arrFieldAll = arrFieldNames + ["DEPTYPE"]
    CompletedLayers = 0
    for pFClass in colFRILayers:
        dictSummary = {}
        # add in DEPTYPE but still filter so we're not getting more data than required
        fields = [x.name for x in arcpy.Describe(pFClass).fields if x.name.upper() in arrFieldAll]
        fields_upper = map(lambda x: x.upper(), fields)
        missing = [x for x in arrFieldNames if x not in fields_upper]
        #''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # Add the FBP and Ont value fields
        #   FBPvalue - This will hold the calculated FBP value that can be used in Prometheus
        #   OntFBP - This will hold the Ontario determined FBP value where any value >1000 is an estimated value
        #''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        def AddFBPfield(FeatureClass, FieldName):
            global fields
            if FieldName.lower() not in map(lambda _: _.lower(), fields):
                # add to field list but don't add field if it's already there
                if FieldName.lower() not in map(lambda _: _.name.lower(), arcpy.Describe(pFClass).fields):
                    arcpy.AddField_management(pFClass, FieldName, "LONG")
                fields += [FieldName]
            return fields.index(FieldName)
        intFBPval = AddFBPfield(pFClass, "FBPvalue")
        intOntFBP = AddFBPfield(pFClass, "OntFBP")
        #''''''''''''''''''''''''''''''''''''''''''''''''''
        # Index
        #       1 - eFRI Ideal Match
        #       2 - National Fuels Model
        #       3 - eFRI Fair Match
        #       4 - eFRI unknown
        #       5 - eFRI bad match
        #''''''''''''''''''''''''''''''''''''''''''''''''''
        intOntIdx = AddFBPfield(pFClass, "OntIndex")
        # look up the name of the OBJECTID field for the feature
        oid_field = arcpy.Describe(pFClass).OIDFieldName
        fields.append(oid_field)
        # dictionary of indexes for the fields in the row
        idx = {}
        for f in fields:
            idx[f] = fields.index(f)
            # add in upper case so we can look based on that too
            idx[f.upper()] = fields.index(f)
        with arcpy.da.UpdateCursor(pFClass, fields) as cursor:
            for row in cursor:
                strPolyType = row[idx['POLYTYPE']]
                if strPolyType <> 'FOR':
                    row[intOntIdx] = 1
                    if strPolyType in ['DAL', 'GRS']:
                        row[intOntFBP] = 31                         # O1a
                    elif strPolyType in ['BSH']:
                        row[intOntFBP] = 105                        # Vegetated Non-Fuel
                    elif strPolyType == 'RCK':
                        row[intOntFBP] = 101                        # Non-Fuel
                    elif strPolyType == 'ISL':
                        row[intOntFBP] = 103                        # Unknown
                    elif strPolyType == 'WAT':
                        row[intOntFBP] = 102                        # Water
                    elif strPolyType in ['TMS', 'OMS', 'UCL']:
                        row[intOntFBP] = 104                        # Unclassified
                    else:
                        row[intOntFBP] = 103                        # Unknown
                else:
                    # it's a forest so try to classify it
                    dictSpecies = SPCcollection(row, fields, idx)
                    row[intOntFBP] = 1104                           # Default to Unclassified Forested
                    if len(dictSpecies.keys()) > 0:
                        row[intOntFBP] = SeekMatch(row, fields, idx, dictSpecies)
                        row[intOntIdx] = 5 if row[intOntFBP] > 2000 else 3 if row[intOntFBP] > 1000 else 1
                FBPvalue = row[intOntFBP] % 1000
                if FBPvalue == 103:
                    row[intOntIdx] = 4
                row[intFBPval] = FBPvalue         #Assign FBP value
                #''''''''''''''''''''''''''''''''''''''''
                # Update summary dictionary
                #''''''''''''''''''''''''''''''''''''''''
                pArea = row[idx["SHAPE_AREA"]] / 10000
                if (FBPvalue == 104 and strPolyType <> 'ISL'
                        and ((not row[idx['OSPCOMP']]) or 0 < len(row[idx['OSPCOMP']].strip()))):
                    tmp = {}
                    for i in xrange(len(fields)):
                        if i not in [intOntFBP, intFBPval, idx["SHAPE_AREA"], idx[oid_field], idx["POLYID"], intOntIdx]:
                            tmp[fields[i]] = row[i]
                    if VERBOSE:
                        print (" ".join([pFClass, str(row[idx[oid_field]]), str(FBPvalue), "{:.5f}".format(pArea)]))
                        print tmp
                if FBPvalue >= 600 and FBPvalue < 700:
                    FBPvalue = 600
                elif FBPvalue >= 900 and FBPvalue < 900:
                    FBPvalue = 900
                if dictSummary.has_key(FBPvalue):
                    pArea += dictSummary[FBPvalue]
                dictSummary[FBPvalue] = pArea
                cursor.updateRow(row)
        for f, v in sorted(dictSummary.iteritems()):
            print (" ".join([pFClass, str(f), "{:.5f}".format(v)]))
        CompletedLayers += 1
    print (' - '.join(["Done", str(len(colFRILayers)), "Layers", str(CompletedLayers), "Converted"]))

if __name__ == '__main__':
    GDBPath = r'C:\FireGUARD\data\GIS\intermediate\fuels\eFRI_LIO.gdb'
    layers = None
    if len(sys.argv) > 1:
        layers = sys.argv[1].split(',')
    FRI2FBP2016(GDBPath, layers)
