#pragma once

// c++
#include <array>


struct FTCALConstants {
    static constexpr int NCHANNEL = 484;

    std::array<int, NCHANNEL> status{};

    std::array<double, NCHANNEL> pedestal{};
    std::array<double, NCHANNEL> pedestal_rms{};
    std::array<double, NCHANNEL> noise{};
    std::array<double, NCHANNEL> noise_rms{};
    std::array<double, NCHANNEL> threshold{};

    std::array<double, NCHANNEL> mips_charge{};
    std::array<double, NCHANNEL> mips_energy{};
    std::array<double, NCHANNEL> fadc_to_charge{};
    std::array<double, NCHANNEL> preamp_gain{};
    std::array<double, NCHANNEL> apd_gain{};

    std::array<double, NCHANNEL> time_offset{};
    std::array<double, NCHANNEL> time_rms{};

    double preamp_input_noise = 5500.0;
    double apd_noise = 0.0033;
    double light_speed = 0.0;
};
