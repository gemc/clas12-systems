#pragma once

// c++
#include <array>
#include <vector>


struct FTHODOConstants {
    static constexpr int NSECTOR = 8;
    static constexpr int NLAYER = 2;

    using ChannelValues = std::array<std::array<std::vector<double>, NLAYER>, NSECTOR>;
    using ChannelStatus = std::array<std::array<std::vector<int>, NLAYER>, NSECTOR>;

    ChannelStatus status;
    ChannelValues pedestal;
    ChannelValues pedestal_rms;
    ChannelValues gain_pc;
    ChannelValues gain_mv;
    ChannelValues npe_threshold;
    ChannelValues mips_charge;
    ChannelValues mips_energy;
    ChannelValues time_offset;
    ChannelValues time_rms;

    double ns_per_sample = 0.0;
    double fadc_input_impedance = 50.0;
    double fadc_lsb = 0.4884;
};
