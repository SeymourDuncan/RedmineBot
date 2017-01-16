from redmine import Redmine
import config
import docxbuilder

def getCustomValue(issue, id):
    val = issue.custom_fields.get(id, None)
    if not val:
        return ''
    return val.value

# def getScenario(issue):


# Состояние Закрыта
closed_state_id = 5
whatsnew_text_id = 24
initiator_id = 6

version_name = 'NGT-Smart Версия 4.1.9'

base_smart_id = 'base_smart'
# ngt_smart_id = 'ngt-smart'
my_id = 572

redmine = Redmine(config.redmine_url, key=config.redmine_token)

print(list(redmine.issue_status.all().values()))

proj = redmine.project.get(base_smart_id)
version = next(v for v in proj.versions if v.name == version_name)

issues = redmine.issue.filter(project_id = base_smart_id, status_id = closed_state_id, assigned_to_id = my_id)

# фильтруем нужную версию
# issues = list(i for i in issues if checkFixVer(i, version))
issues = list(i for i in issues if hasattr(i, 'fixed_version') and i.fixed_version.id == version.id)

print(len(issues))

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
    lst.append([getCustomValue(iss, whatsnew_text_id), iss.description, '', getCustomValue(iss, initiator_id)])

print(data)

docxbuilder.BuildDocx(data)

