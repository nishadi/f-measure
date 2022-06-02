# Python script to generate the two plots for DMKD paper on F-measure
#
# Peter Christen, with Google Scholar crawling program by Nishadi Kirielle
#
# May 2022
#
# Assumed structure of the input file is (first line is a header line)
# - col 1: years
# - col 2 onwards: various query terms
# - rows 2 onwards are counts for query terms for individual years
#
import sys
import time

import matplotlib
import matplotlib.pyplot as plt

today_str = time.strftime("%Y%m%d", time.localtime())  # yyyymmdd

# The measures not to include in the calculations and plotting
#
black_list = ['misclassification+rate', 'false+discovery+rate',
              'auc+AND+roc', 'area+under+curve',
              'auc+AND+precision+AND+recall']

#all_fm_query_term = 'f-measure+OR+f1-measure+OR+f-score+OR+f1-score'

# -----------------------------------------------------------------------------

in_file = open(sys.argv[1])  # CSV filewith counts

header_line = in_file.readline()
print(header_line)

all_query_term_list =   []
fm_query_term_list =    []  # Single F-measure related query terms
fm_or_query_term_list = []  # Conjuncted F-measure related query terms

for query_term in header_line.split(',')[1:]:
  query_term = query_term.strip()
  all_query_term_list.append(query_term)

  if ('f-measure' in query_term) or ('f1-measure' in query_term) or \
     ('f-score' in query_term) or ('f1-score' in query_term):

    if ('+OR+' not in query_term):
      fm_query_term_list.append(query_term)
    else:
      fm_or_query_term_list.append(query_term)

print(all_query_term_list)
print(fm_query_term_list)
print(fm_or_query_term_list)
print()

query_res_dict = {}  # One list per query term with counts per year

year_list = []

for line in in_file:
  if (line.strip()[0] == '#'):
    continue
  line_list = line.strip().split(',')

  year = int(line_list[0])
  year_list.append(year)

  for (i, query_term) in enumerate(all_query_term_list):
    year_count = int(line_list[i+1])
    query_term_count_list = query_res_dict.get(query_term, [])
    query_term_count_list.append(year_count)
    query_res_dict[query_term] = query_term_count_list

num_year = len(year_list)
print(min(year_list), max(year_list))

print()
for (query_term, count_list) in sorted(query_res_dict.items()):
  print(query_term, count_list)

# -----------------------------------------------------------------------------
# Generate a line plot with number of matches per year
#
w,h = plt.figaspect(2./3)
plt.figure(figsize=(w,h))

title_str = 'Number of matches per year'
plt.title(title_str, fontsize=18)

plt.yscale('log')
plt.xlim(xmin=1979,xmax=2022)
plt.grid()

plt.xlabel('Year', fontsize=16)
plt.ylabel('Number of matches', fontsize=16)

x_plot_list = year_list

# Plot the maximum of the conjuncted F-measure query counts
#
fm_or_max_count_list = [0]*len(year_list)

for query_term in fm_or_query_term_list:
  query_term_count_list = query_res_dict[query_term]
  for (i,count) in enumerate(query_term_count_list):
    fm_or_max_count_list[i] = max(fm_or_max_count_list[i], count)
print(fm_or_max_count_list)

# Don't plot the last year due to incomplete counts
#
#plt.plot(x_plot_list[:-1], fm_or_max_count_list[:-1], color = 'k',
#             linewidth=3, label='All F-measure terms')
plt.plot(x_plot_list, fm_or_max_count_list, color = 'k',
             linewidth=3, label='All F-measure terms')

# Plot all the other non F-measure counts
#
other_query_term_list = list(set(all_query_term_list) - \
          set(fm_query_term_list) - set(fm_or_query_term_list))
print(other_query_term_list)

for other_query_term in sorted(other_query_term_list):

  # Don't plot those in the black list
  #
  if other_query_term not in black_list:
    query_term_count_list = query_res_dict[other_query_term]

    label_str = other_query_term.replace('+', ' ').capitalize()
    label_str = label_str.replace('auc', 'AUC').replace('Auc', 'AUC')
    label_str = label_str.replace('roc', 'ROC')

    if ('Error' in label_str):
      label_str = 'Error/misclassification rate'

    # Don't plot the last year due to incomplete counts
    #
    #plt.plot(x_plot_list[:-1], query_term_count_list[:-1], #color = '#777777',
    #         linewidth=2, label=label_str)
    plt.plot(x_plot_list, query_term_count_list, #color = '#777777',
             linewidth=2, label=label_str)

plt.legend(loc="lower right", fontsize=12, borderpad=0.5, ncol=1,
           labelspacing=0.25)

#plt.savefig('f-measure-google-scholar-change-abs-%s.svg' % (today_str),
#            bbox_inches='tight')
plt.savefig('f-measure-google-scholar-change-abs-%s.eps' % (today_str),
            bbox_inches='tight')

# -----------------------------------------------------------------------------
# Generate a percentage plot of F-measure over all measures
#
w,h = plt.figaspect(2./3)
plt.figure(figsize=(w,h))

#title_str = 'Percentage F-measure matches versus all measures'
title_str = 'F-measure matches versus all measures'
plt.title(title_str, fontsize=18) # , fontsize=22)

plt.xlim(xmin=1979,xmax=2022)
plt.ylim(ymin=-0.5, ymax=8.5)
plt.grid()

plt.xlabel('Year', fontsize=16)
plt.ylabel('Percentage', fontsize=16)

x_plot_list = year_list

all_count_list = [0]*len(year_list)

# Get counts for all measures
#
for query_term in query_res_dict:

  if (query_term not in black_list):  # Except those in black list

    query_term_count_list = query_res_dict[query_term]
    assert len(query_term_count_list) == len(all_count_list)
    for i in range(len(query_term_count_list)):
      all_count_list[i] += query_term_count_list[i]

# First draw all individual F-measure terms
#
for query_term in fm_query_term_list:
  fm_count_list = query_res_dict[query_term]

  print(query_term)
  print(fm_count_list)

  perc_list = []
  assert len(all_count_list) == len(fm_count_list)

  for (i, all_count) in enumerate(all_count_list):
    perc_list.append(100.0*float(fm_count_list[i])/ all_count)
  print(perc_list)
  print()

  # Don't plot the last year due to incomplete counts
  #
  #plt.plot(x_plot_list[:-1], perc_list[:-1], linewidth=2,
  #           label=query_term.capitalize())
  plt.plot(x_plot_list, perc_list, linewidth=2,
           label=query_term.capitalize())

# Plot the maximum of the conjuncted F-measure query counts
#
fm_or_max_count_list = [0]*len(year_list)

for query_term in fm_or_query_term_list:
  query_term_count_list = query_res_dict[query_term]
  for (i,count) in enumerate(query_term_count_list):
    fm_or_max_count_list[i] = max(fm_or_max_count_list[i], count)
print(fm_or_max_count_list)

perc_list = []
for (i, all_count) in enumerate(all_count_list):
  perc_list.append(100.0*float(fm_or_max_count_list[i]) / all_count)
print(perc_list)
print()

#plt.plot(x_plot_list[:-2], perc_list[:-2], color = 'k',
#             linewidth=3, label='All F-measure terms')

plt.legend(loc="upper left", fontsize=12, borderpad=0.5, ncol=1,
           labelspacing=0.25)

#plt.savefig('google-scholar-percentage-%s.svg' % (today_str),
#            bbox_inches='tight')
plt.savefig('google-scholar-percentage-%s.eps' % (today_str),
            bbox_inches='tight')

# End.
