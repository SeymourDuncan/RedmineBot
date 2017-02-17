from enum import Enum

class Messages():
    #
    bad_commad_msg = 'Неверная команда'
    #
    help_msg = 'Привет, {}! Я - Uftnc.Smart.RedmineBot.\n' \
               'Я помогу сделать твою жизнь лучше!\n' \
               'Для вызова команд используй меню.'

    prepare_file = 'Я занимаюсь подготовкой файла {}. Это займет некоторое время.'

    select_command = "Выберите одну из команд"

class RedmineConsts():
    # Состояние Закрыта
    closed_state_id = 5

    # Custom field id:
    whatsnew_text_id = 24
    initiator_id = 6
    customer_id = 8 # 68

    # Project identifiers
    base_smart_id = 'base_smart'

    # other
    my_id = 572

    versions = ['NGT-Smart Версия 4.2.0', 'NGT-Smart Версия 4.2.1', 'NGT-Smart Версия 4.2.2']
    customers = ['Для всех', 'БН', 'УНТЦ', 'РуссНефть-Саратов']

class Reports():
    # имя файла протокола тестирования
    tp_filen = 'test_protocol.docx'

    header_tmp = 'ТЕСТ-ПЛАН. ОБНОВЛЕНИЕ {}'

class Parsing():
    user_steps_begin = '{{steps_for_user_begin}}'
    user_steps_end = '{{steps_for_user_end}}'
    user_result_begin = '{{result_for_user_begin}}'
    user_result_end = '{{result_for_user_end}}'
    collapse_begin = r'{{collapse\(.*?\)'
    #(Показать..., Скрыть)
    collapse_end = r'}}?'

# тип парсинга
class ParseType(Enum):
     # заменить совпавшее значение
     REPLACE = 1
     # вернуть совпавшее значение
     RETURN = 2


