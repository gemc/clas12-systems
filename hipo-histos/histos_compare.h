#ifndef HIPO_HISTOS_HISTOS_COMPARE_H
#define HIPO_HISTOS_HISTOS_COMPARE_H

#include <iosfwd>
#include <string>

class TH1;
class TH2;

struct HistoCompareOptions {
    double max_chi2_ndf = 5.0;
    double max_rel_integral_diff = 0.05;
    double max_abs_bin_diff = -1.0;
    double min_entries_per_bin = -1.0;
    double scale_a = 1.0;
    double scale_b = 1.0;
};

struct HistoCompareResult {
    std::string name;
    bool passed = false;
    double chi2_ndf = 0.0;
    double integral_a = 0.0;
    double integral_b = 0.0;
    double rel_integral_diff = 0.0;
    double max_abs_bin_diff = 0.0;
    int bins_compared = 0;
    double entries_a = 0.0;
    double entries_b = 0.0;
    int occupied_bins_a = 0;
    int occupied_bins_b = 0;
    double median_per_bin_a = 0.0;
    double median_per_bin_b = 0.0;
    std::string reason;
};

HistoCompareResult compare_th1(const TH1 &a, const TH1 &b, const HistoCompareOptions &options);
HistoCompareResult compare_th2(const TH2 &a, const TH2 &b, const HistoCompareOptions &options);
void print_compare_result(const HistoCompareResult &result, std::ostream &out);

#endif
