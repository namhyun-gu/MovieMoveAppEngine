__author__ = 'namhyun'
from datetime import date, timedelta
import urllib2
import json
import logging
import yaml
import webapp2
from google.appengine.ext import ndb

from urlbuilder import urlbuilder

class KobisApi():
    TYPE_COMMON_CODE = 100
    TYPE_DAILY_BOX_OFFICE = 101
    TYPE_MOVIE_DETAIL_INFO = 102
    TYPE_MOVIE_LIST = 103

    BASE_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest"

    QUERY_CODE = "code"
    QUERY_SEARCH_CODE_LIST = "searchCodeList"
    QUERY_BOXOFFICE = "boxoffice"
    QUERY_SEARCH_DAILY_BOXOFFICE_LIST = "searchDailyBoxOfficeList"
    QUERY_MOVIE = "movie"
    QUERY_SEARCH_MOVIE_INFO = "searchMovieInfo"
    QUERY_SEARCH_MOVIE_LIST = "searchMovieList"
    QUERY_TYPE = ".json"

    API_KEY = "7ffbb106d667ab3ddf34dc7ba8ff2c65"
    PARAM_KEY = "key"
    PARAM_TARGET_DT = "targetDt"
    PARAM_MOVIE_CD = "movieCd"

    paramMovieCd = None

    def __init__(self):
        pass

    def get_url(self, type):
        target_dt = self.get_target_dt()
        builder = urlbuilder(self.BASE_URL)
        if type == self.TYPE_COMMON_CODE:
            builder.append_path(self.QUERY_CODE).append_path(self.QUERY_SEARCH_CODE_LIST + self.QUERY_TYPE)
        elif type == self.TYPE_DAILY_BOX_OFFICE:
            builder.append_path(self.QUERY_BOXOFFICE).append_path(
                self.QUERY_SEARCH_DAILY_BOXOFFICE_LIST + self.QUERY_TYPE).append_query_param(
                self.PARAM_TARGET_DT, target_dt)
        elif type == self.TYPE_MOVIE_DETAIL_INFO:
            if self.paramMovieCd is not None:
                builder.append_path(self.QUERY_MOVIE).append_path(self.QUERY_SEARCH_MOVIE_INFO + self.QUERY_TYPE) \
                    .append_query_param(self.PARAM_MOVIE_CD, self.paramMovieCd)

            else:
                return None
        elif type == self.TYPE_MOVIE_LIST:
            builder.append_path(self.QUERY_MOVIE).append_path(self.QUERY_SEARCH_MOVIE_LIST + self.QUERY_TYPE);
        else:
            return None
        return builder.append_query_param(self.PARAM_KEY, self.API_KEY).build()

    def get_target_dt(self):
        yesterday = date.today() - timedelta(1)
        return yesterday.strftime('%Y%m%d')

    def set_param_moviecd(self, movieCd):
        self.paramMovieCd = movieCd


class TheMovieDbApi():
    TYPE_SEARCH_MOVIE = 100
    TYPE_MOVIE_IMAGE = 101

    BASE_URL = "http://api.themoviedb.org/3"
    QUERY_SEARCH = "search"
    QUERY_MOVIE = "movie"
    QUERY_IMAGES = "images"

    API_KEY = "848790748cc5407875ba6ae106a18f24"  # It is test key!
    PARAM_KEY = "api_key"
    PARAM_QUERY = "query"
    PARAM_LANGUAGE = "language"

    paramId = None
    paramLanguage = None
    paramQuery = None

    def __init__(self):
        pass

    def get_url(self, type):
        builder = urlbuilder(self.BASE_URL)
        if type == self.TYPE_MOVIE_IMAGE:
            if self.paramId is not None and self.paramLanguage is not None:
                builder.append_path(self.QUERY_MOVIE).append_path(self.paramId) \
                    .append_path(self.QUERY_IMAGES).append_query_param(self.PARAM_LANGUAGE, self.paramLanguage)
            else:
                return None
        elif type == self.TYPE_SEARCH_MOVIE:
            if self.paramQuery is not None:
                builder.append_path(self.QUERY_SEARCH).append_path(self.QUERY_MOVIE).append_query_param(
                    self.PARAM_QUERY,
                    self.paramQuery)
            else:
                return None
        else:
            return None
        return builder.append_query_param(self.PARAM_KEY, self.API_KEY).build()

    def set_param_id(self, id):
        self.paramId = id

    def set_param_language(self, language):
        self.paramLanguage = language

    def set_param_query(self, query):
        self.paramQuery = query


class ResultBean():
    rank = None
    rankInten = None
    rankOldAndNew = None
    movieNm = None
    openDt = None
    audiCnt = None
    audiInten = None
    audiAcc = None
    thumbnailUrl = None
    detail = None

    def __init__(self):
        pass


class DetailBean():
    showTm = None
    genreNm = None
    watchGradeNm = None

    def __init__(self):
        pass


class DataBean(ndb.Model):
    date = ndb.StringProperty(repeated=False, required=True)
    data = ndb.JsonProperty(required=True)


class MovieMoveHandler(webapp2.RedirectHandler):
    # Kobis API
    KEY_BOX_OFFICE_RESULT = "boxOfficeResult"
    KEY_DAILY_BOX_OFFICE_LIST = "dailyBoxOfficeList"

    KEY_RANK = "rank"
    KEY_RANK_INTEN = "rankInten"
    KEY_RANK_OLD_AND_NEW = "rankOldAndNew"
    KEY_MOVIE_NM = "movieNm"
    KEY_OPEN_DT = "openDt"
    KEY_AUDI_CNT = "audiCnt"
    KEY_AUDI_INTEN = "audiInten"
    KEY_AUDI_ACC = "audiAcc"
    KEY_MOVIE_CD = "movieCd"

    # (Detail)
    KEY_MOVIE_INFO_RESULT = "movieInfoResult"
    KEY_MOVIE_INFO = "movieInfo"

    KEY_SHOW_TM = "showTm"
    KEY_GENRES = "genres"
    KEY_GENRE_NM = "genreNm"
    KEY_AUDITS = "audits"
    KEY_WATCH_GRADE_NM = "watchGradeNm"

    # The Movie DB API
    KEY_RESULTS = "results"
    KEY_ID = "id"
    KEY_POSTER_PATH = "poster_path"

    def get(self):
        json_result_content = None
        if self.is_data_exist() == False:
            logging.info("DATA NOT EXIST!")
            json_result_content = self.fetch_data()
            self.save_content(self.get_date(), json_result_content)
        else:
            logging.info("DATA EXIST!")
            json_result_content = self.fetch_data_from_ndb()
        self.response.headers['content-Type'] = 'application/json'
        self.response.out.write(json_result_content)
        # self.response.write(kobis_json_object[self.OBJECT_BOX_OFFICE_RESULT][self.ARRAY_DAILY_BOX_OFFICE_LIST])
        # URL encoding handling http://cpeter7.blogspot.kr/2008/11/urllib-unicode-handling.html

    def get_date(self):
        caculateDate = date.today() - timedelta(1)
        savedDate = caculateDate.strftime('%Y%m%d')
        return savedDate

    def fetch_data(self):
        kobis_url = KobisApi().get_url(KobisApi.TYPE_DAILY_BOX_OFFICE)
        kobis_responce = urllib2.urlopen(kobis_url)
        kobis_content = unicode(kobis_responce.read(), "utf-8")
        kobis_json_object = yaml.load(kobis_content)

        kobis_daily_boxoffice_array = kobis_json_object[self.KEY_BOX_OFFICE_RESULT][self.KEY_DAILY_BOX_OFFICE_LIST]
        results = []
        for result_object in kobis_daily_boxoffice_array:
            bean = ResultBean()
            bean.rank = result_object[self.KEY_RANK]
            bean.rankInten = result_object[self.KEY_RANK_INTEN]
            bean.rankOldAndNew = result_object[self.KEY_RANK_OLD_AND_NEW]
            bean.movieNm = result_object[self.KEY_MOVIE_NM]
            bean.openDt = result_object[self.KEY_OPEN_DT]
            bean.audiCnt = result_object[self.KEY_AUDI_CNT]
            bean.audiInten = result_object[self.KEY_AUDI_INTEN]
            bean.audiAcc = result_object[self.KEY_AUDI_ACC]

            kobis_api = KobisApi()
            kobis_api.set_param_moviecd(result_object[self.KEY_MOVIE_CD])
            kobis_url = kobis_api.get_url(KobisApi.TYPE_MOVIE_DETAIL_INFO)

            kobis_responce = urllib2.urlopen(kobis_url)
            kobis_content = unicode(kobis_responce.read(), "utf-8")
            kobis_json_object = yaml.load(kobis_content)
            kobis_detail_object = kobis_json_object[self.KEY_MOVIE_INFO_RESULT][self.KEY_MOVIE_INFO]

            result_detail_object = DetailBean()
            result_detail_object.showTm = kobis_detail_object[self.KEY_SHOW_TM]
            result_detail_object.watchGradeNm = kobis_detail_object[self.KEY_AUDITS][0][self.KEY_WATCH_GRADE_NM]
            genreArray = []
            result_detail_object_genre_array = kobis_detail_object[self.KEY_GENRES]
            for result_detail_object_genre_object in result_detail_object_genre_array:
                genreArray.append(result_detail_object_genre_object[self.KEY_GENRE_NM])
                result_detail_object.genreNm = genreArray
            bean.detail = result_detail_object

            try:
                the_movie_db = TheMovieDbApi()
                the_movie_db.set_param_query(result_object[self.KEY_MOVIE_NM].replace(" ", "%20"))
                the_movie_db_url = the_movie_db.get_url(TheMovieDbApi.TYPE_SEARCH_MOVIE)
                the_movie_db_responce = urllib2.urlopen(the_movie_db_url)
                the_movie_db_content = unicode(the_movie_db_responce.read(), "utf-8")
                the_movie_db_json_object = yaml.load(the_movie_db_content)

                if the_movie_db_json_object[self.KEY_RESULTS][0][self.KEY_ID] is "":
                    results.append(bean)
                    continue

                bean.thumbnailUrl = the_movie_db_json_object[self.KEY_RESULTS][0][self.KEY_POSTER_PATH]
                results.append(bean)
            except IndexError, err:
                bean.thumbnailUrl = "null"
                results.append(bean)
            except urllib2.HTTPError, err:
                if err.code == 400:
                    bean.thumbnailUrl = "null"
                    results.append(bean)
        return json.dumps(results, ensure_ascii=False, default=lambda o: o.__dict__)

    def is_data_exist(self):
        entity = DataBean.query(DataBean.date == self.get_date()).fetch()
        if len(entity) != 0:
            return True
        else:
            return False

    def fetch_data_from_ndb(self):
        entity = DataBean.query(DataBean.date == self.get_date()).fetch()
        return entity[0].data

    def save_content(self, contentDate, contentData):
        dataModel = DataBean(date=contentDate, data=contentData)
        dataModel.put()