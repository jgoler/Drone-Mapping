# Plotting Evaluation Results

I want to create plots for the NeRF and Gaussian Splatting evaluation results I have. Help write me code to generate these plots.

## Scope and Deliverables

Write Python code that I can paste into a python file to generate the desired plots as described later in the prompt. Use libraries like `pandas` for data handling and `matplotlib` or `seaborn` for plotting. Ensure the code is modular, well-commented, and easy to modify for future changes.

**Output Directory of Plots**: for now, same directory as the script. But this should be something I can easily change in the code later.

**Note**: None of the existing codebase is relevant to this tasks. All the relevant context is in this prompt.

## Context

I'm working on downsampling (i.e. frame selection) strategies to pick out smaller training data sets from a larger video dataset for training NeRFs and Gaussian Splatting models. I have evaluation results for different downsampling strategies, and I want to visualize these results using plots.

The evaluation results are stored in CSV files with PSNR, SSIM, and LPIPS metrics for each downsampling strategy. The CSV files exist in the folder `~/NeRF/drone_mapping/results/`. Note that this folder is specified as an absolute path and it is not in the workspace.

The folder contains CSV files, each named according to the downsampling strategy used, the percentage of frames retained, and whether it is for NeRF or Gaussian Splatting. For example, `10p_cluster_nerf.csv` means 10% of frames were retained using a clustering strategy for NeRF evaluation. The frame selection strategies include:

- Random sampling (`random`)
- Uniform sampling (`uniform`)
- Clustering-based sampling (`cluster`)
- Content-based sampling (`content`)
- Motion-based sampling (`motion`)

And, the percentages of frames retained go from 10 percent to 100 percent in increments of 10 percent (i.e., 10%, 20%, ..., 100%). As mentioned before, each CSV file contains the evaluation metrics PSNR, SSIM, and LPIPS for the particular experiment, with columns named `PSNR`, `SSIM`, and `LPIPS`.

## Plots Desired

I want to create the following plots:

1. **Line Plots**: For each downsampling strategy, create line plots showing how PSNR, SSIM, and LPIPS change as the percentage of frames retained increases from 10% to 100%. Each plot should have the percentage of frames on the x-axis and the metric value on the y-axis. There should be separate plots for NeRF and Gaussian Splatting. This should give you ten plots in total (five for each of the five sampling strategies for NeRF, and another five for Gaussian Splat).
2. **Box and Whisker Plots**: For each downsampling strategy, create box and whisker plots to visualize the distribution of PSNR values across different percentages of frames retained. Again, there should be separate plots for NeRF and Gaussian Splatting. For now, just do it for PSNR, but your code should be flexible enough for me to easily modify it to do the same for SSIM and LPIPS later if I want. This should give you ten plots in total (five for each of the five sampling strategies for NeRF, and another five for Gaussian Splat).
3. **Combined Line Plots**: Create combined line plots that overlay the results of all downsampling strategies on a single plot for each metric (PSNR, SSIM, LPIPS) for both NeRF and Gaussian Splatting. This will help compare the effectiveness of different downsampling strategies at a glance. This should give you six plots in total (three metrics for NeRF, and three for Gaussian Splat).
