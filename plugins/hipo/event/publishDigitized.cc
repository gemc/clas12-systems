// hipo plugin
#include "gstreamerHIPOFactory.h"

// gemc
#include "gemc/ghit/ghit.h"   // getIdentityMap

// hipo
#include "hipo4/bank.h"

bool GStreamerHIPOFactory::publishEventDigitizedDataImpl(
    const std::string&                        detectorName,
    const std::vector<const GDigitizedData*>& digitizedData) {

    if (digitizedData.empty()) return true;

    const int nHits = static_cast<int>(digitizedData.size());

    // Determine which bank types are present by inspecting the first hit's variables.
    // Convention used by digitization plugins:
    //   "ADC_" prefix  →  ADC bank
    //   "TDC_" prefix  →  TDC bank
    //   "WF_"  prefix  →  WF bank
    const auto& firstIntVars = digitizedData[0]->getIntObservablesMap(0);
    const auto& firstDblVars = digitizedData[0]->getDblObservablesMap(0);

    bool hasADC = false;
    bool hasTDC = false;
    bool hasWF  = false;

    for (const auto& [name, _] : firstIntVars) {
        if (name.rfind("ADC_", 0) == 0) hasADC = true;
        if (name.rfind("TDC_", 0) == 0) hasTDC = true;
        if (name.rfind("WF_",  0) == 0) hasWF  = true;
    }
    for (const auto& [name, _] : firstDblVars) {
        if (name.rfind("ADC_", 0) == 0) hasADC = true;
        if (name.rfind("TDC_", 0) == 0) hasTDC = true;
        if (name.rfind("WF_",  0) == 0) hasWF  = true;
    }

    hipo::schema adcSchema = schemas->getSchema(detectorName, 0);
    hipo::schema tdcSchema = schemas->getSchema(detectorName, 1);
    hipo::schema wfSchema  = schemas->getSchema(detectorName, 2);

    // Suppress bank if the schema is empty (detector has no ADC/TDC/WF).
    if (adcSchema.getEntryName(0) == "empty") hasADC = false;
    if (tdcSchema.getEntryName(0) == "empty") hasTDC = false;
    if (wfSchema.getEntryName(0)  == "empty") hasWF  = false;

    if (!hasADC && !hasTDC && !hasWF) return true;

    hipo::bank adcBank(adcSchema, nHits);
    hipo::bank tdcBank(tdcSchema, nHits);
    hipo::bank wfBank(wfSchema,   nHits);

    for (int nh = 0; nh < nHits; ++nh) {
        const auto* hit    = digitizedData[nh];
        auto identityMap   = getIdentityMap(hit->getIdentity());
        auto intVars       = hit->getIntObservablesMap(0);
        auto dblVars       = hit->getDblObservablesMap(0);

        auto putIntColumn = [&](hipo::bank& bank, const std::string& col, int val) {
            if (!bank.getSchema().exists(col.c_str())) return;

            switch (bank.getSchema().getEntryType(col.c_str())) {
            case hipo::kByte:
                bank.putByte(col.c_str(), nh, static_cast<int8_t>(val));
                break;
            case hipo::kShort:
                bank.putShort(col.c_str(), nh, static_cast<int16_t>(val));
                break;
            case hipo::kInt:
                bank.putInt(col.c_str(), nh, val);
                break;
            case hipo::kLong:
                bank.putLong(col.c_str(), nh, static_cast<int64_t>(val));
                break;
            default:
                break;
            }
        };

        auto putFloatColumn = [&](hipo::bank& bank, const std::string& col, double val) {
            if (!bank.getSchema().exists(col.c_str())) return;

            switch (bank.getSchema().getEntryType(col.c_str())) {
            case hipo::kByte:
                bank.putByte(col.c_str(), nh, static_cast<int8_t>(val));
                break;
            case hipo::kShort:
                bank.putShort(col.c_str(), nh, static_cast<int16_t>(val));
                break;
            case hipo::kInt:
                bank.putInt(col.c_str(), nh, static_cast<int32_t>(val));
                break;
            case hipo::kFloat:
                bank.putFloat(col.c_str(), nh, static_cast<float>(val));
                break;
            case hipo::kDouble:
                bank.putDouble(col.c_str(), nh, val);
                break;
            case hipo::kLong:
                bank.putLong(col.c_str(), nh, static_cast<int64_t>(val));
                break;
            default:
                break;
            }
        };

        // Touchable identities are defaults only. Detector digitization code may publish output
        // variables with the same bank column names but different meanings, such as DC global
        // layer 1..36 versus the touchable's local layer 1..6.
        auto putIdentityDefaults = [&](hipo::bank& bank) {
            for (const auto& [idName, idVal] : identityMap) {
                putIntColumn(bank, idName, idVal);
            }
        };

        auto fillBank = [&](hipo::bank& bank, const std::string& prefix) {
            putIdentityDefaults(bank);
            const std::size_t prefixLen = prefix.size();

            for (const auto& [name, val] : intVars) {
                if (bank.getSchema().exists(name.c_str())) {
                    putIntColumn(bank, name, val);
                    continue;
                }
                if (name.rfind(prefix, 0) == 0) {
                    std::string col = name.substr(prefixLen);
                    putIntColumn(bank, col, val);
                }
            }
            for (const auto& [name, val] : dblVars) {
                if (bank.getSchema().exists(name.c_str())) {
                    putFloatColumn(bank, name, val);
                    continue;
                }
                if (name.rfind(prefix, 0) == 0) {
                    std::string col = name.substr(prefixLen);
                    putFloatColumn(bank, col, val);
                }
            }
        };

        if (hasADC) fillBank(adcBank, "ADC_");
        if (hasTDC) fillBank(tdcBank, "TDC_");
        if (hasWF)  fillBank(wfBank,  "WF_");
    }

    if (hasADC) outEvent->addStructure(adcBank);
    if (hasTDC) outEvent->addStructure(tdcBank);
    if (hasWF)  outEvent->addStructure(wfBank);

    log->info(2, FUNCTION_NAME,
              detectorName,
              ": ADC=", hasADC, " TDC=", hasTDC, " WF=", hasWF,
              " hits=", nHits);
    return true;
}
