#pragma once


// gdynamic
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// geant4
#include "G4ThreeVector.hh"

// dc plugin
#include "dc_constants.h"

// c++
#include <memory>
#include <string>

class GField;

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


	bool loadTTImpl(int runno, std::string const& variation) override;

	[[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;
	[[nodiscard]] bool apply_efficiency_impl(GHit* ghit, GDigitizedData* digitizedData) override;
	[[nodiscard]] bool efficiencies_are_intrinsic_impl() const override { return true; }

	DCConstants dcc;

private:

	[[nodiscard]] double calc_Time(double x, double dmax, double tmax, double alpha,
	                               double bfield, int sec, int sl) const;
	[[nodiscard]] double calc_TimeBeta(double x, double beta, int sec, int sl) const;
	[[nodiscard]] double doca_smearing(double x, double beta, int sec, int sl) const;

	bool magneticFieldChecked = false;
	std::shared_ptr<GField> magneticField;

	// Transient digitization values used only by the post-digitization efficiency policy.
	// They are not written to output banks; they let apply_efficiency_impl() make the GEMC2
	// rejection decision without rerunning drift-time digitization.
	static constexpr const char* DC_FRACTIONAL_DOCA = "dc_fractional_doca";
	static constexpr const char* DC_INEFFICIENCY = "dc_inefficiency";
};
