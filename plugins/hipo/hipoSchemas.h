#pragma once

// hipo
#include "hipo4/bank.h"
#include "hipo4/writer.h"

// c++
#include <map>
#include <string>

/**
 * \class HipoSchemas
 * \brief Owns every CLAS12 HIPO4 schema object and the map used to register
 *        them with the writer before the output file is opened.
 *
 * Schema names, group/item ids, and column definitions mirror the official
 * CLAS12 bank definitions at
 * https://github.com/JeffersonLab/clas12-offline-software/tree/development/etc/bankdefs/hipo4
 */
class HipoSchemas
{
public:
    HipoSchemas();

    // run / generator banks
    hipo::schema runConfigSchema;
    hipo::schema trueInfoSchema;
    hipo::schema geantParticle;
    hipo::schema mcEventHeader;

    // flux
    hipo::schema fluxADCSchema;

    // detector banks
    hipo::schema alertAhdcADCSchema;
    hipo::schema alertAhdcTDCSchema;
    hipo::schema alertAhdcWFSchema;
    hipo::schema alertAtofTDCSchema;
    hipo::schema bandADCSchema;
    hipo::schema bandTDCSchema;
    hipo::schema bmtADCSchema;
    hipo::schema bstADCSchema;
    hipo::schema cndADCSchema;
    hipo::schema cndTDCSchema;
    hipo::schema ctofADCSchema;
    hipo::schema ctofTDCSchema;
    hipo::schema dcTDCSchema;
    hipo::schema dcDOCASchema;
    hipo::schema ecalADCSchema;
    hipo::schema ecalTDCSchema;
    hipo::schema fmtADCSchema;
    hipo::schema ftcalADCSchema;
    hipo::schema fthodoADCSchema;
    hipo::schema ftofADCSchema;
    hipo::schema ftofTDCSchema;
    hipo::schema ftrkTDCSchema;
    hipo::schema htccADCSchema;
    hipo::schema htccTDCSchema;
    hipo::schema ltccADCSchema;
    hipo::schema ltccTDCSchema;
    hipo::schema rfADCSchema;
    hipo::schema rfTDCSchema;
    hipo::schema richTDCSchema;
    hipo::schema rtpcADCSchema;
    hipo::schema rtpcPOSSchema;
    hipo::schema helADCSchema;
    hipo::schema helFLIPSchema;
    hipo::schema helONLINESchema;
    hipo::schema urwtADCSchema;
    hipo::schema recoilADCSchema;
    hipo::schema rasterADCSchema;
    hipo::schema mucalADCSchema;
    hipo::schema muvtADCSchema;
    hipo::schema murtADCSchema;
    hipo::schema murhADCSchema;
    hipo::schema rawADCSchema;
    hipo::schema rawTDCSchema;
    hipo::schema rawSCALERSchema;
    hipo::schema rawVTPSchema;
    hipo::schema rawEPICSSchema;
    hipo::schema emptySchema;

    // keyed by DETECTOR::type (e.g. "DC::tdc") – registered with writer before file open
    std::map<std::string, hipo::schema> schemasToLoad;

    // Returns the schema for the given detector name and type (0=adc, 1=tdc, 2=wf).
    hipo::schema getSchema(const std::string& detectorName, int type) const;

private:
    bool non_registered_detectors(const std::string& detectorName, int type) const;
};
