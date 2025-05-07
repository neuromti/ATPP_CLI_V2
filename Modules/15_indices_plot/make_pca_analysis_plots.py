import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns


class PlotPCAValidation:
    def __init__(self, WD, SUB_LIST, ROI):
        self.WD = WD
        with open(SUB_LIST, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.validation_folder = f'validation_{len(self.SUB)}'
        self.ROI = ROI
        self.color_palette = [
            '#F2CC8F',
            '#e07a5f',
            '#3d405b',
            '#81b29a',
        ]

    def plot_explained_variance_per_principle_component(self):
        data = pd.read_csv(f'{self.WD}/{self.validation_folder}/data/explained_variance_per_principle_component_{self.ROI}.csv')
        num_of_clusters = pd.read_csv(f'{self.WD}/{self.validation_folder}/data/eigenvalues_per_principle_component_{self.ROI}.csv')

        sns.set_style("whitegrid")

        # Create the plot
        plt.figure(figsize=(12, 8))
        
        columns = [f"PC{i+1}" for i in range(50)]

        mean_values = []
        std_values = []

        for i, column in enumerate(columns):
            mean_values.append(data[column].mean())
            std_values.append(data[column].std())
        
        mean_values = np.array(mean_values)
        std_values = np.array(std_values)
        plt.plot(range(1,51), mean_values, color=self.color_palette[2])
        plt.fill_between(range(1,51), mean_values - std_values, mean_values + std_values, alpha=0.2, color=self.color_palette[2])

        # Add a vertical line at a specific x value
        average_broken_stick = num_of_clusters['Broken stick method'].mean()
        average_kaiser = num_of_clusters['Kaiser criterion'].mean()
        plt.axvline(x=average_broken_stick, color='#6C7D47', linestyle='-', linewidth=2, label=f'Broken stick method (mean: {average_broken_stick:.2f})')
        plt.axvline(x=average_kaiser, color='#45425A', linestyle='-', linewidth=2, label=f'Kaiser criterion (mean: {average_kaiser:.2f})')

        # Labels and title
        plt.xlabel('Number of principle components')
        plt.ylabel('Explained variance')
        plt.title('Explained variance per principle component', weight='bold')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.legend()

        # Save the plot as a vector graphic (SVG) and a PNG
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/explained_variance_per_principle_component/jpgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/explained_variance_per_principle_component/jpgs/explained_variance_per_principle_component_{self.ROI}.jpg')
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/explained_variance_per_principle_component/svgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/explained_variance_per_principle_component/svgs/explained_variance_per_principle_component_{self.ROI}.svg')

    def plot_histograms(self):
        data = pd.read_csv(f'{self.WD}/{self.validation_folder}/data/eigenvalues_per_principle_component_{self.ROI}.csv')

        sns.set_style("whitegrid")
        # Create the plot
        plt.figure(figsize=(8, 8))
        columns = ['Kaiser criterion', 'Broken stick method']
        for i, column in enumerate(columns):
            plt.subplot(2, 1, i + 1)
            sns.histplot(data[column], kde=False, binwidth=1, color=self.color_palette[i+1], alpha=0.7)
            mean_value = data[column].mean()
            plt.axvline(mean_value, color='k', linestyle='-', linewidth=2, label=f'Mean: {mean_value:.2f}')
            plt.legend()
            plt.xlabel(f'Number of principle components to retain according to the {column}')
            plt.ylabel('Frequency')
            plt.title(f'Histogram of {column}', weight='bold')
        plt.tight_layout()
        # Save the plot as a vector graphic (SVG) and a PNG
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/histograms/jpgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/histograms/jpgs/PCA_heuristics_{self.ROI}.jpg')
        os.makedirs(f'{self.WD}/{self.validation_folder}/plots/histograms/svgs', exist_ok=True)
        plt.savefig(f'{self.WD}/{self.validation_folder}/plots/histograms/svgs/PCA_heuristics_{self.ROI}.svg')


if __name__ == '__main__':
    WD, SUB, ROI = sys.argv[1:]

    plotter = PlotPCAValidation(WD, SUB, ROI)
    plotter.plot_explained_variance_per_principle_component()
    plotter.plot_histograms()
        