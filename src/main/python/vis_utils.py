import os
import matplotlib
matplotlib.use('Agg')
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

def humidity_graph(df, output_folder):
    plt.close()
    _, axarr = plt.subplots(2, figsize=[10,8], sharex = True)
    axarr[0].plot(df['Datetime'], df['PM2.5'], label='PM 2.5')
    axarr[0].plot(df['Datetime'], df['PM10.0'], label='PM 10.0')
    axarr[0].legend()
    axarr[0].set_title('Particulate Matter and Humidity')
    axarr[1].plot(df['Datetime'], df['Humidity'], label='Humidity (percent)')
    axarr[1].legend()
    fn = 'humidity_graph.png'
    outpath = os.path.join(output_folder, fn)
    plt.savefig(outpath, dpi='figure')
    return outpath

def threshold_PM25(df, output_folder):
    PM25_ANNUAL_PRIMARY_WHO = 10
    PM25_ANNUAL_PRIMARY_NAAQS = 12
    PM25_ANNUAL_SECONDARY_NAAQS = 15
    PM25_24HR_WHO = 25
    PM25_24HR_NAAQS = 35

    _, axarr = plt.subplots(1, figsize=[10,8], sharex = True)
    axarr.plot(df['Datetime'], df['PM2.5'], label='PM 2.5')

    axarr.hlines(PM25_ANNUAL_PRIMARY_WHO, df['Datetime'][0], df['Datetime'].tail(1), color='m', linestyles='dashed', label='WHO Annual Primary')
    axarr.hlines(PM25_ANNUAL_PRIMARY_NAAQS, df['Datetime'][0], df['Datetime'].tail(1), color='r', linestyles='dashed', label='NAAQS Annual Primary')
    axarr.hlines(PM25_ANNUAL_SECONDARY_NAAQS, df['Datetime'][0], df['Datetime'].tail(1), color='y', linestyles='dashed', label='NAAQS Annual Secondary')
    axarr.hlines(PM25_24HR_WHO, df['Datetime'][0], df['Datetime'].tail(1), color='g', linestyles='dashed', label='WHO 24 Hour')
    axarr.hlines(PM25_24HR_NAAQS, df['Datetime'][0], df['Datetime'].tail(1), color='b', linestyles='dashed', label='NAAQS 24 Hour')

    axarr.legend()
    axarr.set_title('Particulate Matter 2.5')

    fn = 'pm25_graph.png'
    outpath = os.path.join(output_folder, fn)
    plt.savefig(outpath, dpi='figure')
    return outpath

def threshold_PM10(df, output_folder):
    PM10_24HR_WHO = 50
    PM10_ANNUAL_PRIMARY_WHO = 20
    PM10_24HR_NAAQS = 150

    _, axarr = plt.subplots(1, figsize=[10,8], sharex = True)
    axarr.plot(df['Datetime'], df['PM10.0'], label='PM 10.0')

    axarr.hlines(PM10_ANNUAL_PRIMARY_WHO, df['Datetime'][0], df['Datetime'].tail(1), color='m', linestyles='dashed', label='WHO Annual Primary')
    axarr.hlines(PM10_24HR_WHO, df['Datetime'][0], df['Datetime'].tail(1), color='g', linestyles='dashed', label='WHO 24 Hour')
    axarr.hlines(PM10_24HR_NAAQS, df['Datetime'][0], df['Datetime'].tail(1), color='b', linestyles='dashed', label='NAAQS 24 Hour')

    axarr.legend()
    axarr.set_title('Particulate Matter 10.0')

    fn = 'pm10_graph.png'
    outpath = os.path.join(output_folder, fn)
    plt.savefig(outpath, dpi='figure')
    return outpath