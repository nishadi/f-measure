import csv
import logging
import scholarly

QUERY_LIST = ['"error+rate"', '"misclassification+rate"',
              '"positive+predictive+value"',
              '"false+discovery+rate"', '"precision-recall"',
              '"area+under+curve"', '"area+under+the+curve"',
              '"receiver+operating+characteristic"',
              '"auc"+AND+"roc"', '"auc"+AND+"precision"+AND+"recall"',
              '"f-measure"', '"f1-measure"', '"f-score"', '"f1-score"',
              '"f-measure"+OR+"f1-measure"', '"f-measure"+OR+"f-score"',
              '"f-measure"+OR+"f1-score"', '"f1-measure"+OR+"f-score"',
              '"f1-measure"+OR+"f1-score"', '"f-score"+OR+"f1-score"',
              '"f-measure"+OR+"f1-measure"+OR+"f-score"',
              '"f-measure"+OR+"f1-measure"+OR+"f1-score"',
              '"f-measure"+OR+"f-score"+OR+"f1-score"',
              '"f1-measure"+OR+"f-score"+OR+"f1-score"',
              '"f-measure"+OR+"f1-measure"+OR+"f-score"+OR+"f1-score"']

START_YEAR = 1980
END_YEAR = 2022

# Output file name
CSV_FILE = 'out/google-scholar-query-counts-20230409.csv'

# Google scholar URL with query parameter, start year, end year, with no
# patent flag enabled by `as_sdt=1,5`
#
URL = '/scholar?as_sdt=1,5&q={}&hl=en&as_ylo={}&as_yhi={}'


def __retrieve_gs_results_count__(query, start_year, end_year):
  """
  Method to retrieve result count for a given query with a start year,
  end year, without patent results.

  This method retrieves the BeautifulSoup for a page on scholar.google.com
  using the scholarly library and passes the html page to get the result count.
  The result count is specified in the HTML tag  'gs_ab_mdw'.

  :param query: Query string
  :param start_year: Start year
  :param end_year: End year
  :return: The results count
  """

  url = URL.format(query, start_year, end_year)
  soup = scholarly.get_soup_pubs_custom_url(url)

  # Iterating through the 'gs_ab_mdw' tags
  #
  for row in soup.find_all('div', 'gs_ab_mdw'):
    if len(row.contents) > 0:

      # Inspecting the contents
      str_contents = str(row.contents[0])

      # With the results spanning multiple pages, the term starts with 'About'
      #
      if 'About' in str_contents:
        tokens = str_contents.split(' ')
        return tokens[1]

      # With the results in a single page the term does not start with 'About'
      #
      elif 'results' in str_contents or 'result' in str_contents:
        return str_contents.split(' ')[0]
  return 0


def persist_gs_query_result_counts(query_list, start_year, end_year):
  """
  This method iterates through the query list for each year stated between
  the `start_year` and `end_year` and persists the result counts in the
  `CSV_FILE`.
  (the range is [start_year, start_year+1, ..., end_year]).

  :param query_list: List of queries
  :param start_year: Start year
  :param end_year: End year
  """
  logging.info('Started querying')
  with open(CSV_FILE, 'a') as f:

    writer = csv.writer(f)
    writer.writerow(['query', 'year', 'count'])

    for query in query_list:
      for year in range(start_year, end_year + 1):
        logging.info('Query %s for year %s' % (query, year))
        print('Query %s for year %s' % (query, year))
        count = __retrieve_gs_results_count__(query, year, year)
        logging.info('\t%s result(s)' % count)
        writer.writerow([query, year, count])

if __name__ == '__main__':
  log_file_name = 'out/gs-query.log'
  logging.basicConfig(filename=log_file_name, level=logging.INFO, filemode='w')

  persist_gs_query_result_counts(QUERY_LIST, START_YEAR, END_YEAR)
