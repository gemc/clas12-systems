#pragma once

struct LTCCConstants {
    static constexpr int NSECT = 6;
    static constexpr int NSIDE = 2;
    static constexpr int NSEGM = 18;

    double speMean[NSECT][NSIDE][NSEGM] = {};
    double speSigma[NSECT][NSIDE][NSEGM] = {};
    double timeOffset[NSECT][NSIDE][NSEGM] = {};
    double timeRes[NSECT][NSIDE][NSEGM] = {};
    double tdcConv[NSECT][NSIDE][NSEGM] = {};
};
