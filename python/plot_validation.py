import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Report on the validation results.')
    parser.add_argument('--input', help='input filename')
    args = parser.parse_args()
    data = pd.read_csv(args.input)
    unvalidated = data[data.pred_lon == 0]
    data = data[data.pred_lon != 0]

    dist_err_filename = '%s_dist_err_hist.png' % args.input[:-4]
    dist_err_fig = plt.figure()
    dist_err_ax = dist_err_fig.add_subplot(111)
    dist_err_hist = dist_err_ax.hist(data.dist_err, bins=np.logspace(0.1, 4.0, 10))
    dist_err_ax.set_xlabel('distance (km)')
    dist_err_ax.set_ylabel('frequency')
    dist_err_fig.gca().set_xscale("log")
    dist_err_fig.savefig(dist_err_filename, dpi='figure')

    adjust_dist_err_filename = '%s_adjust_dist_err_hist.png' % args.input[:-4]
    adjust_dist_err_fig = plt.figure()
    adjust_dist_err_ax = adjust_dist_err_fig.add_subplot(111)
    adjust_dist_err_ax.set_xlabel('distance (km)')
    adjust_dist_err_ax.set_ylabel('frequency')
    adjust_dist_err_ax.hist(data.adjust_dist_err, bins=np.logspace(0.1, 4.0, 10))
    adjust_dist_err_fig.gca().set_xscale("log")
    adjust_dist_err_fig.savefig(adjust_dist_err_filename, dpi='figure')
