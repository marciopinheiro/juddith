#  Copyright (c) 2019. Marcio Pinheiro. This Item is protected by copyright
#  and/or related rights. You are free to use this Item in any way that is
#  permitted by the copyright and related rights legislation that applies to
#  your use. For other uses you need to obtain permission from the
#  rights-holder(s).

import os
import logging
import datetime
import time
import contextlib
import unidecode
import pandas as pd
import numpy as np
import nltk
import joblib
import dropbox

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from application.models import Elocution


@contextlib.contextmanager
def watch_time(message, logger):
    """
    Context manager to print how long a block of code took.
    :param message:
    :param logger:
    :return:
    """
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        logger.info(f'Total elapsed time for {message}: {(t1 - t0):.2f}')


class FileManager:

    _logger = logging.getLogger('default')
    client = None

    def __init__(self):
        """
        Init class setting the storage and log clients.
        """
        self.client = dropbox.Dropbox(settings.DROPBOX_OAUTH2_TOKEN)
        self._logger.info(f'{self.client.__class__.__name__} was setted as '
                          f'client to web storage')

    @staticmethod
    def get_tempdir_path():
        """
        Get a temp root directory of OS.
        :return:
        """
        import tempfile
        return tempfile.gettempdir()

    def upload(self, filename, key):
        """
        Upload files to default online storage.
        :param filename:
        :param key:
        :return:
        """
        self._logger.info(f'Uploading {key} '
                          f'to {self.client.__class__.__name__}')
        c = self.client
        path = settings.DROPBOX_PATHS.get('keys').get(key)
        mtime = os.path.getmtime(filename)

        with open(filename, 'rb') as l_file:
            data = l_file.read()

        with watch_time(f'upload {len(data)} bytes', self._logger):

            try:
                client_modified = datetime.datetime(*time.gmtime(mtime)[:6])
                c.files_upload(data, '/' + path,
                               dropbox.files.WriteMode.overwrite,
                               client_modified=client_modified,
                               mute=True)

            except dropbox.exceptions.ApiError as err:
                self._logger.error('*** DROPBOX API error', err)

                return None

    def download(self, filename, key):
        """
        Download files from default online storage.
        :param filename:
        :param key:
        :return:
        """
        self._logger.info(f'Downloading {key} '
                          f'from {self.client.__class__.__name__}')

        with watch_time(f'download {filename}', self._logger):
            c = self.client
            path = settings.DROPBOX_PATHS.get('keys').get(key)
            md, res = c.files_download('/' + path)

            with open(filename, 'wb') as l_file:
                l_file.write(res.content)

    def load(self, key):
        """
        Load fitting classes on files.
        :param key:
        :return:
        """
        filename = os.path.join(self.get_tempdir_path(), key + '.joblib')

        if not os.path.exists(filename):
            self.download(filename, key)

        else:
            self._logger.info(f'File {filename} exists, '
                              f'and will not be downloaded')

        self._logger.info(f'Loading {filename}')

        return joblib.load(filename)

    def dump(self, obj, key):
        """
        Dump fitting classes into files.
        :param obj:
        :param key:
        :return:
        """
        filename = os.path.join(self.get_tempdir_path(), key + '.joblib')
        self._logger.info(f'Dumping {obj.__class__.__name__} into {filename}')
        joblib.dump(obj, filename)
        self.upload(filename, key)


class Preprocessor:

    _logger = logging.getLogger('default')
    _dictionary = []

    @staticmethod
    def remove_stopwords(elocution_words):
        """
        Remover of stop words
        :param elocution_words:
        :return:
        """
        import string
        # stopwords_list = list()
        stopwords_list = nltk.corpus.stopwords.words('portuguese')
        stopwords_list.append(':data:')

        return [w for w in elocution_words if w not in stopwords_list
                and w not in string.punctuation]

    @staticmethod
    def steamming_words(elocution_words):
        """
        Stemmer of words
        :param elocution_words:
        :return:
        """
        # stemmer = nltk.stem.SnowballStemmer('portuguese')
        stemmer = nltk.stem.RSLPStemmer()

        return [str(stemmer.stem(w)) for w in elocution_words]

    def preprocess_words(self, elocution):
        """
        Pre-processor of words
        :param elocution:
        :return:
        """
        elocution = unidecode.unidecode(elocution)
        elocution = elocution.lower()
        elocution_words = nltk.word_tokenize(elocution)
        elocution_words = self.remove_stopwords(elocution_words)
        elocution_words = self.steamming_words(elocution_words)

        self._logger.info(f'Elocution words: {elocution_words}')

        return elocution_words

    def convert_to_features(self, elocution_words, dictionary, target=None):
        """
        Conversor the words into features to train or predict
        :param elocution_words:
        :param dictionary:
        :param target:
        :return:
        """
        self._dictionary = dictionary
        features = self.get_features(elocution_words)

        if target:
            features['target'] = target

        return features

    def get_features(self, elocution_words):
        """
        Get words as features to train or predict.
        :param elocution_words:
        :return:
        """
        terms = set(elocution_words)
        data = {}

        for w in self._dictionary:
            data[w] = (w in terms)

        return data


class Trainer:

    _logger = logging.getLogger('default')
    _df = None
    _dictionary = []
    _classifier = None
    _columns = ['target']

    @staticmethod
    def get_new_classifier():
        """
        Get a new classifier instance.
        :return:
        """
        from sklearn.neural_network import MLPClassifier
        return MLPClassifier(verbose=True, max_iter=1000, tol=0.000010)

    def __init__(self):
        self.make_df()

        file_manager = FileManager()
        df_filename = os.path.join(file_manager.get_tempdir_path(),
                                   'dataframe.csv')
        self._df.to_csv(df_filename, index=False)
        file_manager.upload(df_filename, 'dtf')

    def make_df(self):
        """
        Make a train dataframe with database data.
        :return:
        """
        raw_data = []

        try:
            self._logger.info('Getting data to make a dataframe')
            elocutions_all = Elocution.objects.filter(status=1)

            self._logger.info(f'Found {len(elocutions_all)} elocution(s)')

            for elocution in elocutions_all:

                if elocution.intent is not None:
                    raw_data.append((self.preprocess_df(elocution.text),
                                     elocution.intent.tag))

            self._dictionary = list(nltk.FreqDist(self._dictionary).keys())

            preprocess = Preprocessor()
            features_data = []

            for d in raw_data:
                features_data.append(
                    preprocess.convert_to_features(d[0],
                                                   self._dictionary, d[1])
                )

            self._df = pd.DataFrame(data=features_data,
                                    columns=(self._dictionary + self._columns))
            self._logger.info('Dataframe generated successfully')

        except ObjectDoesNotExist:
            self._logger.error('No elocutions found')

    def preprocess_df(self, elocution):
        """
        Process the train dataframe.
        :param elocution:
        :return:
        """
        preprocess = Preprocessor()
        elocution_words = preprocess.preprocess_words(elocution)

        for w in elocution_words:
            self._dictionary.append(w)

        return elocution_words

    def fit(self):
        """
        Train the classifier.
        :return:
        """
        self.set_classifier()

        features_to_train = self._df.iloc[:, 0:-1]
        target_to_train = self._df.target

        self._classifier.fit(features_to_train, target_to_train)
        self._logger.info('Classifier trained successfully')

        self.generate_confusion_matrix(test_size=0.25)

    def set_classifier(self):
        """
        Set classifier instance to class property.
        :return:
        """
        self._classifier = self.get_new_classifier()
        self._logger.info(f'The classifier '
                          f'is: {self._classifier.__class__.__name__}')

    def generate_confusion_matrix(self, test_size=0.25):
        """
        Generate a confusion matrix based on train tests.
        :param test_size:
        :return:
        """
        import copy
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import confusion_matrix

        features = self._df.iloc[:, 0:-1]
        target = self._df.target

        x_train, x_test, y_train, y_test = train_test_split(features, target,
                                                            test_size=test_size,
                                                            random_state=0)

        clf = copy.copy(self.get_new_classifier())
        clf.fit(x_train, y_train)
        predictions = self._classifier.predict(x_test)

        cm_df = pd.DataFrame(confusion_matrix(y_test, predictions,
                                              labels=clf.classes_),
                             columns=clf.classes_,
                             index=clf.classes_)

        self._logger.info('Confusion matrix generated successfully')

        self.generate_confusion_matrix_graph(cm_df)

    def generate_confusion_matrix_graph(self, cm_df):
        """
        Generate a graph image with results of confusion matrix.
        :param cm_df:
        :return:
        """
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt

        target_hits = []
        target_mistakes = []

        for classe in cm_df.columns:
            target_hits.append(cm_df.loc[classe, classe])
            target_mistakes.append(sum(cm_df.loc[classe,
                                                 cm_df.columns != classe]))

        ind = np.arange(len(cm_df.columns))  # the x locations for the groups
        width = 0.75  # the width of the bars: can also be len(x) sequence

        p1 = plt.bar(ind, target_hits, width)
        p2 = plt.bar(ind, target_mistakes, width, bottom=target_hits)

        plt.ylabel('Scores')
        plt.title('Scores classification by target')
        plt.xticks(ind, cm_df.columns, rotation='vertical')
        plt.yticks(np.arange(0, cm_df.max().max() * 1.3))
        plt.legend((p1[0], p2[0]), ('hit', 'mistake'))

        self._logger.info('Confusion matrix graph generated successfully')

        file_manager = FileManager()
        graph_filename = os.path.join(file_manager.get_tempdir_path(),
                                      'confusion_matrix.png')
        plt.savefig(graph_filename, bbox_inches='tight')
        file_manager.upload(graph_filename, 'gph')

    def persist(self):
        """
        Persist the dictionary and trained classifier on storage.
        :return:
        """
        file_manager = FileManager()
        file_manager.dump(self._classifier, 'clf')
        file_manager.dump(self._dictionary, 'dic')


class Predictor:

    _logger = logging.getLogger('default')
    _classifier = None
    _dictionary = None

    def __init__(self):

        try:
            file_manager = FileManager()
            self._classifier = file_manager.load('clf')
            self._dictionary = file_manager.load('dic')

        except OSError:
            self._logger.error('No classifier found in defined path. '
                               'Execute de train program.')

    def get_prediction(self, data):
        """
        Get predition of given data.
        :param data:
        :return:
        """
        with watch_time(f'prediction of {data} ', self._logger):

            try:
                preprocessor = Preprocessor()
                data = preprocessor.preprocess_words(data)
                data = preprocessor.convert_to_features(data, self._dictionary)
                df = pd.DataFrame(data=[data], columns=self._dictionary,
                                  index=None)
                results = self._classifier.predict_proba(df)[0]
                probabilities = [x for x in map(lambda x: (x/sum(results))*100,
                                                results)]
                p_index = np.argsort(probabilities)[::-1]

                if probabilities[p_index[0]] > 40:
                    self._logger.info('The probability of prediction is strong '
                                      'and will match a target')
                    predicted_target = self._classifier.classes_[p_index[0]]
                    self._logger.info(f'The prediction is: '
                                      f'{predicted_target} with '
                                      f'{(probabilities[p_index[0]]):.2f}%')

                    return predicted_target
                self._logger.info('The probability of prediction is poorly '
                                  'and cannot match a target')

                for i, target in enumerate(probabilities):
                    self._logger.info(f'The prediction is: '
                                      f'{self._classifier.classes_[i]} with '
                                      f'{(probabilities[i]):.2f}%')

                return 'not_found'

            except AttributeError as e:
                self._logger.error('The prediction cannot be done because '
                                   'the data cannot be None')
                self._logger.error(str(e))
