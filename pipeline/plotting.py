#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Function to extract percentage from filename
def extract_percentage(filename):
    return int(filename.split("_")[0].replace("p", ""))


# Function to read CSV files and return a DataFrame
def read_results(results_folder, keyframe_methods, model_types):
    data = []
    for model_type in model_types:
        for method in keyframe_methods:
            for filename in os.listdir(results_folder):
                if filename.endswith(f"_{method}_{model_type}.csv"):
                    percentage = extract_percentage(filename)
                    df = pd.read_csv(os.path.join(results_folder, filename))
                    df["Percentage"] = percentage
                    df["Method"] = method
                    df["Model"] = model_type
                    data.append(df)
    return pd.concat(data, ignore_index=True)


# Function to plot box and whisker plots
def plot_metrics(results_df, metrics, model_types):
    for metric in metrics:
        for model_type in model_types:
            plt.figure(figsize=(12, 8))
            sns.boxplot(
                x="Percentage",
                y=metric,
                hue="Method",
                data=results_df[results_df["Model"] == model_type],
                showfliers=False,
            )
            plt.title(f"{metric} vs Percentage of Frames Remaining ({model_type})", fontsize=20)
            plt.xlabel("Percentage of Frames Remaining", fontsize=18)
            plt.ylabel(metric, fontsize=18)
            plt.legend(prop={"size": 16})
            plt.grid(True)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            plt.savefig(
                f"/home/navlab/NeRF/drone_mapping/Drone-Mapping/plots/{metric}_{model_type}.png"
            )
            plt.show()


if __name__ == "__main__":
    # Define the path to the results folder
    results_folder = "/home/navlab/NeRF/drone_mapping/Drone-Mapping/results/pepperwood_preserve"

    # Define the keyframe selection methods and model types
    keyframe_methods = ["katna", "random", "open_source", "ffmpeg"]
    model_types = ["nerfacto", "splatfacto"]
    metrics = ["PSNR", "SSIM"]
    # Read the results
    results_df = read_results(results_folder, keyframe_methods, model_types)
    # Plot the metrics
    plot_metrics(results_df, metrics, model_types)
