#include "histos_compare.h"

#include "TAxis.h"
#include "TH1.h"
#include "TH2.h"

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace {

bool same_axis(const TAxis *a, const TAxis *b)
{
    if (a == nullptr || b == nullptr) {
        return false;
    }

    return a->GetNbins() == b->GetNbins() &&
           std::abs(a->GetXmin() - b->GetXmin()) <= 1.0e-12 &&
           std::abs(a->GetXmax() - b->GetXmax()) <= 1.0e-12;
}

double rel_integral_difference(double a, double b)
{
    const double scale = std::max({std::abs(a), std::abs(b), 1.0});
    return std::abs(a - b) / scale;
}

double median_of(std::vector<double> values)
{
    if (values.empty()) {
        return 0.0;
    }

    std::sort(values.begin(), values.end());
    const std::size_t mid = values.size() / 2;
    if (values.size() % 2 == 0) {
        return 0.5 * (values[mid - 1] + values[mid]);
    }
    return values[mid];
}

// Raw occupancy statistics used to flag whether a histogram has enough entries
// for the chi2 comparison to be statistically meaningful. Computed on the
// unscaled histogram, before any event-count normalization.
struct HistoStats {
    double entries = 0.0;
    int occupied_bins = 0;
    double median_occupied = 0.0;
};

HistoStats th1_stats(const TH1 &histo)
{
    std::vector<double> occupied;
    double entries = 0.0;
    for (int xbin = 1; xbin <= histo.GetNbinsX(); ++xbin) {
        const double content = histo.GetBinContent(xbin);
        entries += content;
        if (content > 0.0) {
            occupied.push_back(content);
        }
    }

    HistoStats stats;
    stats.entries = entries;
    stats.occupied_bins = static_cast<int>(occupied.size());
    stats.median_occupied = median_of(std::move(occupied));
    return stats;
}

HistoStats th2_stats(const TH2 &histo)
{
    std::vector<double> occupied;
    double entries = 0.0;
    for (int xbin = 1; xbin <= histo.GetNbinsX(); ++xbin) {
        for (int ybin = 1; ybin <= histo.GetNbinsY(); ++ybin) {
            const double content = histo.GetBinContent(xbin, ybin);
            entries += content;
            if (content > 0.0) {
                occupied.push_back(content);
            }
        }
    }

    HistoStats stats;
    stats.entries = entries;
    stats.occupied_bins = static_cast<int>(occupied.size());
    stats.median_occupied = median_of(std::move(occupied));
    return stats;
}

void apply_stats(HistoCompareResult &result, const HistoStats &a, const HistoStats &b)
{
    result.entries_a = a.entries;
    result.entries_b = b.entries;
    result.occupied_bins_a = a.occupied_bins;
    result.occupied_bins_b = b.occupied_bins;
    result.median_per_bin_a = a.median_occupied;
    result.median_per_bin_b = b.median_occupied;
}

std::string fail_reason(double chi2_ndf, double rel_integral_diff, double max_abs_bin_diff,
                        const HistoCompareOptions &options)
{
    std::ostringstream reason;
    bool first = true;

    if (chi2_ndf > options.max_chi2_ndf) {
        reason << "chi2/ndf " << chi2_ndf << " > " << options.max_chi2_ndf;
        first = false;
    }
    if (rel_integral_diff > options.max_rel_integral_diff) {
        if (!first) {
            reason << "; ";
        }
        reason << "relative integral diff " << rel_integral_diff << " > "
               << options.max_rel_integral_diff;
        first = false;
    }
    if (options.max_abs_bin_diff >= 0.0 && max_abs_bin_diff > options.max_abs_bin_diff) {
        if (!first) {
            reason << "; ";
        }
        reason << "max bin diff " << max_abs_bin_diff << " > " << options.max_abs_bin_diff;
    }

    return reason.str();
}

void compare_bin(double value_a, double value_b, double error_a, double error_b, double scale_a,
                 double scale_b, double &chi2, double &max_abs_bin_diff, int &bins_compared)
{
    const double scaled_a = value_a * scale_a;
    const double scaled_b = value_b * scale_b;
    const double scaled_error_a = error_a * scale_a;
    const double scaled_error_b = error_b * scale_b;
    const double diff = scaled_a - scaled_b;

    // Prefer explicit ROOT bin errors when available. For DC z-vertex and occupancy histograms those errors are
    // event-level standard errors, so this keeps the diagnostic test aligned with the plotted uncertainties.
    double variance = scaled_error_a * scaled_error_a + scaled_error_b * scaled_error_b;
    if (variance <= 0.0) {
        // Fallback for histograms that have no stored errors: approximate two independent Poisson counts.
        variance = std::max(std::abs(scaled_a) + std::abs(scaled_b), 1.0);
    }

    chi2 += diff * diff / variance;
    max_abs_bin_diff = std::max(max_abs_bin_diff, std::abs(diff));
    ++bins_compared;
}

void finish_result(HistoCompareResult &result, const HistoCompareOptions &options)
{
    result.chi2_ndf = result.bins_compared > 0 ? result.chi2_ndf / result.bins_compared : 0.0;
    result.rel_integral_diff = rel_integral_difference(result.integral_a, result.integral_b);
    result.reason = fail_reason(result.chi2_ndf, result.rel_integral_diff,
                                result.max_abs_bin_diff, options);

    if (options.min_entries_per_bin >= 0.0) {
        const double worst_median = std::min(result.median_per_bin_a, result.median_per_bin_b);
        if (worst_median < options.min_entries_per_bin) {
            std::ostringstream reason;
            if (!result.reason.empty()) {
                reason << result.reason << "; ";
            }
            reason << "insufficient statistics: median entries/occupied bin " << worst_median
                   << " < " << options.min_entries_per_bin;
            result.reason = reason.str();
        }
    }

    result.passed = result.reason.empty();
    if (result.passed) {
        result.reason = "within configured limits";
    }
}

} // namespace

HistoCompareResult compare_th1(const TH1 &a, const TH1 &b, const HistoCompareOptions &options)
{
    HistoCompareResult result;
    result.name = std::string(a.GetName()) + " vs " + b.GetName();

    if (!same_axis(a.GetXaxis(), b.GetXaxis())) {
        result.reason = "incompatible x axis binning";
        return result;
    }

    apply_stats(result, th1_stats(a), th1_stats(b));

    result.integral_a = a.Integral(1, a.GetNbinsX()) * options.scale_a;
    result.integral_b = b.Integral(1, b.GetNbinsX()) * options.scale_b;
    double chi2 = 0.0;

    for (int xbin = 1; xbin <= a.GetNbinsX(); ++xbin) {
        compare_bin(a.GetBinContent(xbin), b.GetBinContent(xbin), a.GetBinError(xbin),
                    b.GetBinError(xbin), options.scale_a, options.scale_b, chi2,
                    result.max_abs_bin_diff, result.bins_compared);
    }

    result.chi2_ndf = chi2;
    finish_result(result, options);
    return result;
}

HistoCompareResult compare_th2(const TH2 &a, const TH2 &b, const HistoCompareOptions &options)
{
    HistoCompareResult result;
    result.name = std::string(a.GetName()) + " vs " + b.GetName();

    if (!same_axis(a.GetXaxis(), b.GetXaxis()) || !same_axis(a.GetYaxis(), b.GetYaxis())) {
        result.reason = "incompatible x/y axis binning";
        return result;
    }

    apply_stats(result, th2_stats(a), th2_stats(b));

    result.integral_a = a.Integral(1, a.GetNbinsX(), 1, a.GetNbinsY()) * options.scale_a;
    result.integral_b = b.Integral(1, b.GetNbinsX(), 1, b.GetNbinsY()) * options.scale_b;
    double chi2 = 0.0;

    for (int xbin = 1; xbin <= a.GetNbinsX(); ++xbin) {
        for (int ybin = 1; ybin <= a.GetNbinsY(); ++ybin) {
            compare_bin(a.GetBinContent(xbin, ybin), b.GetBinContent(xbin, ybin),
                        a.GetBinError(xbin, ybin), b.GetBinError(xbin, ybin), options.scale_a,
                        options.scale_b, chi2, result.max_abs_bin_diff, result.bins_compared);
        }
    }

    result.chi2_ndf = chi2;
    finish_result(result, options);
    return result;
}

void print_compare_result(const HistoCompareResult &result, std::ostream &out)
{
    out << (result.passed ? "passed" : "failed") << "  " << result.name
        << "  chi2/ndf=" << std::setprecision(6) << result.chi2_ndf
        << "  rel_integral_diff=" << result.rel_integral_diff
        << "  max_bin_diff=" << result.max_abs_bin_diff
        << "  ndf=" << result.bins_compared
        << "  occ_bins=" << result.occupied_bins_a << "/" << result.occupied_bins_b
        << "  median_per_bin=" << result.median_per_bin_a << "/" << result.median_per_bin_b
        << "  (" << result.reason << ")\n";
}
