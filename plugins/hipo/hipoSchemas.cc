// hipo plugin
#include "hipoSchemas.h"

// c++
#include <algorithm>
#include <string>

HipoSchemas::HipoSchemas() {

    // Schema constructor arguments: name, groupid (16-bit), itemid (8-bit).
    // IDs and column definitions mirror:
    //   https://github.com/JeffersonLab/clas12-offline-software/tree/development/etc/bankdefs/hipo4

    runConfigSchema = hipo::schema("RUN::config", 10000, 11);
    trueInfoSchema  = hipo::schema("MC::True",    40,    4);
    geantParticle   = hipo::schema("MC::Particle",40,    2);
    mcEventHeader   = hipo::schema("MC::Event",   40,    1);

    // flux
    fluxADCSchema = hipo::schema("FLUX::adc", 22200, 20);

    // detectors
    alertAhdcADCSchema  = hipo::schema("AHDC::adc",   22400, 11);
    alertAhdcTDCSchema  = hipo::schema("AHDC::tdc",   22400, 12);
    alertAhdcWFSchema   = hipo::schema("AHDC::wf",    22400, 10);
    alertAtofTDCSchema  = hipo::schema("ATOF::tdc",   22500, 12);
    bandADCSchema       = hipo::schema("BAND::adc",   22100, 11);
    bandTDCSchema       = hipo::schema("BAND::tdc",   22100, 12);
    bmtADCSchema        = hipo::schema("BMT::adc",    20100, 11);
    bstADCSchema        = hipo::schema("BST::adc",    20200, 11);
    cndADCSchema        = hipo::schema("CND::adc",    20300, 11);
    cndTDCSchema        = hipo::schema("CND::tdc",    20300, 12);
    ctofADCSchema       = hipo::schema("CTOF::adc",   20400, 11);
    ctofTDCSchema       = hipo::schema("CTOF::tdc",   20400, 12);
    dcTDCSchema         = hipo::schema("DC::tdc",     20600, 12);
    dcDOCASchema        = hipo::schema("DC::doca",    20600, 14);
    ecalADCSchema       = hipo::schema("ECAL::adc",   20700, 11);
    ecalTDCSchema       = hipo::schema("ECAL::tdc",   20700, 12);
    fmtADCSchema        = hipo::schema("FMT::adc",    20800, 11);
    ftcalADCSchema      = hipo::schema("FTCAL::adc",  21000, 11);
    fthodoADCSchema     = hipo::schema("FTHODO::adc", 21100, 11);
    ftrkTDCSchema       = hipo::schema("FTTRK::adc",  21300, 11);
    ftofADCSchema       = hipo::schema("FTOF::adc",   21200, 11);
    ftofTDCSchema       = hipo::schema("FTOF::tdc",   21200, 12);
    htccADCSchema       = hipo::schema("HTCC::adc",   21500, 11);
    htccTDCSchema       = hipo::schema("HTCC::tdc",   21500, 12);
    ltccADCSchema       = hipo::schema("LTCC::adc",   21600, 11);
    ltccTDCSchema       = hipo::schema("LTCC::tdc",   21600, 12);
    rfADCSchema         = hipo::schema("RF::adc",     21700, 11);
    rfTDCSchema         = hipo::schema("RF::tdc",     21700, 12);
    richTDCSchema       = hipo::schema("RICH::tdc",   21800, 12);
    rtpcADCSchema       = hipo::schema("RTPC::adc",   21900, 11);
    rtpcPOSSchema       = hipo::schema("RTPC::pos",   21900, 14);
    helADCSchema        = hipo::schema("HEL::adc",    22000, 11);
    helFLIPSchema       = hipo::schema("HEL::flip",   22000, 12);
    helONLINESchema     = hipo::schema("HEL::online", 22000, 13);
    urwtADCSchema       = hipo::schema("URWT::adc",   22300, 11);
    recoilADCSchema     = hipo::schema("RECOIL::adc", 22600, 11);
    rasterADCSchema     = hipo::schema("RASTER::adc", 22200, 11);
    mucalADCSchema      = hipo::schema("MUCAL::adc",  22800, 11);
    muvtADCSchema       = hipo::schema("MUVT::adc",   22900, 11);
    murtADCSchema       = hipo::schema("MURT::adc",   23000, 11);
    murhADCSchema       = hipo::schema("MURH::adc",   23100, 11);
    rawADCSchema        = hipo::schema("RAW::adc",    20000, 11);
    rawTDCSchema        = hipo::schema("RAW::tdc",    20000, 12);
    rawSCALERSchema     = hipo::schema("RAW::scaler", 20000, 13);
    rawVTPSchema        = hipo::schema("RAW::vtp",    20000, 14);
    rawEPICSSchema      = hipo::schema("RAW::epics",  20000, 15);

    // Column definitions.
    // Types: I=int, S=short, B=byte, F=float, D=double, L=long

    runConfigSchema.parse("run/I, event/I, unixtime/I, trigger/L, timestamp/L, type/B, mode/B, torus/F, solenoid/F");
    trueInfoSchema.parse(
        "detector/B, pid/I, mpid/I, tid/I, mtid/I, otid/I, trackE/F, totEdep/F, "
        "avgX/F, avgY/F, avgZ/F, avgLx/F, avgLy/F, avgLz/F, "
        "px/F, py/F, pz/F, vx/F, vy/F, vz/F, mvx/F, mvy/F, mvz/F, "
        "avgT/F, nsteps/I, procID/I, hitn/I");
    geantParticle.parse("pid/I, px/F, py/F, pz/F, vx/F, vy/F, vz/F, vt/F");
    mcEventHeader.parse(
        "npart/S, atarget/S, ztarget/S, ptarget/F, pbeam/F, "
        "btype/S, ebeam/F, targetid/S, processid/S, weight/F");

    fluxADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, amplitude/I, time/F, ped/S");

    alertAhdcADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S, integral/I, timestamp/L");
    alertAhdcTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I, ped/S");
    {
        std::string wf = "sector/B, layer/B, component/S, order/B, timestamp/L";
        for (int i = 1; i <= 30; ++i) wf += ", s" + std::to_string(i) + "/S";
        wf += ", time/I";
        alertAhdcWFSchema.parse(wf.c_str());
    }
    alertAtofTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I, ToT/I, timestamp/L, trigger/I");

    bandADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, amplitude/I, time/F, ped/S");
    bandTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    bmtADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S, integral/I, timestamp/L");
    bstADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S, timestamp/L");
    cndADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    cndTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    ctofADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    ctofTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    dcTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    dcDOCASchema.parse("sector/B, layer/B, component/S, order/B, doca/F, time/F");
    ecalADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    ecalTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    fmtADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S, integral/I, timestamp/L");
    ftcalADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    fthodoADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    ftrkTDCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S, integral/I, timestamp/L");
    ftofADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    ftofTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    htccADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    htccTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    ltccADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    ltccTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    rfADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    rfTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    richTDCSchema.parse("sector/B, layer/B, component/S, order/B, TDC/I");
    rtpcADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    rtpcPOSSchema.parse("step/I, time/F, energy/F, posx/F, posy/F, posz/F, phi/F, tid/F");
    helADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    helFLIPSchema.parse("run/I, event/I, timestamp/L, helicity/B, helicityRaw/B, pair/B, pattern/B, status/B");
    helONLINESchema.parse("helicity/B, helicityRaw/B");
    urwtADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    recoilADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    rasterADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    mucalADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    muvtADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    murtADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    murhADCSchema.parse("sector/B, layer/B, component/S, order/B, ADC/I, time/F, ped/S");
    rawADCSchema.parse("crate/B, slot/B, channel/S, order/B, ADC/I, time/F, ped/S");
    rawTDCSchema.parse("crate/B, slot/B, channel/S, order/B, TDC/I");
    rawSCALERSchema.parse("crate/B, slot/B, channel/S, helicity/B, quartet/B, value/L");
    rawVTPSchema.parse("crate/B, word/I");
    rawEPICSSchema.parse("json/B");
    emptySchema.parse("empty/B");

    schemasToLoad["RUN::config"]  = runConfigSchema;
    schemasToLoad["MC::True"]     = trueInfoSchema;
    schemasToLoad["MC::Particle"] = geantParticle;
    schemasToLoad["MC::Event"]    = mcEventHeader;
    schemasToLoad["FLUX::adc"]    = fluxADCSchema;

    schemasToLoad["AHDC::wf"]     = alertAhdcWFSchema;
    schemasToLoad["AHDC::tdc"]    = alertAhdcTDCSchema;
    schemasToLoad["ATOF::tdc"]    = alertAtofTDCSchema;
    schemasToLoad["BAND::adc"]    = bandADCSchema;
    schemasToLoad["BAND::tdc"]    = bandTDCSchema;
    schemasToLoad["BMT::adc"]     = bmtADCSchema;
    schemasToLoad["BST::adc"]     = bstADCSchema;
    schemasToLoad["CND::adc"]     = cndADCSchema;
    schemasToLoad["CND::tdc"]     = cndTDCSchema;
    schemasToLoad["CTOF::adc"]    = ctofADCSchema;
    schemasToLoad["CTOF::tdc"]    = ctofTDCSchema;
    schemasToLoad["DC::tdc"]      = dcTDCSchema;
    schemasToLoad["ECAL::adc"]    = ecalADCSchema;
    schemasToLoad["ECAL::tdc"]    = ecalTDCSchema;
    schemasToLoad["FMT::adc"]     = fmtADCSchema;
    schemasToLoad["FTCAL::adc"]   = ftcalADCSchema;
    schemasToLoad["FTHODO::adc"]  = fthodoADCSchema;
    schemasToLoad["FTTRK::adc"]   = ftrkTDCSchema;
    schemasToLoad["FTOF::adc"]    = ftofADCSchema;
    schemasToLoad["FTOF::tdc"]    = ftofTDCSchema;
    schemasToLoad["HTCC::adc"]    = htccADCSchema;
    schemasToLoad["HTCC::tdc"]    = htccTDCSchema;
    schemasToLoad["LTCC::adc"]    = ltccADCSchema;
    schemasToLoad["LTCC::tdc"]    = ltccTDCSchema;
    schemasToLoad["RICH::tdc"]    = richTDCSchema;
    schemasToLoad["RTPC::adc"]    = rtpcADCSchema;
    schemasToLoad["RTPC::pos"]    = rtpcPOSSchema;
    schemasToLoad["HEL::flip"]    = helFLIPSchema;
    schemasToLoad["RASTER::adc"]  = rasterADCSchema;
    schemasToLoad["URWT::adc"]    = urwtADCSchema;
    schemasToLoad["MUVT::adc"]    = muvtADCSchema;
    schemasToLoad["MUCAL::adc"]   = mucalADCSchema;
    schemasToLoad["MURT::adc"]    = murtADCSchema;
    schemasToLoad["MURH::adc"]    = murhADCSchema;
    schemasToLoad["RECOIL::adc"]  = recoilADCSchema;
}


hipo::schema HipoSchemas::getSchema(const std::string& detectorName, int type) const {
    const std::string typeStr = (type == 0) ? "adc" : (type == 1) ? "tdc" : "wf";

    std::string upper = detectorName;
    std::transform(upper.begin(), upper.end(), upper.begin(), ::toupper);
    std::string key = upper + "::" + typeStr;

    auto it = schemasToLoad.find(key);
    if (it != schemasToLoad.end()) return it->second;

    // Legacy aliases for ft subsystems
    if (detectorName == "ft_cal")  return ftcalADCSchema;
    if (detectorName == "ft_hodo") return fthodoADCSchema;
    if (detectorName == "ft_trk")  return ftrkTDCSchema;

    if (non_registered_detectors(detectorName, type)) {
        // Only warn for combinations that are genuinely unexpected.
    }
    return emptySchema;
}


bool HipoSchemas::non_registered_detectors(const std::string& name, int type) const {
    // Returns false (= suppress warning) for detector/type combos known to have no bank.
    if (type == 0) {
        if (name == "dc" || name == "rich" || name == "atof" || name == "ahdc") return false;
    }
    else if (type == 1) {
        if (name == "bmt" || name == "fmt" || name == "rtpc" || name == "bst" ||
            name == "urwt" || name == "muvt" || name == "murt" || name == "murh" ||
            name == "mucal" || name == "recoil" || name == "flux")
            return false;
    }
    else if (type == 2) {
        if (name == "atof" || name == "band" || name == "bmt" || name == "fmt" ||
            name == "dc"   || name == "bst"  || name == "cnd" || name == "ctof" ||
            name == "ecal" || name == "ftof"  || name == "ft_cal" || name == "ft_hodo" ||
            name == "ft_trk" || name == "htcc" || name == "ltcc"  || name == "rich" ||
            name == "rtpc" || name == "urwt"  || name == "mucal"  || name == "muvt" ||
            name == "murt" || name == "murh"  || name == "recoil" || name == "flux")
            return false;
    }
    return true;
}
