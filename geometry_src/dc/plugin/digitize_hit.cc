// dc plugin
#include "dc.h"

// gemc
#include <gemc/gfields/gmagneto.h>

// geant4
#include "G4ThreeVector.hh"
#include "Randomize.hh"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>
#include <CLHEP/Units/PhysicalConstants.h>
#include <CLHEP/Random/RandGauss.h>

// c++
#include <cmath>
#include <vector>


namespace {

// Centre of a sense wire in the superlayer corner-based local frame (origin at first guard wire).
// layer and wire are 1-based; dlayer and dwire are the full wire-to-wire pitches.
G4ThreeVector dc_wire_position(int layer, int wire, double dlayer, double dwire) {
    return G4ThreeVector(0.0,
                         dwire * (static_cast<double>(wire) + 0.5 * (layer % 2)),
                         dlayer * static_cast<double>(layer));
}

bool valid_dc_identity(int sector, int superlayer, int layer, int wire) {
    return sector >= 1 && sector <= 6 &&
           superlayer >= 1 && superlayer <= 6 &&
           layer >= 1 && layer <= DCConstants::NLAYERS &&
           wire >= 1 && wire <= DCConstants::NWIRES;
}

} // namespace


// Ported from dc_HitProcess::calc_Time in clas12Tags.
// Returns the drift time [ns] for distance x [cm] using the polynomial parameterisation.
// bfield is in Tesla; with bfield=0 the B-field correction vanishes.
double DC_digitization::calc_Time(double x, double dmax, double tmax, double alpha,
                                   double bfield, int sec, int sl) const {
    using namespace CLHEP;
    if (x > dmax) x = dmax;

    const double R       = dcc.R[sec][sl];
    const double cos30a  = std::cos((30.0 - alpha) * deg);
    const double dmaxA   = dmax * cos30a;
    const double xhatA   = x / dmaxA;
    const double rcap    = R * dmax;
    const double delt    = tmax - dmax / dcc.v0[sec][sl];
    const double delv    = 1.0 / dcc.vmid[sec][sl] - 1.0 / dcc.v0[sec][sl];

    double c = (3.0 * delv / (R * dmax)
                + 12.0 * R * R * delt / (2.0 * (1.0 - 2.0 * R) * dmax * dmax));
    c /= (4.0 - (1.0 - 6.0 * R * R) / (1.0 - 2.0 * R));
    const double b = delv / (rcap * rcap) - 4.0 * c / (3.0 * rcap);
    const double d = 1.0 / dcc.v0[sec][sl];
    const double a = (tmax - b * dmaxA * dmaxA * dmaxA - c * dmaxA * dmaxA - d * dmaxA)
                   / (dmaxA * dmaxA * dmaxA * dmaxA);

    double time = a * x * x * x * x + b * x * x * x + c * x * x + d * x;

    time += dcc.delta_bfield_coefficient[sec][sl] * bfield * bfield * tmax
          * (dcc.deltatime_bfield_par1[sec][sl] * xhatA
           + dcc.deltatime_bfield_par2[sec][sl] * xhatA * xhatA
           + dcc.deltatime_bfield_par3[sec][sl] * xhatA * xhatA * xhatA
           + dcc.deltatime_bfield_par4[sec][sl] * xhatA * xhatA * xhatA * xhatA);
    return time;
}


// Ported from dc_HitProcess::calc_TimeBeta in clas12Tags.
// Returns the beta-dependent time walk correction [ns].
double DC_digitization::calc_TimeBeta(double x, double beta, int sec, int sl) const {
    const double b3 = std::pow(beta * beta * dcc.distbeta[sec][sl], 3);
    return (0.5 * b3 * x / (b3 + x * x * x)) / dcc.v0[sec][sl];
}


// Ported from dc_HitProcess::doca_smearing in clas12Tags.
// Returns the Gaussian sigma of the time smearing [ns] at fractional distance x.
// beta is kept in the signature for API parity with the original but is not used.
double DC_digitization::doca_smearing(double x, [[maybe_unused]] double beta, int sec, int sl) const {
    using namespace CLHEP;
    if (x > 1.0) x = 1.0;
    double smear = (dcc.smearP0[sec][sl]
                  + dcc.smearP1[sec][sl] * x
                  + dcc.smearP2[sec][sl] * x * x
                  + dcc.smearP3[sec][sl] * x * x * x
                  + dcc.smearP4[sec][sl] * x * x * x * x) * cm;
    return smear / (dcc.v0[sec][sl] * cm / ns);
}


// Ported from dc_HitProcess::integrateDgt in clas12Tags.
// Computes the smeared TDC time for the fastest hit on the primary track and returns a
// GDigitizedData with sector, global layer (1-36), component (wire), TDC_order, and TDC_TDC.
// Returns nullptr when the hit falls outside valid layer/wire bounds or is rejected by the
// distance-dependent inefficiency model.
std::unique_ptr<GDigitizedData> DC_digitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    // Identity (1-based)
    const auto& gid        = ghit->getGID();
    if (gid.size() < 4 || ghit->nsteps() == 0) return nullptr;

    const int   sector     = gid[0].getValue();
    const int   superlayer = gid[1].getValue();
    const int   layer      = gid[2].getValue();
    const int   nwire      = gid[3].getValue();
    const int   SECI       = sector     - 1; // 0-based
    const int   SLI        = superlayer - 1;
    const int   LAYI       = layer      - 1;

    if (!valid_dc_identity(sector, superlayer, layer, nwire)) return nullptr;

    // Detector shape parameters from the G4Trap volume
    const auto&  dims        = ghit->getDetectorDimensions();
    if (dims.size() <= 5) return nullptr;

    const double zlength     = dims[0]; // half-thickness along the wire-depth axis
    const double ylength     = dims[3]; // semi-height along the wire-number axis
    const double xlength_low = dims[4]; // half-base at -ylength
    const double xlength_hi  = dims[5]; // half-base at +ylength

    // Sense-wire pitch in the superlayer local frame
    const double deltaz = 2.0 * zlength / static_cast<double>(DCConstants::NLAYERS + 1);
    const double deltay = 2.0 * ylength / static_cast<double>(DCConstants::NWIRES  + 1);

    // Wire centre in the corner-based local frame; Region 3 (SL 5-6) carries mini-stagger
    G4ThreeVector wirePos = dc_wire_position(LAYI + 1, nwire, deltaz, deltay);
    if (SLI > 3) wirePos.setY(wirePos.y() + dcc.miniStagger[LAYI]);

    // Wire half-length at the wire's y position (G4Trap width varies linearly with y)
    const double WIRE_DX = xlength_low + (xlength_hi - xlength_low) * wirePos.y() / (2.0 * ylength);

    // Per-step vectors
    const auto   tids   = ghit->getTids();
    const auto   times  = ghit->getTimes();
    const auto   edeps  = ghit->getEdeps();
    const auto   pos    = ghit->getGlobalPositions();
    const auto   Lpos   = ghit->getLocalPositions();
    const auto   mom    = ghit->getMomenta();
    const auto   trackE = ghit->getTrackEs();
    const size_t nsteps = ghit->nsteps();

    if (tids.size() < nsteps || times.size() < nsteps || edeps.size() < nsteps ||
        pos.size() < nsteps || Lpos.size() < nsteps || mom.size() < nsteps || trackE.size() < nsteps)
        return nullptr;

    // TDC jitter (same for every step in this hit)
    double tdc_jitter = 0.0;
    if (dcc.jitter_cycles != 0)
        tdc_jitter = dcc.jitter_period
                   * static_cast<double>((0 + dcc.jitter_phase) % dcc.jitter_cycles);

    // --- Loop 1: find the step with the smallest signal arrival time ---
    // trackIds: primary track (must deposit energy above threshold)
    // trackIdw: fallback — fastest track regardless of threshold
    int    trackIds     = -1;
    int    trackIdw     = -1;
    double minTime      = 1.0e10;
    double hit_signal_t = 0.0;
    double prop_t       = 0.0;

    for (size_t s = 0; s < nsteps; s++) {
        const G4ThreeVector DOCA(0.0,
                                 Lpos[s].y() + ylength - wirePos.y(),
                                 Lpos[s].z() + zlength - wirePos.z());
        const double tprop  = (WIRE_DX + dcc.stbloc[SECI][SLI] * (Lpos[s].x() - wirePos.x()))
                            / dcc.vprop;
        // Propagation time is intentionally excluded from signal_t (GEMC2 TODO for future fix)
        const double signal = times[s] / ns + DOCA.mag() / (dcc.v0[SECI][SLI] * cm / ns);

        if (signal < minTime) {
            trackIdw     = tids[s];
            minTime      = signal;
            hit_signal_t = times[s] / ns;
            prop_t       = tprop / ns;
            if (edeps[s] >= dcc.dcThreshold * eV)
                trackIds = tids[s];
        }
    }
    if (trackIds == -1) trackIds = trackIdw;

    // --- Loop 2: find the step with the smallest DOCA on the primary track to compute alpha ---
    double alpha    = 0.0;
    double doca_val = 1.0e10;
    double thisMgnf = 0.0;
    double beta_p   = 0.0;

    // sl_sign replicates the GEMC2 loop that writes to sl_sign on every iteration:
    // only the last iteration (i=2, SLI==5) can leave sl_sign=-1; all other SLI yield 1.
    const int    sl_sign        = (SLI == 5) ? -1 : 1;
    const double rotate_to_sec  = static_cast<double>(-60 * SECI) * deg;
    const double rotate_to_wire = 6.0 * sl_sign * deg;
    const double const1         = std::cos(6.0 * deg);
    const double const2         = sl_sign * std::sin(6.0 * deg);

    if (!magneticFieldChecked) {
        magneticField = GMagneto::initialize_magnetic_field(gopts, dcc.fieldPolarity, log);
        magneticFieldChecked = true;
    }

    for (size_t s = 0; s < nsteps; s++) {
        const G4ThreeVector DOCA(0.0,
                                 Lpos[s].y() + ylength - wirePos.y(),
                                 Lpos[s].z() + zlength - wirePos.z());
        if (DOCA.mag() <= doca_val && tids[s] == trackIds) {
            G4ThreeVector rv(mom[s]);
            rv.rotateZ(rotate_to_sec);
            rv.rotateY(-25.0 * deg);
            rv.rotateZ(rotate_to_wire);
            alpha = std::asin((const1 * rv.x() + const2 * rv.y()) / rv.mag()) / deg;

            thisMgnf = GMagneto::magnetic_field_magnitude_tesla(magneticField, pos[s]);

            // B-field isochrone-twist correction; theta0=0 when no global field is configured.
            const double theta0 = std::acos(1.0 - 0.02 * thisMgnf) / deg;
            alpha -= dcc.fieldPolarity * theta0;

            // Reduce alpha to the symmetric [0, 30] deg range (Mac's reduced alpha, VZ)
            double ralpha = std::fabs(alpha * deg);
            while (ralpha > pi / 3.0) ralpha -= pi / 3.0;
            if (ralpha > pi / 6.0) ralpha = pi / 3.0 - ralpha;
            alpha = ralpha / deg;

            doca_val = DOCA.mag();
            beta_p   = mom[s].mag() / trackE[s];
        }
    }

    // Fractional distance from the wire, normalised to the half-cell size
    const double X = (doca_val / cm) / (2.0 * dcc.dLayer[SLI]);

    // Distance-dependent fractional inefficiency
    const double ddEff =
        dcc.iScale[SECI][SLI] *
        (dcc.P1[SECI][SLI] / std::pow(X * X + dcc.P2[SECI][SLI], 2.0) +
         dcc.P3[SECI][SLI] / std::pow((1.0 - X) + dcc.P4[SECI][SLI], 2.0));
    const double rnd = G4UniformRand();

    // Drift time from the distance-time function plus the beta-dependent time walk
    const double unsmeared = calc_Time(doca_val / cm,
                                        dcc.dmaxsuperlayer[SLI],
                                        dcc.tmaxsuperlayer[SECI][SLI],
                                        alpha, thisMgnf, SECI, SLI)
                           + calc_TimeBeta(doca_val / cm, beta_p, SECI, SLI);

    // Gaussian smearing from the DOCA resolution parameterisation
    const double dt_sigma  = doca_smearing(X, beta_p, SECI, SLI);
    const double dt_random = std::fabs(CLHEP::RandGauss::shoot(0.0, dt_sigma));

    // Final smeared TDC time [ns]: drift + smearing + event time + propagation + T0 + jitter
    const double smeared_time = unsmeared + dt_random + hit_signal_t + prop_t
                              + dcc.get_T0(SECI, SLI, LAYI, nwire) + tdc_jitter;

    // Reject the hit based on the distance-dependent inefficiency model
    if (rnd < ddEff || X > 1.0) return nullptr;

    auto digitizedData = std::make_unique<GDigitizedData>(gopts, ghit);
    digitizedData->includeVariable("hitn",      static_cast<int>(hitn));
    digitizedData->includeVariable("sector",    sector);
    digitizedData->includeVariable("layer",     SLI * 6 + layer); // global layer 1-36
    digitizedData->includeVariable("component", nwire);
    digitizedData->includeVariable("TDC_order", 0);
    digitizedData->includeVariable("TDC_TDC",   smeared_time);

    return digitizedData;
}
