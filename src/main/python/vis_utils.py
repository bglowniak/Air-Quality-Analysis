import os
import matplotlib.pyplot as plt

def boxplot(df, output_folder):
    #simple version, only makes the 4 boxplots every dataset has in common
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
    #fig.suptitle('Air Beam', fontsize=20)
    dat = [df['Temperature'].dropna()]
    ax1.boxplot(dat, labels = ['Temperature'], vert = True)
    dat = [df['Humidity'].dropna()]
    ax2.boxplot(dat, labels = ['Humidity'], vert = True)
    dat = [df['PM2.5'].dropna()]
    ax3.boxplot(dat, labels = ['PM 2.5'], vert = True)
    dat = [df['PM10.0'].dropna()]
    ax4.boxplot(dat, labels = ['PM 10.0'], vert = True)
    fig.subplots_adjust(wspace=0.5)
    outpath = os.path.join(output_folder, 'boxplot.png')
    fig.savefig(outpath)
    return outpath

def threshold_graph(df, output_folder):
    plt.close()
    _, axarr = plt.subplots(2, figsize=[10,8], sharex = True)
    axarr[0].plot(df['Datetime'], df['PM2.5'], label='PM 2.5')
    axarr[0].plot(df['Datetime'], df['PM10.0'], label='PM 10.0')
    axarr[0].hlines(25, df['Datetime'][0], df['Datetime'].tail(1), color='r', linestyles='dashed', label='Threshold')
    axarr[0].legend()
    axarr[0].set_title('Particulate Matter and Humidity')
    axarr[1].plot(df['Datetime'], df['Humidity'], label='Humidity (percent)')
    #plt.xticks([df['Datetime'][0], df['Datetime'][5000], df['Datetime'][10000]])
    axarr[1].legend()
    fn = 'threshold_graph.png'
    outpath = os.path.join(output_folder, fn)
    plt.savefig(outpath, dpi='figure')
    return outpath
