#include "common.h"

#include "TCanvas.h"
#include "TColor.h"
#include "TFile.h"
#include "TH1.h"
#include "TH2.h"
#include "TLegend.h"
#include "TLatex.h"
#include "TPad.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TText.h"

#include <algorithm>
#include <cctype>
#include <filesystem>
#include <memory>
#include <stdexcept>

namespace {

double max_bin_content_with_error(const TH1 *histo)
{
    if (histo == nullptr) {
        return 0.0;
    }

    double ymax = 0.0;
    for (int bin = 1; bin <= histo->GetNbinsX(); ++bin) {
        ymax = std::max(ymax, histo->GetBinContent(bin) + histo->GetBinError(bin));
    }
    return ymax;
}

std::unique_ptr<TH2> make_ratio_2d(const TH2 *first, const TH2 *second,
                                   const std::string &name)
{
    if (first == nullptr || second == nullptr) {
        return nullptr;
    }

    auto ratio = std::unique_ptr<TH2>(static_cast<TH2 *>(second->Clone(name.c_str())));
    ratio->SetDirectory(nullptr);
    ratio->Reset("ICES");

    for (int xbin = 1; xbin <= first->GetNbinsX(); ++xbin) {
        for (int ybin = 1; ybin <= first->GetNbinsY(); ++ybin) {
            const double denominator = first->GetBinContent(xbin, ybin);
            const double numerator = second->GetBinContent(xbin, ybin);
            if (denominator <= 0.0) {
                ratio->SetBinContent(xbin, ybin, 0.0);
                ratio->SetBinError(xbin, ybin, 0.0);
                continue;
            }
            ratio->SetBinContent(xbin, ybin, numerator / denominator);
        }
    }

    return ratio;
}

void draw_2d_pad(TH2 *histo, const std::string &label)
{
    gPad->SetGrid();
    gPad->SetRightMargin(0.16);
    gPad->SetTopMargin(0.08);
    histo->DrawCopy("colz");

    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(18);
    latex.DrawLatex(0.12, 0.93, label.c_str());
}

} // namespace

std::string file_stem(const std::string &path)
{
    return std::filesystem::path(path).stem().string();
}

std::string sanitize_root_name(const std::string &name)
{
    std::string out;
    out.reserve(name.size());
    for (char c : name) {
        if (std::isalnum(static_cast<unsigned char>(c)) || c == '_') {
            out.push_back(c);
        } else {
            out.push_back('_');
        }
    }
    return out.empty() ? "histos" : out;
}

void ensure_directory(const std::string &path)
{
    if (path.empty()) {
        return;
    }
    std::error_code ec;
    std::filesystem::create_directories(path, ec);
    if (ec) {
        throw std::runtime_error("Could not create directory '" + path + "': " + ec.message());
    }
}

namespace {
std::string g_plot_extension = "png";
} // namespace

void set_plot_extension(const std::string &ext)
{
    std::string value = ext;
    if (!value.empty() && value.front() == '.') {
        value.erase(value.begin());
    }
    if (!value.empty()) {
        g_plot_extension = value;
    }
}

std::string plot_file(const std::string &dir, const std::string &stem)
{
    return dir + "/" + stem + "." + g_plot_extension;
}

void set_root_style(bool interactive)
{
    gROOT->SetBatch(!interactive);
    gStyle->SetOptStat(0);
    gStyle->SetOptTitle(0);
    gStyle->SetNumberContours(80);
    gStyle->SetPalette(kBird);
}

TCanvas *make_canvas(const std::string &name, const std::string &title, int width, int height)
{
    auto canvas = dynamic_cast<TCanvas *>(gROOT->FindObject(name.c_str()));
    if (canvas != nullptr) {
        canvas->Clear();
        canvas->SetTitle(title.c_str());
        return canvas;
    }
    return new TCanvas(name.c_str(), title.c_str(), width, height);
}

void draw_canvas_header(TCanvas *canvas, const std::string &header)
{
    if (canvas == nullptr || header.empty()) {
        return;
    }

    canvas->cd();
    TText text;
    text.SetNDC(true);
    text.SetTextFont(43);
    text.SetTextSize(16);
    text.SetTextAlign(21);
    text.DrawText(0.5, 0.977, header.c_str());
}

void draw_status_label(bool passed)
{
    TLatex latex;
    latex.SetNDC(true);
    latex.SetTextFont(43);
    latex.SetTextSize(24);
    latex.SetTextColor(passed ? kGreen + 3 : kRed + 1);
    latex.DrawLatex(0.14, 0.84, passed ? "passed" : "failed");
}

void show_canvas(TCanvas *canvas)
{
    if (canvas == nullptr) {
        return;
    }
    canvas->Draw();
    canvas->Modified();
    canvas->Update();
}

void draw_overlay(const std::vector<TH1 *> &histos, const std::vector<std::string> &labels,
                  const std::string &title, const std::string &output_path, bool log_y,
                  const std::string &header, bool has_status, bool passed)
{
    if (histos.empty()) {
        return;
    }

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title);
    canvas->SetGrid();
    canvas->SetLogy(log_y);

    const std::vector<int> colors = {kBlack, kRed + 1, kBlue + 1, kGreen + 2};
    const std::vector<int> markers = {20, 24, 21, 25};
    double ymax = 0.0;
    for (auto *histo : histos) {
        ymax = std::max(ymax, max_bin_content_with_error(histo));
    }
    if (ymax <= 0.0) {
        ymax = 1.0;
    }

    TLegend legend(0.65, 0.75, 0.90, 0.90);
    legend.SetBorderSize(0);
    legend.SetFillStyle(0);

    bool drew_one = false;
    for (std::size_t i = 0; i < histos.size(); ++i) {
        auto *histo = histos[i];
        if (histo == nullptr) {
            continue;
        }

        histo->SetLineColor(colors[i % colors.size()]);
        histo->SetMarkerColor(colors[i % colors.size()]);
        histo->SetMarkerStyle(markers[i % markers.size()]);
        histo->SetMarkerSize(0.7);
        histo->SetLineWidth(2);
        histo->SetMaximum(ymax * (log_y ? 5.0 : 1.25));
        histo->SetMinimum(log_y ? 0.1 : 0.0);
        histo->DrawCopy(drew_one ? "E1 same" : "E1");
        legend.AddEntry(histo, labels[i].c_str(), "lep");
        drew_one = true;
    }

    if (has_status) {
        draw_status_label(passed);
    }
    legend.DrawClone();
    draw_canvas_header(canvas, header);
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

void draw_2d(TH2 *histo, const std::string &title, const std::string &output_path)
{
    if (histo == nullptr) {
        return;
    }

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title);
    canvas->SetGrid();
    canvas->SetRightMargin(0.15);
    histo->DrawCopy("colz");
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

void draw_2d_comparison(TH2 *first, TH2 *second, const std::vector<std::string> &labels,
                        const std::string &title, const std::string &output_path,
                        const std::string &header, bool has_status, bool passed)
{
    if (first == nullptr || second == nullptr || labels.size() < 2) {
        return;
    }

    auto ratio = make_ratio_2d(first, second, "ratio_" + sanitize_root_name(title));
    if (ratio == nullptr) {
        return;
    }

    ratio->SetTitle((labels[1] + " / " + labels[0]).c_str());
    ratio->GetZaxis()->SetTitle((labels[1] + " / " + labels[0]).c_str());
    ratio->SetMinimum(0.0);
    ratio->SetMaximum(2.0);

    auto canvas = make_canvas("c_" + sanitize_root_name(output_path), title, 1800, 620);
    canvas->Divide(3, 1, 0.001, 0.001);

    canvas->cd(1);
    draw_2d_pad(first, labels[0]);

    canvas->cd(2);
    draw_2d_pad(second, labels[1]);
    if (has_status) {
        draw_status_label(passed);
    }

    canvas->cd(3);
    draw_2d_pad(ratio.get(), labels[1] + " / " + labels[0]);

    draw_canvas_header(canvas, header);
    canvas->SaveAs(output_path.c_str());
    show_canvas(canvas);
}

double SubsystemHistos::diagnostic_scale(const std::string &, bool normalize) const
{
    if (!normalize || events() <= 0) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events());
}

double SubsystemHistos::comparison_plot_scale(const std::string &, bool normalize) const
{
    if (!normalize || events() <= 0) {
        return 1.0;
    }
    return 1.0 / static_cast<double>(events());
}
