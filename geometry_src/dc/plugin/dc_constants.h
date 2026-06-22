#pragma once

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

// All calibration and geometry constants loaded from CCDB for the DC digitization plugin.
// Fields map 1-to-1 to the clas12Tags dcConstants struct; indices are always 0-based.
struct DCConstants {

    static constexpr int NWIRES  = 112;
    static constexpr int NLAYERS = 6;

    double dcThreshold = 50;  // eV

    // -- efficiency parameters [sector][superlayer] (/calibration/dc/signal_generation/inefficiency)
    double iScale[6][6]{};
    double P1[6][6]{}, P2[6][6]{}, P3[6][6]{}, P4[6][6]{};

    // -- smearing parameters [sector][superlayer] (/calibration/dc/signal_generation/doca_smearing)
    double smearP0[6][6]{}, smearP1[6][6]{}, smearP2[6][6]{}, smearP3[6][6]{}, smearP4[6][6]{};

    // -- time-to-distance parameters [sector][superlayer] (/calibration/dc/v2/t2d_pressure)
    double v0[6][6]{};
    double vmid[6][6]{};
    double tmaxsuperlayer[6][6]{};
    double distbeta[6][6]{};
    double R[6][6]{};
    double delta_bfield_coefficient[6][6]{};
    double deltatime_bfield_par1[6][6]{}, deltatime_bfield_par2[6][6]{};
    double deltatime_bfield_par3[6][6]{}, deltatime_bfield_par4[6][6]{};

    // -- DC core geometry (/geometry/dc/superlayer)
    double dLayer[6]{};         // ~cell size in each superlayer
    double dmaxsuperlayer[6]{}; // 2 * dLayer

    // -- mini-stagger offsets per layer: +0.300 mm on odd layers, -0.300 mm on even layers
    double miniStagger[6]{};

    // -- wire readout side: -1=left, +1=right [sector][superlayer] (hardcoded, matches reconstruction)
    int stbloc[6][6]{};

    // -- signal propagation speed along the wire (hardcoded, matches reconstruction)
    double vprop = 29.97924580 * 0.7 * CLHEP::cm / CLHEP::ns;

    // -- torus field polarity used by the alpha isochrone-twist correction
    double fieldPolarity = 1.0;

    // -- T0 corrections [sector][superlayer][slot][cable] (/calibration/dc/v2/t0)
    double T0Correction[6][6][7][6]{};

    // -- TDC jitter (/calibration/dc/time_jitter)
    double jitter_period = 0;
    int    jitter_phase  = 0;
    int    jitter_cycles = 0;

    // Cable-ID lookup table [layer][local-wire-in-slot] (16 wires per slot, 7 slots per layer).
    // Maps a 0-based local wire index within its slot to a 1-based cable number.
    int CableID[6][16] = {
        {1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6}, // Layer 1
        {1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6}, // Layer 2
        {1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6}, // Layer 3
        {1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6}, // Layer 4
        {1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6}, // Layer 5
        {1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 6}, // Layer 6
    };

    // Returns the T0 correction (ns) for a given 0-based sector/superlayer/layer and 1-based wire.
    double get_T0(int sectorI, int superlayerI, int layerI, int nwire) const {
        int slot        = ((nwire - 1) / 16);
        int localWireI  = ((nwire - 1) % 16);
        int cable       = CableID[layerI][localWireI] - 1;
        return T0Correction[sectorI][superlayerI][slot][cable];
    }
};
