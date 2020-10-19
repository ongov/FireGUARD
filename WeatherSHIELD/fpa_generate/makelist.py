import pandas
import re
import numpy

def split_line(line):
    """ Split given line on whitespace sections """
    return re.sub(r' +', ' ', line.strip()).split(' ')



def read(filename):
    """ Read AMO data from URL """
    with open(filename, 'r') as f:
        return [line for line in f]

def write(input=r'grid_lctns.ltab', max=100, groups=10):
    content = read(input)
    cols = numpy.array(map(split_line, content))
    # points = map(lambda x: split_line(x)[0], content)
    set = 'a'
    num_files = (len(cols) / max) + 1
    for n in xrange(num_files):
        file = r'split_{:04d}{}'.format(max, (chr(ord(set) + n)))
        print n, file
        cur = cols[(n * max):((n + 1)* max)]
        points = cur[:, 0]
        with open(file + '.ltab', 'w') as ltab:
            ltab.writelines(content[(n * max):((n + 1)* max)])
        with open(file + '.fpdf', 'w') as f:
            f.write('\n'.join([
                '! Display the OR sites ...',
                '',
                '! =================================================================',
                '! To add new stations, insert new station identifier after the last',
                '! identifier and before the semi-colon as in:',
                '! location_ident_list =	WFS BAK NEW;',
                '! =================================================================',
                '',
                '@define_sample_list',
                '{',
                '  list_name           = list_stns;',
                ''
            ]))
            group_size = max / groups
            for group in xrange(group_size):
                f.write('!S{:02d}\n'.format(group))
                f.write('  location_ident_list = ')
                f.write(' '.join(points[(group * group_size):((group + 1) * group_size)]))
                f.write('\n')
            f.write('\n'.join([
                '  x_shift = 0;',
                '  y_shift = 1;',
                '}',
                ''
                '']))

write()
