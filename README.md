## spicy.document

Приложение Django для проекта SpicyCMS. Использует [концепцию реиспользования кода и конфигурации spicy.core](https://github.com/spicycms/spicy.core).

## Назначение

Модуль spicy.document предоставляет базовый класс Документа с возможностью создавать приватные документы, скрывать от не зарегистрированных пользователей, комментировать. 

Вы можете переопределить модель документа для нужд вашего приложения, добавить возможность помечать Документ [тегами](https://github.com/spicycms/spicy.labels) и присваивать [категории](https://github.com/spicycms/spicy.document). Также при подключении [spicy.history](https://github.com/spicycms/spicy.history) можно настроить сохранение истории изменений и откатывать их.

### Подключение модуля к приложению

Добавить приложение в settings.py:

    INSTALLED_APPS = (
    #...
    'spicy.document',
    #...
    )
    
### Делаем свою модель Документа

Модуль предоставляет абстрактную модель для работы с Документом. По умолчанию предоставляется базовый класс ``spicy.document.models.DefaultDocument`` который может быть переопределен. Для того, чтобы использовать свой класс документа, укажите в settings.py:

    USE_DEFAULT_DOCUMENT_MODEL = False
    CUSTOM_DOCUMENT_MODEL = 'yourapp.models.CustomDocument'

Объявите новую модель в вашем приложении, унаследовав ее от ``spicy.document.abs.AbstractDocument``, и укажите ``Meta.abstract = False``, чтобы Django создала таблицу в базе данных:

    # yourapp.models.py
    from spicy.document.abs import AbstractDocument

    class CustomDocument(AbstractDocument):
        # your additional fields
        # here you could add FK to category
        
        class Meta:
            abstract = False
    
По умолчанию для создания и редактирования документа в админке используются формы ``spicy.document.forms.CreateDocumentForm`` и ``spicy.document.forms.DocumentForm``. Вам необходимо создать свои формы, чтобы новые поля ``CustomDocument`` можно было редактировать в интерфейсе администратора, для этого укажите в settings.py:

    CREATE_DOCUMENT_FORM = 'yourapp.forms.CreateCustomDocumentForm'
    EDIT_DOCUMENT_FORM = 'yourpps.forms.CustomDocumentForm'
    
И объявите формы в проекте, унаследовав от ``CreateDocumentForm`` и ``DocumentForm``:

    # yourapp.forms.py
    from spicy.utils.models import get_custom_model_class
    from spicy.document.forms import CreateDocumentForm, DocumentForm
    from spicy.document import defaults as dc_defaults
    CustomDocumentModel = get_custom_model_class(dc_defaults.CUSTOM_DOCUMENT_MODEL)

    class CreateCustomDocumentForm(CreateDocumentForm):
        # your additional fields
        class Meta(CreateDocumentForm.Meta):
            model = CustomDocumentModel
            
    class CustomDocumentForm(DocumentForm):
        # your additional fields
        class Meta(DocumentForm.Meta):
            model = CustomDocumentModel
    
{TODO}     фрагмент для добавления новых полей в админку ({% formfield %})
    
### Настройка истории изменений

Для использования истории изменений подключить сервисы ``[TrashService]``(https://github.com/spicycms/spicy.core) и ``[HistoryService]``(https://github.com/spicycms/spicy.history) в settings.py и добавить модули в INSTALLED_APPS:

    SERVICES = (
        'spicy.core.trash.services.TrashService',
        'spicy.history.services.HistoryService',
    )
    
    INSTALLED_APPS = (
      #...
      'spicy.core.trash',
      'spicy.history',
      #...
    )
    


    
    
    
  
  


