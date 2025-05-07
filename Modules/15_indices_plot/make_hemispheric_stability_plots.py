import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns


class PlotValidation:
    def __init__(self, WD, SUB_LIST, MAX_CL_NUM):
        self.WD = WD
        with open(SUB_LIST, 'r') as f:
            self.SUB = [line.strip() for line in f]

        self.MAX_CL_NUM = MAX_CL_NUM
        self.validation_folder = f'validation_{len(self.SUB)}'
        self.color_palette = [
            '#F2CC8F',
            '#e07a5f',
            '#3d405b',
            '#81b29a',
        ]


    def plot_hemispheric_coefficients_group(self):

        data = pd.read_csv(f'{self.WD}/{self.validation_folder}/data/group_validation_hemispheric_stability.csv')

        sns.set_style("whitegrid")

        # Create the plot
        plt.figure(figsize=(12, 8))
        scores = ['Dice Coefficient', 'Jaccard Index', 'NMI (normalized mutual information)', 'Rand Index']

        # Plot each column with a different line style and color
        for idx, score in enumerate(scores):
            plt.plot(data['Clusters'], data[score], label=str(score), marker="o", color=self.color_palette[idx])

        # Labels and title
        plt.xlabel('Number of clusters')
        plt.ylabel('Coefficients of hemispheric stability')
        plt.ylim(0, 1)
        plt.title('Coefficients of hemispheric stability on group level', weight='bold')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()


        # Save the plot as a vector graphic (SVG) and a PNG
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/jpgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/jpgs/hemispheric_stability_group.jpg')
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/svgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/svgs/hemispheric_stability_group.svg')



    def plot_hemispheric_coefficients_subjects(self):
        # Load the data
        data = pd.read_csv(f'{self.WD}/{self.validation_folder}/data/subject_level_validation_hemispheric_stability.csv')

        # Group by Cluster and calculate the mean and std for each metric
        group_results = data.groupby('Clusters').agg(['mean', 'std']).reset_index()

        # Define the scores to plot
        scores = ['Dice Coefficient', 'Jaccard Index', 'NMI (normalized mutual information)', 'Rand Index']

        # Set the style
        sns.set_style("whitegrid")

        # Create a plot for each score
        for idx, score in enumerate(scores):
            # Extract mean and std for the current score
            mean = group_results[score]['mean']
            std = group_results[score]['std']
            clusters = group_results['Clusters']

            plt.figure(figsize=(12, 8))
            
            # Plot the mean line
            plt.plot(clusters, mean, label=f'{score.replace("_", " ")}', marker='o', color=self.color_palette[idx])
            
            # Plot the shaded area for std
            plt.fill_between(clusters, mean - std, mean + std, alpha=0.2, color=self.color_palette[idx])

            # Add labels, title, and legend
            plt.xlabel('Number of clusters')
            plt.ylabel(f'{score.replace("_", " ")}')
            plt.title(f'Hemispheric Stability on Subject Level - {score.replace("_", " ")} ± std')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.ylim(0, 1)

            os.makedirs(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/jpgs', exist_ok=True)
            plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/jpgs/hemispheric_stability_subject_{score}.png')
            os.makedirs(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/svgs', exist_ok=True)
            plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/svgs/hemispheric_stability_subject_{score}.svg')


        plt.figure(figsize=(12, 8))
        for idx, score in enumerate(scores):
            # Extract mean and std for the current score
            mean = group_results[score]['mean']
            std = group_results[score]['std']
            clusters = group_results['Clusters']

            
            # Plot the mean line
            plt.plot(clusters, mean, label=f'{score.replace("_", " ")}', marker='o', color=self.color_palette[idx])
            
            # Plot the shaded area for std
            plt.fill_between(clusters, mean - std, mean + std, alpha=0.2, color=self.color_palette[idx])

        # Add labels, title, and legend
        plt.xlabel('Clusters')
        plt.ylabel(f'Validation metrics')
        plt.title(f'Hemispheric stability on subject level - All Scores')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.ylim(0, 1)

        # Save the plot
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/jpgs/hemispheric_stability_all_scores.png')
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/hemispheric_stability/svgs/hemispheric_stability_all_scores.svg')





def load_arguments():
    if len(sys.argv) != 4:
        print("Usage: python3 Modules/13_indices_plot/make_validation_plots.py <WD> <SUB_LIST> <MAX_CL_NUM>", flush=True)
        sys.exit(1)

    WD = sys.argv[1]
    SUB_LIST = sys.argv[2]
    MAX_CL_NUM = int(sys.argv[3])

    return WD, SUB_LIST, MAX_CL_NUM

if __name__ == "__main__":
    WD, SUB_LIST, MAX_CL_NUM = load_arguments()
    print(f"WD: {WD}")
    print(f"SUB_LIST: {SUB_LIST}")
    print(f"MAX_CL_NUM: {MAX_CL_NUM}")

    plot_validation = PlotValidation(WD, SUB_LIST, MAX_CL_NUM)
    plot_validation.plot_hemispheric_coefficients_group()
    plot_validation.plot_hemispheric_coefficients_subjects()