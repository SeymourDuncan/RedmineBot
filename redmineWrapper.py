from redmine import Redmine
import config
import docxbuilder
from consts import RedmineConsts, Parsing

import re

class RedmineWrapper():
    def __init__(self):
        self.redmine = Redmine(config.redmine_url, key=config.redmine_token)

    # Выдает docx файл.
    # Параметры: version - версия проекта
    # Проект задан по умолчанию - "Базовый функицонал"
    def getTestProtocol(self, **kvargs):
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
            # без категории не работаем
            if not getattr(iss, 'category', None):
                continue
            ctg = iss.category.name
            # категория еще не встречалась - создаем пустой список
            if not ctg in data.keys():
                data[ctg] = []
            lst = data[ctg]

            testObj = '{}\r\n{}'.format(RedmineWrapper.getCustomValue(iss, RedmineConsts.whatsnew_text_id), iss.id)
            steps = parseTextBetween(iss.description, startFrom=Parsing.user_steps_begin, endWith=Parsing.user_steps_end)
            result = parseTextBetween(iss.description, startFrom=Parsing.user_result_begin, endWith=Parsing.user_result_end)
            initiator = RedmineWrapper.getCustomValue(iss, RedmineConsts.initiator_id)
            lst.append([testObj, steps, result, initiator])

        # только цифры от версии
        ver_num = re.search('[0-9.]+', ver_arg).group()
        return docxbuilder.BuildDocx(data, ver_num)

    def getIssue(self, id):
        return self.redmine.issue.get(id)

    @staticmethod
    def getCustomValue(issue, id):
        val = issue.custom_fields.get(id, None)
        if not val:
            return ''
        return val.value

# парсинги
def parseTextBetween(text, **kwargs):
    res = ''
    startFrom = kwargs['startFrom']
    if not startFrom:
        return res

    endWith = kwargs['endWith']
    if not endWith:
        return res

    match = re.search(startFrom + '(?P<content>[^\>]*)' + endWith, text)
    if not match:
        return res
    res = match.group('content')
    if not res:
        return ''
    # удаляем лишние перносы строк
    res = trimExtraEscapes(res)

    # удаляем collapse
    res = deleteTags(res, startTag=Parsing.collapse_begin, endTag=Parsing.collapse_end)
    return res

# возвращает тест без тегов
def deleteTags(text, **kwargs):
    # вернуть то что между тегами
    def getContent(matchobj):
        res = matchobj.group('content')
        return res

    res = ''
    startTag = kwargs['startTag']
    if not startTag:
        return res

    endTag = kwargs['endTag']
    if not endTag:
        return res

    res = re.sub(startTag + '(?P<content>[^\>]*?)' + endTag, getContent, text)
    return res

def trimExtraEscapes(str):
    extraEsc = r'\r\n'
    match = re.search(extraEsc+ '*' + '(?P<content>[^\>]*)' + extraEsc+'*', str)
    if not match:
        return ''
    res = match.group('content')
    if not res:
        return ''
    return res;

if __name__ == '__main__':
    rdm = RedmineWrapper()
    iss = rdm.getIssue('48051')
    steps = parseTextBetween(iss.description, startFrom=Parsing.user_steps_begin, endWith=Parsing.user_steps_end)
    result = parseTextBetween(iss.description, startFrom=Parsing.user_result_begin, endWith=Parsing.user_result_end)
    pass




