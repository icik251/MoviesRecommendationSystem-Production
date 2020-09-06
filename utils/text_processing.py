from ast import literal_eval
from nltk.stem import PorterStemmer
from rake_nltk import Rake
from nltk.corpus import wordnet as wn
import string
import en_core_web_sm


class TextProcessing:
    def __init__(self):
        "tag only PERSON"1
        self.dict_of_NE = {'PERSON': ''}
        """custom stop words list"""
        self.stop_words = ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any",
                           "are", "aren",
                           "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
                           "but", "by",
                           "can", "thing"
                                  "couldn", "couldn't", "d", "did", "didn", "didn't", "do", "does", "doesn", "doesn't",
                           "doing", "don",
                           "don't",
                           "down", "during", "each", "few", "for", "from", "further", "had", "hadn", "hadn't", "has",
                           "hasn",
                           "hasn't",
                           "have", "haven", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
                           "himself", "his",
                           "how",
                           "i", "if", "in", "into", "is", "isn", "isn't", "it", "it's", "its", "itself", "just", "ll",
                           "m", "ma",
                           "me",
                           "mightn", "mightn't", "more", "most", "mustn", "mustn't", "my", "myself", "needn", "needn't",
                           "no", "nor",
                           "not",
                           "now", "o", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
                           "out", "over",
                           "own",
                           "re", "s", "same", "shan", "shan't", "she", "she's", "should", "should've", "shouldn",
                           "shouldn't", "so",
                           "some",
                           "such", "t", "than", "that", "that'll", "the", "their", "theirs", "them", "themselves",
                           "then", "there",
                           "these",
                           "they", "this", "those", "through", "to", "too", "under", "until", "up", "ve", "very", "was",
                           "wasn",
                           "wasn't",
                           "we", "were", "weren", "weren't", "what", "when", "where", "which", "while", "who", "whom",
                           "why", "will",
                           "with", "won", "won't", "wouldn", "wouldn't", "y", "you", "you'd", "you'll", "you're",
                           "you've", "your",
                           "yours",
                           "yourself", "yourselves", "could", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll",
                           "i'm",
                           "i've",
                           "let's", "ought", "she'd", "she'll", "that's", "there's", "they'd", "they'll", "they're",
                           "they've",
                           "we'd",
                           "we'll", "we're", "we've", "what's", "when's", "where's", "who's", "why's", "would", "able",
                           "abst",
                           "accordance", "according", "accordingly", "across", "act", "actually", "added", "adj",
                           "affected",
                           "affecting",
                           "affects", "afterwards", "ah", "almost", "alone", "along", "already", "also", "although",
                           "always",
                           "among",
                           "amongst", "announce", "another", "anybody", "anyhow", "anymore", "anyone", "anything",
                           "anyway",
                           "anyways",
                           "anywhere", "apparently", "approximately", "arent", "arise", "around", "aside", "ask",
                           "asking", "auth",
                           "available", "away", "awfully", "b", "back", "became", "become", "becomes", "becoming",
                           "beforehand",
                           "begin",
                           "beginning", "beginnings", "begins", "behind", "beside", "besides", "beyond",
                           "biol", "brief",
                           "briefly", "c", "ca", "came", "cannot", "can't", "cause", "causes", "certain", "certainly",
                           "co", "com",
                           "come",
                           "comes", "contain", "containing", "contains", "couldnt", "date", "different", "done",
                           "downwards", "due",
                           "e",
                           "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "end",
                           "ending", "enough",
                           "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything",
                           "everywhere",
                           "except", "f", "far", "ff", "fifth", "first", "five", "fix", "former",
                           "formerly", "forth", "found", "four", "furthermore", "g", "gave", "get", "gets", "getting",
                           "give",
                           "given",
                           "gives", "giving", "go", "goes", "gone", "got", "gotten", "h", "happens", "hardly", "hed",
                           "hence",
                           "hereafter",
                           "hereby", "herein", "heres", "hereupon", "hes", "hi", "hid", "hither", "home", "howbeit",
                           "however",
                           "hundred",
                           "id", "ie", "im", "immediate", "immediately", "importance", "important", "inc", "indeed",
                           "index",
                           "information",
                           "instead", "inward", "itd", "it'll", "j", "k", "keep", "keeps", "kept", "kg",
                           "km", "know",
                           "known",
                           "knows", "l", "largely", "last", "lately", "later", "latter", "latterly", "least", "less",
                           "lest", "let",
                           "lets",
                           "like", "liked", "likely", "line", "little", "'ll", "look", "looking", "looks", "ltd",
                           "made", "mainly",
                           "make",
                           "makes", "many", "may", "maybe", "mean", "means", "meantime", "meanwhile", "merely", "mg",
                           "might",
                           "million",
                           "miss", "ml", "moreover", "mostly", "mr", "mrs", "much", "mug", "must", "n", "na", "name",
                           "namely",
                           "nay", "nd",
                           "near", "nearly", "necessarily", "necessary", "need", "needs", "neither", "never",
                           "nevertheless", "new",
                           "next",
                           "nine", "ninety", "nobody", "non", "none", "nonetheless", "noone", "normally", "nos",
                           "noted", "nothing",
                           "nowhere", "obtain", "obtained", "obviously", "often", "oh", "ok", "okay", "old", "omitted",
                           "one",
                           "ones",
                           "onto", "ord", "others", "otherwise", "outside", "overall", "owing", "p", "page", "pages",
                           "part",
                           "particular",
                           "particularly", "past", "per", "perhaps", "placed", "please", "plus", "poorly", "possible",
                           "possibly",
                           "potentially", "pp", "predominantly", "present", "previously", "primarily", "probably",
                           "promptly",
                           "provides", "put", "q", "que", "quickly", "quite", "qv", "r", "ran", "rather", "rd",
                           "readily", "really",
                           "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related",
                           "relatively",
                           "respectively", "resulted", "resulting", "results", "right", "run", "said", "saw", "say",
                           "saying",
                           "says",
                           "sec", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self",
                           "selves", "sent",
                           "seven", "several", "shall", "shed", "shes", "show", "showed", "shown", "showns", "shows",
                           "significant",
                           "significantly", "similar", "similarly", "since", "six", "slightly", "somebody", "somehow",
                           "someone",
                           "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry",
                           "specifically",
                           "specified", "specify", "specifying", "still", "stop", "strongly", "sub", "substantially",
                           "successfully",
                           "sufficiently", "suggest", "sup", "sure", "take", "taken", "taking", "tell", "tends", "th",
                           "thank",
                           "thanks",
                           "thanx", "thats", "that've", "thence", "thereafter", "thereby", "thered", "therefore",
                           "therein",
                           "there'll",
                           "thereof", "therere", "theres", "thereto", "thereupon", "there've", "theyd", "theyre",
                           "think", "thou",
                           "though",
                           "thoughh", "thousand", "throug", "throughout", "thru", "thus", "til", "tip", "together",
                           "took", "toward",
                           "towards", "tried", "tries", "truly", "try", "trying", "ts", "twice", "two", "u", "un",
                           "unfortunately",
                           "unless", "unlike", "unlikely", "unto", "upon", "ups", "us", "use", "used", "useful",
                           "usefully",
                           "usefulness",
                           "uses", "using", "usually", "v", "value", "various", "'ve", "via", "viz", "vol", "vols",
                           "vs", "w",
                           "want",
                           "wants", "wasnt", "way", "wed", "welcome", "went", "werent", "whatever", "what'll", "whats",
                           "whence",
                           "whenever", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever",
                           "whether",
                           "whim",
                           "whither", "whod", "whoever", "whole", "who'll", "whomever", "whos", "whose", "widely",
                           "willing", "wish",
                           "within", "without", "wont", "words", "world", "wouldnt", "www", "x", "yes", "yet", "youd",
                           "youre", "z",
                           "zero",
                           "a's", "ain't", "allow", "allows", "apart", "appear", "appreciate", "appropriate",
                           "associated", "best",
                           "better", "c'mon", "c's", "cant", "changes", "clearly", "concerning", "consequently",
                           "consider",
                           "considering",
                           "corresponding", "course", "currently", "definitely", "described", "despite", "entirely",
                           "exactly",
                           "example", "well", "film", "story", "set", "year", "time", "man",
                           "going", "greetings", "hello", "help", "hopefully", "ignored", "inasmuch", "indicate",
                           "indicated",
                           "indicates",
                           "inner", "insofar", "it'd", "keep", "keeps", "novel", "presumably", "reasonably", "second",
                           "secondly",
                           "sure", "t's", "third", "thorough", "thoroughly",
                           "three"]
        self.nlp_spacy = en_core_web_sm.load()
        """I add punctuation symbols by hand so I can append this special symbol '–' which is not the ordinary '-' """
        self.list_of_punct_symbols = list(string.punctuation)
        self.list_of_punct_symbols.append('–')
        self.list_of_punct_symbols.append('’')

        """Create rake obj that will extract keywords for us. Setting pucntuation list, stopwords list and 
        the max length for extracted keywords"""
        self.rake = Rake(punctuations=self.list_of_punct_symbols,
                         max_length=3,
                         stopwords=self.stop_words)

        """Create stemmer """
        self.porter_stemmer = PorterStemmer()

    def _format_person_entity(self, person_entity):
        """reformat the person entity in the right format for checking"""
        return person_entity.translate(str.maketrans('', '', ''.join(self.list_of_punct_symbols))).lower()

    @staticmethod
    def convert_string_list_to_object_list(list_to_check):
        if isinstance(list_to_check, str):
            return literal_eval(list_to_check)
        else:
            return list_to_check

    def clear_keywords_overview(self, text, list_of_keywords):
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        """Remove punctuation symbols if something is left and 'amp' because this is ampersand and goes like &amp;"""
        for index, keyword in enumerate(list_of_keywords):
            list_of_keywords[index] = keyword.translate(
                str.maketrans('', '', ''.join(self.list_of_punct_symbols))).strip()

            list_of_keyword = keyword.split()
            for index_j, word in enumerate(list_of_keyword):
                if word == 'amp':
                    list_of_keyword.remove(word)

            if list_of_keyword:
                list_of_keywords[index] = ' '.join(list_of_keyword)
            else:
                list_of_keywords.pop(index)

        """remove keywords from list if they are names"""
        doc = self.nlp_spacy(text)

        """name could be part of a 2 or 3-gram keyword"""
        list_of_splitted_keywords = []
        for keyword in list_of_keywords:
            if len(keyword.split()) > 1:
                for subkeyword in keyword.split():
                    list_of_splitted_keywords.append(subkeyword)
            else:
                list_of_splitted_keywords.append(keyword)

        for ent in doc.ents:
            break_reached = False
            if ent.label_ in self.dict_of_NE.keys():
                formatted_person = self._format_person_entity(ent.text)
                if formatted_person in list_of_splitted_keywords:
                    for word in list_of_keywords:
                        if formatted_person in word.split():
                            break_reached = True
                            break
                    if break_reached:
                        list_of_keywords.remove(word)

        return list_of_keywords

    def merge_overview_keywords_and_keywords(self, list_of_overview_keywords, list_of_keywords):
        res_list_of_keywords = []
        res_list_of_overview_keywords = []
        if list_of_keywords is not '':
            res_list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        if list_of_overview_keywords is not '':
            res_list_of_overview_keywords = self.convert_string_list_to_object_list(list_of_overview_keywords)

        merged_list_of_keywords = list(set(res_list_of_keywords + res_list_of_overview_keywords))

        return merged_list_of_keywords

    def extract_keywords_overview(self, text):
        self.rake.extract_keywords_from_text(text)
        list_of_keywords = self.rake.get_ranked_phrases()
        return list_of_keywords

    def create_dict_of_root_keywords(self, df, column='merged_keywords'):
        dict_of_root_keywords = dict()
        # create dictionary with key: root of the word,
        # and value set of all keywords with this root

        for string_list_obj in df[column]:
            if string_list_obj is not '':
                for keyword in self.convert_string_list_to_object_list(string_list_obj):
                    root_keyword = self.porter_stemmer.stem(keyword.lower())
                    if root_keyword in dict_of_root_keywords.keys():
                        dict_of_root_keywords[root_keyword].add(keyword)
                    else:
                        dict_of_root_keywords[root_keyword] = {keyword}

        return dict_of_root_keywords

    @staticmethod
    def choose_best_keyword_for_root(dict_of_root_keywords):
        dict_of_root_selected_keyword = dict()

        for key_root in dict_of_root_keywords.keys():
            """if the set of values contains more than 1 word,
            we check the word with minimum length cuz this is going to be the keyword that we are going to use"""
            if len(dict_of_root_keywords[key_root]) > 1:
                min_length = 500
                for word in dict_of_root_keywords[key_root]:
                    if len(word) < min_length:
                        curr_best_word = word
                        min_length = len(word)

                dict_of_root_selected_keyword[key_root] = curr_best_word
            else:
                dict_of_root_selected_keyword[key_root] = dict_of_root_keywords[key_root].pop()

        return dict_of_root_selected_keyword

    def normalize_keywords(self, list_of_keywords, dict_of_root_selected_keyword):
        set_of_normalized_keywords = set()
        for keyword in literal_eval(list_of_keywords):
            stemmed_keyword = self.porter_stemmer.stem(keyword)
            if stemmed_keyword in dict_of_root_selected_keyword.keys():
                set_of_normalized_keywords.add(dict_of_root_selected_keyword[stemmed_keyword])
            else:
                print('No key {} in dict'.format(stemmed_keyword))
                set_of_normalized_keywords.add(keyword)

        return list(set_of_normalized_keywords)

    def get_synonyms(self, word):
        synonyms_set = set()
        """not 100% right as we don't have the context here"""
        word_original_type = wn.synsets('alien')[0]
        word_original_type = word_original_type.pos()

        for syns in wn.synsets(word):
            for syn_word in syns.lemma_names():
                original_syn_word = syns.name()
                """find the index position of the word type (noun, adj, verb, etc)"""
                """we get only the nouns"""
                word_type = original_syn_word.split('.')[1]
                if word_type == word_original_type:
                    """replacing _ with ' ' cuz some synomyms are separated by _"""
                    synonyms_set.add(syn_word.replace('_', ' ').lower())
        """add the word we are searching syns for"""
        synonyms_set.add(word)
        return synonyms_set

    def find_synonyms_for_list_of_keywords(self, dict_of_keyword_count, list_of_keywords):
        dict_of_keyword_synonyms_count = dict()

        for keyword in list_of_keywords:
            set_of_syns = self.get_synonyms(keyword)
            temp_dict = dict()
            for syn in set_of_syns:
                if syn in dict_of_keyword_count.keys():
                    temp_dict[syn] = dict_of_keyword_count[syn]

            dict_of_keyword_synonyms_count[keyword] = temp_dict

        return dict_of_keyword_synonyms_count

    def _logic_useless_n_gram(self, non_stemmed_token, dict_of_keyword_count):
        stemmed_token = self.porter_stemmer.stem(non_stemmed_token)
        stemmed_count, non_stemmed_count = 0, 0
        if stemmed_token in dict_of_keyword_count.keys():
            stemmed_count = dict_of_keyword_count[stemmed_token]
        if non_stemmed_token in dict_of_keyword_count.keys():
            non_stemmed_count = dict_of_keyword_count[non_stemmed_token]

        if stemmed_count > non_stemmed_count and (stemmed_count > 0 or non_stemmed_count > 0):
            return stemmed_token
        elif stemmed_count <= non_stemmed_count and (stemmed_count > 0 or non_stemmed_count > 0):
            return non_stemmed_token

        return None

    def process_n_grams(self, dict_of_keyword_count, list_of_keywords, count_threshold=1):
        list_of_result_keywords = []
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        for keyword in list_of_keywords:
            if len(keyword.split()) > 1:
                if dict_of_keyword_count[keyword] > count_threshold:
                    list_of_result_keywords.append(keyword)
                else:
                    """split word and try to fit it in the keywords by stemming and finding syns"""
                    for token in keyword.split():
                        processed_token = self._logic_useless_n_gram(token, dict_of_keyword_count)
                        if processed_token:
                            list_of_result_keywords.append(processed_token)

            else:
                """if keyword len is above len 1"""
                if len(keyword) > 1:
                    list_of_result_keywords.append(keyword)

        return list_of_result_keywords

    def process_keywords_with_synonyms(self, dict_of_keyword_count, list_of_keywords, count_threshold=1):
        list_of_result_keywords = []
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        for keyword in list_of_keywords:
            if dict_of_keyword_count[keyword] > count_threshold:
                list_of_result_keywords.append(keyword)
            else:
                chosen_synonym = self._get_best_synonym_from_keywords(dict_of_keyword_count, keyword, count_threshold)
                if chosen_synonym:
                    list_of_result_keywords.append(chosen_synonym)
                    print("{} --> {} : {} count".format(keyword, chosen_synonym, dict_of_keyword_count[chosen_synonym]))

        return list_of_result_keywords

    def final_clean_special_symbols(self, list_of_keywords):
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        res_list_of_keywords = []
        for keyword in list_of_keywords:
            if all(i in self.list_of_punct_symbols for i in keyword):
                continue
            else:
                res_list_of_keywords.append(keyword)

        return res_list_of_keywords

    def _get_best_synonym_from_keywords(self, dict_of_keyword_count, keyword, count_threshold=1):
        set_of_syns = self.get_synonyms(keyword)
        temp_chosen_synonym = None
        for syn in set_of_syns:
            if syn in dict_of_keyword_count.keys():
                if dict_of_keyword_count[syn] > count_threshold:
                    count_threshold = dict_of_keyword_count[syn]
                    temp_chosen_synonym = syn

        return temp_chosen_synonym

    @staticmethod
    def count_words_occurences(df, column=''):
        dict_of_keyword_count = dict()

        for list_obj in df[column]:
            for keyword in list_obj:
                if keyword in dict_of_keyword_count.keys():
                    dict_of_keyword_count[keyword] += 1
                else:
                    dict_of_keyword_count[keyword] = 1

        return dict_of_keyword_count

    def remove_stopwords(self, list_of_keywords):
        list_of_res = []
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        for keyword in list_of_keywords:
            if keyword not in self.stop_words:
                list_of_res.append(keyword)

        return list_of_res

    """format keywords, put + between the keywords that contain more than 1 word,
    and bracket all the keywords with + and return string"""
    def format_keywords(self, list_of_keywords):
        list_of_result = []
        list_of_keywords = self.convert_string_list_to_object_list(list_of_keywords)
        for keyword in list_of_keywords:
            if len(keyword.split()) > 1:
                list_of_result.append(keyword.replace(' ', '+'))
            else:
                if len(keyword) > 1 and str.isalnum(keyword):
                    list_of_result.append('+' + keyword + '+')

        return ' '.join(list_of_result)

