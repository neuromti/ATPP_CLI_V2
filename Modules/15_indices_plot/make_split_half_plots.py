import pandas as pd
import os
import matplotlib.pyplot as plt
import sys
import seaborn as sns


class SplitHalfPlot:
    def __init__(self, WD, SUB, ROI):
        """
        Initializes the class with parameters for plotting split-half reliability results.

        Parameters:
        -----------
        WD : str
            Working directory where results and data are stored.
        N_ITER : int
            Number of iterations for split-half evaluation.
        MAX_CL_NUM : int
            Maximum number of clusters to evaluate.
        """
        self.WD = WD
        with open(SUB, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.ROI = ROI


    def plot_split_half_results(self):
        """
        Plots split-half reliability results for each ROI and each number of clusters.
        """

        color_palette = [
            '#F2CC8F',
            '#e07a5f',
            '#3d405b',
            '#81b29a',
        ]

        split_half_results = pd.read_csv(
            os.path.join(self.WD, f'validation_{len(self.SUB)}', 'data', f'split_half_scores_{self.ROI}.csv'))
        
        split_half_results = split_half_results.groupby('Clusters').agg(['mean', 'std']).reset_index()

        # Define the scores to plot
        scores = ['Dice Coefficient', 'Jaccard Index', 'NMI (normalized mutual information)', 'Rand Index']

        # Set the style
        sns.set_style("whitegrid")


        # Create a plot for each score
        for idx, score in enumerate(scores):
            # Extract mean and std for the current score
            mean = split_half_results[score]['mean']
            std = split_half_results[score]['std']
            clusters = split_half_results['Clusters']

            plt.figure(figsize=(12, 8))
            
            # Plot the mean line
            plt.plot(clusters, mean, label=f'{score.replace("_", " ")}', marker='o', color=color_palette[idx])
            
            # Plot the shaded area for std
            plt.fill_between(clusters, mean - std, mean + std, alpha=0.2, color=color_palette[idx])

            # Add labels, title, and legend
            plt.xlabel('Number of clusters')
            plt.ylabel(f'{score.replace("_", " ")}')
            plt.title(f'Split-half reliability for {self.ROI} - {score.replace("_", " ")} ± std')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.ylim(0, 1)

            os.makedirs(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/jpgs', exist_ok=True)
            plt.savefig(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/jpgs/split_half_{self.ROI}_{score}.png')
            os.makedirs(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/svgs', exist_ok=True)
            plt.savefig(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/svgs/split_half_{self.ROI}_{score}.svg')



        plt.figure(figsize=(12, 8))
        for idx, score in enumerate(scores):
            # Extract mean and std for the current score
            mean = split_half_results[score]['mean']
            std = split_half_results[score]['std']
            clusters = split_half_results['Clusters']

            
            # Plot the mean line
            plt.plot(clusters, mean, label=f'{score.replace("_", " ")}', marker='o', color=color_palette[idx])
            
            # Plot the shaded area for std
            plt.fill_between(clusters, mean - std, mean + std, alpha=0.2, color=color_palette[idx])

        # Add labels, title, and legend
        plt.xlabel('Clusters')
        plt.ylabel(f'Validation metrics')
        plt.title(f'Split-half reliability for {self.ROI} - All Scores')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.ylim(0, 1)

        # Save the plot
        plt.savefig(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/jpgs/split_half_{self.ROI}_all_scores.png')
        plt.savefig(f'{self.WD}/validation_{len(self.SUB)}/plots/split_half_validation/svgs/split_half_{self.ROI}_all_scores.svg')



if __name__ == '__main__':
    WD, SUB, ROI = sys.argv[1:]

    plotter = SplitHalfPlot(WD, SUB, ROI)
    plotter.plot_split_half_results()
        