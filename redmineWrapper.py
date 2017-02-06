from redmine import Redmine
import config
import docxbuilder
import os
from consts import RedmineConsts, Parsing, ParseType
import shutil
import re


class RedmineWrapper():
    # папка с вложенияеми
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

    def __init__(self):
        self.redmine = Redmine(config.redmine_url, key=config.redmine_token)
        self.attach_file_idx = 1
        self.currIss = None

    # Выдает docx файл.
    # Параметры: version - версия проекта
    # Проект задан по умолчанию - "Базовый функицонал"
    def getTestProtocol(self, **kvargs):
        # зачищаем предыдущие вложения
        if not os.path.exists(RedmineWrapper.img_path):
            shutil.rmtree(RedmineWrapper.img_path)

        proj = self.redmine.project.get(RedmineConsts.base_smart_id)
        ver_arg = kvargs['version']
        if not type(ver_arg) is str:
            return None

        # version = next(v for v in proj.versions if v.name == ver_arg)
        # issues = self.redmine.issue.filter(project_id=RedmineConsts.base_smart_id, status_id=RedmineConsts.closed_state_id
        #                                    #, assigned_to_id=RedmineConsts.my_id#
        #                                    )
        # # фильтруем нужную версию
        # issues = list(i for i in issues if hasattr(i, 'fixed_version') and i.fixed_version.id == version.id)

        # тестовый тикет
        issues = [self.redmine.issue.get('48051')]

        # собираем данные. Dict(категория: list(dict с необходимыми данными))
        data = {}
        for iss in issues:
            self.currIss = iss
            # без категории не работаем
            if not getattr(iss, 'category', None):
                continue
            ctg = iss.category.name
            # категория еще не встречалась - создаем пустой список
            if not ctg in data.keys():
                data[ctg] = []
            lst = data[ctg]

            # объект тестирования
            testObj = '{}\n{}'.format(RedmineWrapper.getCustomValue(iss, RedmineConsts.whatsnew_text_id), iss.id)
            # шаги воспроизведения
            steps = self.parseTextBetween(iss.description, Parsing.user_steps_begin, Parsing.user_steps_end)
            # результат воспроизведения
            result = self.parseTextBetween(iss.description, Parsing.user_result_begin, Parsing.user_result_end)
            # инициатор задачи
            initiator = RedmineWrapper.getCustomValue(iss, RedmineConsts.initiator_id)
            lst.append([testObj, steps, result, initiator])

        # получаем только цифры от версии
        ver_num = re.search('[0-9.]+', ver_arg).group()
        # запускаем создание документы
        return docxbuilder.BuildDocx(data, ver_num)

    def getIssue(self, id):
        return self.redmine.issue.get(id)

    # парсим текст между startFrom и endWith
    def parseTextBetween(self, text, startTag, endTag):
        # парсим главный блок
        res = self.doParseTags(text, begin_tag=startTag, end_tag=endTag, parse_type=ParseType.RETURN)
        # удаляем collapse
        res = self.doParseTags(res, begin_tag=Parsing.collapse_begin, end_tag=Parsing.collapse_end)
        # находим вложения-картинки. Переименовываем их
        res = self.doParseTags(res, begin_tag='!', end_tag='!', action=lambda txt: self.parseImage(txt))
        # удаляем лишние перносы строк
        res = trimExtraEscapes(res)
        return res

    # Парсинг текста из тегов.
    # Параметры
    # begin_tag - начальный тег
    # end_tag - конечный тег
    # parse_type - тип действия ParseType
    # action - обработка совпадения, принимает параметр text - текст между тегами. По умолчанию вернет text
    def doParseTags(self, text, **kwargs):

        def processContent(match):
            return action(match.group('content'))

        res = ''
        action = kwargs.get('action')
        if not action:
            action = lambda text: text

        parse_type = kwargs.get('parse_type')
        if not parse_type and type(parse_type) is not ParseType:
            parse_type = ParseType.REPLACE

        startTag = kwargs.get('begin_tag')
        if not startTag:
            return res

        endTag = kwargs.get('end_tag')
        if not endTag:
            return res

        if parse_type == ParseType.REPLACE:
            res = re.sub(startTag + '(?P<content>[^\>]*?)' + endTag, processContent, text)
        elif parse_type == ParseType.RETURN:
            match = re.search(startTag + '(?P<content>[^\>]*?)' + endTag, text)
            res = ''
            if match:
                res = processContent(match)

        return res

    # загружаем картинку из redmine. Скачиваем, сохраняем с простым именем.
    # imgName - название вложения-картинки
    def parseImage(self, imgName):
        res = imgName
        try:
            if not self.currIss:
                return res
            attch = next(a for a in self.currIss.attachments if a.filename == imgName)
            if not attch:
                return res

            filename = format(str(self.attach_file_idx).zfill(5) + os.path.splitext(attch.filename)[1])
            self.attach_file_idx += 1
            if not os.path.exists(RedmineWrapper.img_path):
                os.makedirs(RedmineWrapper.img_path)
            attch.download(filename=filename, savepath=RedmineWrapper.img_path)
            res = '!!{}!!'.format(os.path.join(RedmineWrapper.img_path, filename))
        finally:
            return res

    @staticmethod
    def getCustomValue(issue, id):
        val = issue.custom_fields.get(id, None)
        if not val:
            return ''
        return val.value


def trimExtraEscapes(str):
    extraEsc = r'\r\n'
    match = re.search(extraEsc + '+' + '(?P<content>[^\>]*)' + extraEsc + '+', str)
    if not match:
        return str
    res = match.group('content')
    if not res:
        return ''
    res = re.sub(r'\r\n', lambda m: '\n', res)
    return res


if __name__ == '__main__':
    rdm = RedmineWrapper()
    iss = rdm.getIssue('48051')
    rdm.currIss = iss
    steps = rdm.parseTextBetween(iss.description, Parsing.user_steps_begin, Parsing.user_steps_end)
    result = rdm.parseTextBetween(iss.description, Parsing.user_result_begin, Parsing.user_result_end)
    pass
