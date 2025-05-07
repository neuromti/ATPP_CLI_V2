import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt


class ClusterSelectionHeuristics:
    def __init__(self, WD, SUBs, ROI):
        self.WD = WD
        with open(SUBs, 'r') as f:
            self.SUB = [line.strip() for line in f]
        self.ROI = ROI
        self.validation_folder = os.path.join(self.WD, f'validation_{len(self.SUB)}')
        print('ROI: ', self.ROI)


    def kaiser_value_per_subject(self):
        """
        Calculate the Kaiser criterion for each subject.
        """
        data = pd.read_csv(os.path.join(self.validation_folder, 'data', f'eigenvalues_per_principle_component_{self.ROI}.csv'))
        kaiser_values = []
        for sub in self.SUB:
            subject_data = data[data['Subject'] == int(sub)]
            values = np.array(subject_data.drop(columns=[col for col in ['Subject', 'Kaiser criterion'] if col in subject_data.columns]))
            mean_value = values[0].mean()
            count_above_mean = (subject_data.drop(columns=['Subject']) > mean_value).sum(axis=1).values[0]
            kaiser_values.append(count_above_mean)

        data['Kaiser criterion'] = kaiser_values
        data.to_csv(os.path.join(self.validation_folder, 'data', f'eigenvalues_per_principle_component_{self.ROI}.csv'), index=False)


    def run_broken_stick_method(self):
        data = pd.read_csv(os.path.join(self.validation_folder, 'data', f'eigenvalues_per_principle_component_{self.ROI}.csv'))

        broken_stick_values = []
        for sub in self.SUB:
            print(sub)
            subject_data = data[data['Subject'] == int(sub)]
            eigenvalues = np.array(subject_data.drop(columns=[col for col in ['Subject', 'Broken stick method'] if col in subject_data.columns]))
            n_components = self.broken_stick(eigenvalues[0])
            broken_stick_values.append(n_components)

        data['Broken stick method'] = broken_stick_values
        data.to_csv(os.path.join(self.validation_folder, 'data', f'eigenvalues_per_principle_component_{self.ROI}.csv'), index=False)



    def broken_stick(self, ev, show=False):
        # Broken stick model (MacArthur 1957)
        n = len(ev)
        bsm = np.zeros((n, 2))
        bsm[:, 0] = np.arange(1, n+1)
        bsm[0, 1] = 1 / n
        for i in range(1, n):
            bsm[i, 1] = bsm[i-1, 1] + (1 / (n + 1 - i))
        bsm[:, 1] = 100 * bsm[:, 1] / n

        perc_eig = 100 * ev / np.sum(ev)

        if show:
            # Plot eigenvalues and % of variation for each axis
            fig, axes = plt.subplots(2, 1, figsize=(6, 8))
            fig.subplots_adjust(top=0.85, bottom=0.15, hspace=0.4)
            axes[0].bar(np.arange(1, n+1), ev, color='bisque')
            axes[0].axhline(y=np.mean(ev), color='red')
            axes[0].set_title("Eigenvalues")
            axes[0].legend(["Average eigenvalue"], loc='upper right')
            axes[0].set_xlabel("Axis")
            axes[0].set_ylabel("Eigenvalue")

            axes[1].bar(np.arange(1, n+1), perc_eig, color='bisque', label='% eigenvalue')
            axes[1].bar(np.arange(1, n+1), bsm[::-1, 1], color='blue', label='Broken stick model', alpha=0.4)
            axes[1].set_title("% Variation")
            axes[1].legend(loc='upper right')
            axes[1].set_xlabel("Axis")
            axes[1].set_ylabel("% Variation")

            plt.show()  # Commented out to prevent the script from hanging
            #plt.savefig(f"broken_stick_plot_{ev}.png")
            plt.close()
            
        ## TODO fix this hack!
        idxs = np.where(perc_eig>=bsm[::-1, 1])[0]
        idxs = idxs[idxs<30]

        return idxs.max()+1


if __name__ == '__main__':
    # Parse command-line arguments
    WD, SUB, ROI = sys.argv[1:]
    evaluator = ClusterSelectionHeuristics(WD, SUB, ROI)
    evaluator.kaiser_value_per_subject()
    evaluator.run_broken_stick_method()
