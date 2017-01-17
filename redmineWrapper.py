from redmine import Redmine
import config
import docxbuilder
from consts import RedmineConsts

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

        version = next(v for v in proj.versions if v.name == ver_arg)

        issues = self.redmine.issue.filter(project_id=RedmineConsts.base_smart_id, status_id=RedmineConsts.closed_state_id,
                                      assigned_to_id=RedmineConsts.my_id)

        # фильтруем нужную версию
        issues = list(i for i in issues if hasattr(i, 'fixed_version') and i.fixed_version.id == version.id)

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
            # lst.append({'object': getCustomValue(iss, whatsnew_text_id), 'scenario': iss.description, 'result': '', 'initiator': getCustomValue(iss, initiator_id)})
            lst.append([RedmineWrapper.getCustomValue(iss, RedmineConsts.whatsnew_text_id), iss.description, '',
                        RedmineWrapper.getCustomValue(iss, RedmineConsts.initiator_id)])

        return docxbuilder.BuildDocx(data)

    @staticmethod
    def getCustomValue(issue, id):
        val = issue.custom_fields.get(id, None)
        if not val:
            return ''
        return val.value
