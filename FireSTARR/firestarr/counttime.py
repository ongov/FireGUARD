"""Go through a folder and figure out how long it took to run all the fires in it"""

import os
import sys
import fnmatch
from dateutil.parser import parse
import pandas
from Settings import Settings
## Number of results to display
TOP = 20

## Default folder to summarize if none specified
DEFAULT_FOLDER = Settings.OUTPUT_DEFAULT
## folder to summarize
folder = DEFAULT_FOLDER if 1 == len(sys.argv) else sys.argv[1]

def read_file(input, from_file=None):
    """!
    Read the entire contents of a file
    @param input Directory to read from, or entire path to file
    @param from_file File within directory, or None if input is full path
    @return String contents of file
    """
    file = os.path.join(input, from_file) if from_file else input
    with open(file, "r") as text_file:
        return text_file.read()

def get_time(line):
    """!
    Parse time from line of a log
    @param line String to parse time from
    @return Time for parsed line
    """
    return parse(line[1:line.find(']')])

def run():
    """!
    Calculate time that simulations took to run
    @return None
    """
    min_start = None
    max_stop = None
    total = None
    data = []
    for root, dirs, files in os.walk(folder):
        for file in fnmatch.filter(files, "output.txt"):
            real_folder = apply(os.path.join, root.split('/'))
            path = os.path.join(real_folder, file)
            stdout = read_file(path)
            sim_output = stdout.strip().split('\n')
            fire = [x for x in sim_output if r'firestarr.exe' in x]
            if 1 == len(fire):
                fire = fire[0]
                fire = fire[fire.find(r'firestarr.exe'):]
                if '--perim' in fire:
                    fire = fire[:fire.rfind('--perim')]
                fire = fire[:fire.rfind('/')]
                fire = fire[fire.rfind('/') + 1:]
            else:
                fire = [x for x in sim_output if r'Saving to' in x][0]
                fire = fire[:fire.rfind('/')]
                fire = fire[:fire.rfind('/')]
                fire = fire[fire.rfind('/') + 1:]
            start = get_time(sim_output[0])
            stop = get_time(sim_output[-1])
            if not min_start or start < min_start:
                min_start = start
            if not max_stop or stop > max_stop:
                max_stop = stop
            duration = stop - start
            print fire, duration
            data.append([fire, duration])
            total = total + duration if total else duration
    #~ print total
    df = pandas.DataFrame(data)
    df.columns = ['Fire', 'Duration']
    df = df.sort_values('Duration', ascending=False).set_index('Fire')
    print "{} fires processed".format(len(df))
    print "Top {}:".format(TOP)
    print df[:TOP]
    print 'Sum:    ', df['Duration'].sum()
    print 'Median: ', df['Duration'].median()
    print 'Mean:   ', df['Duration'].mean()
    print 'Max:    ', df['Duration'].max()
    print 'Min:    ', df['Duration'].min()
    print 'Total Duration: ', (max_stop - min_start)

if __name__ == "__main__":
    run()
