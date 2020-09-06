import pandas as pd
from utils.text_processing import TextProcessing

qualified_movies_df = pd.read_csv('..\\data\\nlp\\normalized_keywords.csv')
qualified_movies_df = qualified_movies_df.fillna('')
print('test')
text_processing_obj = TextProcessing()

"""remove stopwords and create count words occurences"""
qualified_movies_df['normalized_keywords'] = qualified_movies_df['normalized_keywords']. \
    apply(lambda x: text_processing_obj.remove_stopwords(x))
dict_of_keyword_count = text_processing_obj.count_words_occurences(qualified_movies_df, 'normalized_keywords')

"""whats the minimum count for a word to be replaced by synonym or deleted"""
count_threshold = 2

for index, row in qualified_movies_df.iterrows():
    original_keywords = row['keywords']
    original_overview = row['overview']
    print(original_overview)
    list_of_res_keywords = text_processing_obj.process_n_grams(dict_of_keyword_count, row['normalized_keywords'],
                                                               count_threshold=count_threshold)
    list_of_res_keywords_syns = text_processing_obj.process_keywords_with_synonyms(dict_of_keyword_count,
                                                                                   list_of_res_keywords,
                                                                                   count_threshold=count_threshold)

    list_of_res_keywords_syns = text_processing_obj.final_clean_special_symbols(
        list_of_keywords=list_of_res_keywords_syns)

    list_of_res_keywords_syns = list(set(list_of_res_keywords_syns))

    print('List of original keywords:')
    print(original_keywords)
    print('List of result keywords after everything:')
    print(list_of_res_keywords_syns)

    list_of_differences = []
    for keyword in list_of_res_keywords_syns:
        if keyword not in original_keywords:
            list_of_differences.append(keyword)
    print('Differences:')
    print(list_of_differences)
    print('--------------------------------')
    if index == 30:
        break
