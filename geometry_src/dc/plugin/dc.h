#pragma once


// gdynamic
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// dc plugin
#include "dc_constants.h"

// c++
#include <string>


class DC_digitization : public GDynamicDigitization
{
public:
	/// Use "dc" as the logger channel so verbosity.dc controls this plugin independently
	/// of the global gdigitization verbosity.
	explicit DC_digitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
		log = std::make_shared<GLogger>(g, "DC_digitization", "dc");
	}


	bool defineReadoutSpecsImpl() override;

	[[nodiscard]] std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
	    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) override;

	bool loadConstantsImpl(int runno, std::string const& variation) override;


	// bool loadTTImpl([[maybe_unused]] int runno, [[maybe_unused]] std::string const& variation) override;


	// [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, [[maybe_unused]] size_t hitn) override;

	DCConstants dcc;

private:

	/// Translation table created by loadTTImpl().
	// std::shared_ptr<GTranslationTable> translationTable;
};
