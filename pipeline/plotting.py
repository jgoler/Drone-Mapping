#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from pathlib import Path

# Configuration
RESULTS_DIR = os.path.expanduser("results/")
OUTPUT_DIR = "result_plots/"  # Change this to modify output directory
STRATEGIES = ["random", "uniform", "cluster", "content", "motion"]
PERCENTAGES = [0.5, 1, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90]
METHODS = ["nerf", "splat"]  # splat for Gaussian Splatting
METRICS = ["PSNR", "SSIM", "LPIPS"]

# Set style for better-looking plots
sns.set_style("whitegrid")
# Define a color-blind-friendly palette (Okabe–Ito subset) and apply it consistently.
# The mapping ensures the same color is used for each strategy across all plots.
COLOR_BLIND_PALETTE = {
    "random": "#E69F00",   # orange
    "uniform": "#CC79A7",  # purple / pink
    "cluster": "#009E73",  # green
    "content": "#0072B2",  # blue
    "motion": "#56B4E9",   # sky blue
}
# Apply the palette to seaborn's color cycle in the same order as STRATEGIES
sns.set_palette([COLOR_BLIND_PALETTE[s] for s in STRATEGIES])

# Enforce white background for figures and axes
plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"

def load_data(results_dir):
    """Load all CSV files and organize data into a structured format."""
    data = {}

    for method in METHODS:
        data[method] = {}
        for strategy in STRATEGIES:
            data[method][strategy] = {}
            for percentage in PERCENTAGES:
                percent_str = str(int(percentage)) if percentage.is_integer() else str(percentage)
                percent_str = percent_str.replace('.', '')  # e.g., 0.5 -> '05'
                filename = f"{percentage}p_{strategy}_{method}.csv"
                filepath = os.path.join(results_dir, filename)

                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    data[method][strategy][percentage] = df
                else:
                    print(f"Warning: File not found - {filepath}")

    return data


def create_line_plots(data, output_dir):
    """Create line plots for each downsampling strategy showing metric trends."""
    print("Creating line plots...")

    for method in METHODS:
        method_name = "NeRF" if method == "nerf" else "Gaussian Splatting"

        for strategy in STRATEGIES:
            # Skip this strategy if no data is available
            if not data.get(method, {}).get(strategy, {}):
                continue

            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            fig.suptitle(f"{strategy.title()} Strategy - {method_name}", fontsize=16)

            for i, metric in enumerate(METRICS):
                percentages = []
                means = []
                stds = []

                for percentage in PERCENTAGES:
                    if percentage in data[method][strategy]:
                        df = data[method][strategy][percentage]
                        if metric in df.columns:
                            percentages.append(percentage)
                            means.append(df[metric].mean())
                            stds.append(df[metric].std())

                if percentages:
                    axes[i].errorbar(
                        percentages,
                        means,
                        yerr=stds,
                        marker="o",
                        linewidth=2,
                        markersize=6,
                        color=COLOR_BLIND_PALETTE[strategy],
                    )
                    axes[i].set_xlabel("Percentage of Frames Retained (%)")
                    axes[i].set_ylabel(metric)
                    axes[i].set_title(f"{metric} vs Frame Percentage")
                    axes[i].grid(True, alpha=0.3)
                    axes[i].set_xlim(-5, 95)

            plt.tight_layout()
            filename = f"line_plot_{strategy}_{method}.png"
            plt.savefig(
                os.path.join(output_dir, filename),
                dpi=300,
                bbox_inches="tight",
                facecolor=plt.rcParams.get("figure.facecolor", "white"),
                transparent=False,
            )
            plt.close()


def create_box_plots(data, output_dir, metric="PSNR"):
    """Create box and whisker plots for the specified metric."""
    print(f"Creating box plots for {metric}...")

    for method in METHODS:
        method_name = "NeRF" if method == "nerf" else "Gaussian Splatting"

        for strategy in STRATEGIES:
            # Prepare data for box plot
            plot_data = []

            for percentage in PERCENTAGES:
                if percentage in data[method][strategy]:
                    df = data[method][strategy][percentage]
                    if metric in df.columns:
                        for value in df[metric]:
                            plot_data.append(
                                {
                                    "Percentage": f"{percentage}%",
                                    "Value": value,
                                    "Percentage_num": percentage,
                                }
                            )

            if plot_data:
                plot_df = pd.DataFrame(plot_data)

                plt.figure(figsize=(12, 6))
                # Use the mapped color for this strategy's boxplot so colors are consistent
                sns.boxplot(data=plot_df, x="Percentage", y="Value", color=COLOR_BLIND_PALETTE[strategy])
                plt.title(f"{strategy.title()} Strategy - {method_name} - {metric} Distribution")
                plt.xlabel("Percentage of Frames Retained")
                plt.ylabel(metric)
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)

                filename = f"box_plot_{strategy}_{method}_{metric.lower()}.png"
                plt.savefig(
                    os.path.join(output_dir, filename),
                    dpi=300,
                    bbox_inches="tight",
                    facecolor=plt.rcParams.get("figure.facecolor", "white"),
                    transparent=False,
                )
                plt.close()


def create_combined_plots(data, output_dir):
    """Create combined line plots comparing all strategies for each metric."""
    print("Creating combined comparison plots...")

    for method in METHODS:
        method_name = "NeRF" if method == "nerf" else "Gaussian Splatting"

        for metric in METRICS:
            plt.figure(figsize=(10, 6))

            for strategy in STRATEGIES:
                percentages = []
                means = []

                for percentage in PERCENTAGES:
                    if percentage in data[method][strategy]:
                        df = data[method][strategy][percentage]
                        if metric in df.columns:
                            percentages.append(percentage)
                            means.append(df[metric].mean())

                if percentages:
                    plt.plot(
                        percentages,
                        means,
                        marker="o",
                        linewidth=2,
                        markersize=6,
                        label=strategy.title(),
                        color=COLOR_BLIND_PALETTE[strategy],
                        alpha=0.8,
                    )

            plt.xlabel("Percentage of Frames Retained (%)")
            plt.ylabel(metric)
            plt.title(f"{metric} Comparison Across Strategies - {method_name}")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xlim(5, 105)

            filename = f"combined_plot_{method}_{metric.lower()}.png"
            plt.savefig(
                os.path.join(output_dir, filename),
                dpi=300,
                bbox_inches="tight",
                facecolor=plt.rcParams.get("figure.facecolor", "white"),
                transparent=False,
            )
            plt.close()


def create_iqr_comparison_plot(data, output_dir, method="splat", strategies=("uniform", "random"), metric="PSNR", filename=None):
    """Compare two strategies for a given method and metric.
    Plots mean lines and shaded IQR (25th-75th percentiles) per percentage.
    """
    if method not in METHODS:
        raise ValueError(f"Unknown method: {method}")

    for s in strategies:
        if s not in STRATEGIES:
            raise ValueError(f"Unknown strategy: {s}")

    method_name = "NeRF" if method == "nerf" else "Gaussian Splatting"
    if metric not in METRICS:
        raise ValueError(f"Unknown metric: {metric}")
    if metric == "LPIPS":
        ylim = (0.4, 0.75)
    elif metric == "SSIM":
        ylim = (0.35, 0.65)
    else:
        ylim = (12, 26)
    plt.figure(figsize=(5, 3))

    any_data = False
    for strategy in strategies:
        perc_list = []
        means = []
        q1s = []
        q3s = []
        medians = []

        for p in PERCENTAGES:
            if p in data[method][strategy]:
                df = data[method][strategy][p]
                if metric in df.columns and not df[metric].dropna().empty:
                    series = df[metric].dropna()
                    perc_list.append(p)
                    means.append(series.mean())
                    medians.append(series.median())
                    q1s.append(series.quantile(0.25))
                    q3s.append(series.quantile(0.75))

        if perc_list:
            any_data = True
            color = COLOR_BLIND_PALETTE.get(strategy, None)
            # plot mean line
            plt.plot(perc_list, medians, marker="D", linewidth=2, markersize=6,
                     label=f"{strategy.title()} median", color=color, alpha=0.9)
            # plot median markers
            plt.scatter(perc_list, means, marker="o", s=30, color=color, alpha=0.9)
            # shaded IQR
            plt.fill_between(perc_list, q1s, q3s, color=color, alpha=0.25,
                             label=f"{strategy.title()} IQR (25-75%)")

    if not any_data:
        print(f"No data available for method={method}, metric={metric}, strategies={strategies}")
        return None

    plt.xlabel("Percentage of Frames Retained (%)")
    plt.ylabel(metric)
    # plt.title(f"{metric} IQR Comparison: {', '.join([s.title() for s in strategies])} - {method_name}")
    # plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(5, 95)
    plt.ylim(ylim)
    plt.xticks(PERCENTAGES, rotation=45)

    if filename is None:
        filename = f"iqr_comparison_{method}_{metric.lower()}_{'_vs_'.join(strategies)}.png"
    outpath = os.path.join(output_dir, filename)
    plt.savefig(
        outpath,
        dpi=300,
        bbox_inches="tight",
        facecolor=plt.rcParams.get("figure.facecolor", "white"),
        transparent=False,
    )
    plt.close()
    return outpath


def create_strategy_legend(
    output_dir,
    strategies=STRATEGIES,
    filename="strategy_legend.png",
    subplot_width=4.0,
    ncols_to_span=2,
    height=0.6,
    fontsize=10,
    transparent=True,
    save_pdf=False,
):
    """
    Create a single-line legend figure showing one colored patch per strategy.

    Parameters
    - output_dir: directory to save the legend image
    - strategies: list of strategy keys (defaults to STRATEGIES)
    - filename: output filename for the PNG
    - subplot_width: width (in inches) of a single subplot column in your page layout
                     (legend width = subplot_width * ncols_to_span)
    - ncols_to_span: number of subplot columns the legend should span (use 2 for two columns)
    - height: legend figure height in inches (0.4-1.0 typical)
    - fontsize: text size for labels
    - transparent: whether to make the saved PNG background transparent (useful for LaTeX)
    - save_pdf: also save a PDF alongside the PNG (vector format for LaTeX)

    Returns: list of saved file paths (PNG first, PDF second if requested)
    """
    import matplotlib.patches as mpatches

    os.makedirs(output_dir, exist_ok=True)
    fig_width = float(subplot_width) * int(ncols_to_span)

    fig = plt.figure(figsize=(fig_width, height))

    # Build handles using the same palette mapping
    handles = []
    labels = []
    for s in strategies:
        color = COLOR_BLIND_PALETTE.get(s, "#333333")
        handles.append(mpatches.Patch(color=color))
        labels.append(s.title())

    # Center the legend in the figure and force one row
    legend = fig.legend(
        handles=handles,
        labels=labels,
        loc="center",
        ncol=len(strategies),
        frameon=False,
        fontsize=fontsize,
    )

    # Remove axes and margins so the legend occupies the entire image width
    plt.axis("off")
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    out_png = os.path.join(output_dir, filename)
    fig.savefig(out_png, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=transparent)
    saved = [out_png]

    if save_pdf:
        out_pdf = os.path.join(output_dir, os.path.splitext(filename)[0] + ".pdf")
        # For PDF we can keep transparency if desired; PDFs are vector and preferred for LaTeX
        fig.savefig(out_pdf, dpi=300, bbox_inches="tight", pad_inches=0.02, transparent=transparent)
        saved.append(out_pdf)

    plt.close(fig)
    return saved


def main():
    """Main function to orchestrate the plotting process."""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Check if results directory exists
    if not os.path.exists(RESULTS_DIR):
        print(f"Error: Results directory not found at {RESULTS_DIR}")
        return

    print(f"Loading data from {RESULTS_DIR}...")
    data = load_data(RESULTS_DIR)

    # Check if any data was loaded
    data_found = False
    for method in METHODS:
        for strategy in STRATEGIES:
            if data[method][strategy]:
                data_found = True
                break
        if data_found:
            break

    if not data_found:
        print("No data files found. Please check the results directory and file naming convention.")
        return

    print(f"Generating plots in {OUTPUT_DIR}...")

    # # Generate all plots
    # Filter for just the motion splat data for now
    data = {
        "splat": {
            "motion": data["splat"]["motion"],
            "uniform": data["splat"]["uniform"],
        }
    }

    # create_line_plots(data, OUTPUT_DIR)
    # create_box_plots(data, OUTPUT_DIR, "PSNR")  # Can change metric here
    # create_combined_plots(data, OUTPUT_DIR)

    # # Example IQR comparison plots
    # metrics = ["PSNR", "SSIM", "LPIPS"]
    # methods = ["nerf", "splat"]
    # for method in methods:
    #     for metric in metrics:
    #         filename = f"iqr_comparison_{method}_{metric.lower()}_all.png"
    #         create_iqr_comparison_plot(
    #             data, OUTPUT_DIR, method=method, strategies=("uniform", "random", "cluster", "motion", "content"), metric=metric, filename=filename
    #         )

    filename = f"iqr_splat_motion.png"
    create_iqr_comparison_plot(
        data, OUTPUT_DIR, method="splat", strategies=("motion", "uniform"), metric="PSNR", filename=filename
    )

    # print("All plots generated successfully!")

    # # Print summary of generated files
    # plot_files = glob.glob(os.path.join(OUTPUT_DIR, "*.png"))
    # print(f"\nThere are {len(plot_files)} plot files:")
    # for file in sorted(plot_files):
    #     print(f"  - {os.path.basename(file)}")


if __name__ == "__main__":
    main()
