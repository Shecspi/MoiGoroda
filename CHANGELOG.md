# Changelog

В этом файле задокументированы все значимые изменения проекта "Мои города".

## [ Подготовка нового релиза ]

#### 🚀 Новые функции

- *(map)* На картах городов региона и городов коллекции добавлена возможность добавлять города ([e3f8d40](https://github.com/Shecspi/MoiGoroda/commit/e3f8d40fd1495d794edf31755907c1f8f375c6cb))

- *(collection)* Появилась возможность создавать персональные коллекции ([2209b8d](https://github.com/Shecspi/MoiGoroda/commit/2209b8d869aa8abe82ec8febe5863fd3713ad8ef))

- *(city)* Сохранение настроек фильтрации и сортировки в списке посещённых городов ([379d21f](https://github.com/Shecspi/MoiGoroda/commit/379d21f482b495618745c7175ef70d4807a5d949))

- *(region)* Добавлен фильтр по годам посещения на карте регионов ([ff6b0a7](https://github.com/Shecspi/MoiGoroda/commit/ff6b0a7ef0a63d172bba276718c78ed3ed60b7a7))

- *(city)* Добавлен фильтр по годам на карте городов ([444ee20](https://github.com/Shecspi/MoiGoroda/commit/444ee205be0a128b241f92d81a21c957b7f0fdd5))

- *(city_districts)* Добавлена новая карта, на которой можно собирать районы городов ([99b5abe](https://github.com/Shecspi/MoiGoroda/commit/99b5abeed1ab85fa9f6c00da14ef77b5bb41eba2))

- *(districts)* Реализована возможность пользовательской настройки цветов карты районов ([bb623b2](https://github.com/Shecspi/MoiGoroda/commit/bb623b2529be4e635f71193a6cd008cb07848245))

- *(place-collection)* Добавлена возможность отмечать места как посещённые/не посещённые и объединять их в коллекции ([5d7966a](https://github.com/Shecspi/MoiGoroda/commit/5d7966a046481eee0e339c91875e4f854265603a))

- *(news)* Создание новостей перенесено с MDeditor на CKeditor, благодаря чему новости в базе данных стали храниться в HTML формате, вместо Markdown ([10de20b](https://github.com/Shecspi/MoiGoroda/commit/10de20b064e035de17e32a379801d9ba717e4133))

- *(blog)* Добавлен модуль, позволяющий писать статьи о городах ([a921c51](https://github.com/Shecspi/MoiGoroda/commit/a921c51bb5abc176f47a859b2e94a33efb50bc22))

- Добавлено кеширование файлов S3 на 1 год ([8b858f8](https://github.com/Shecspi/MoiGoroda/commit/8b858f8276e6f44d4256a37ebb23d2047996ba72))

- *(collection)* Добавлен поиск города по названию на странице создания коллекции ([d394041](https://github.com/Shecspi/MoiGoroda/commit/d39404149b20f1fd5fbb483bae3997ef284966aa))

- *(premium)* Добавлена возможность оплачивать премиум-подписку ([a891bfd](https://github.com/Shecspi/MoiGoroda/commit/a891bfd5dddf3a63060c12dc71aba7cac65b0168))

- *(premium)* Баннер премиум-подписки ([ec8a820](https://github.com/Shecspi/MoiGoroda/commit/ec8a8205d09f58c1323c2b9a2d1418bbc63e3a06))

- *(region)* Добавлена возможность скачивать и делиться изображениями с посещёнными городами ([ff77b95](https://github.com/Shecspi/MoiGoroda/commit/ff77b9549a5307cce494455a14423236f2713df1))

- *(django)* Обновлена версия Django до 5.2 ([336916b](https://github.com/Shecspi/MoiGoroda/commit/336916bfc3069d60a611a4f63b431efe9470bdd1))

- *(dashboard)* Перевод дашборда с DRF на django-modern-rest ([b81a45c](https://github.com/Shecspi/MoiGoroda/commit/b81a45c69f631644067813db73ff5a79ce4f1510))

- *(city)* Исправление ошибки, из-за которой невозможно было добавить город с карты ([71da18f](https://github.com/Shecspi/MoiGoroda/commit/71da18fc07b9b66e42632c4a94afdc120cf5b6b1))

- *(city)* Загрузка пользовательских фотографий городов при расширенной премиум-подписке ([97fa676](https://github.com/Shecspi/MoiGoroda/commit/97fa676c65d95887317ed01040db033c642659bc))


#### 🐛 Исправление ошибок

- Исправлено редактирование сохранённого места ([377687e](https://github.com/Shecspi/MoiGoroda/commit/377687edd57939c9062c40abbc64bc449b9ec547))

- *(sidebar)* Удалён вывод отладочной информации в консоль при работет сайдбара ([8ed0145](https://github.com/Shecspi/MoiGoroda/commit/8ed01451b2ddb49a3f94c6cd6b31ae5177e9516f))

- Исправлена ошибка в Github Actions workflow, из-за которой доставка на сервер не осуществлялась ([3a6398b](https://github.com/Shecspi/MoiGoroda/commit/3a6398b83148f34c902b5e794fe3536581a90d82))

- *(place-collection)* Исправлена ошибка, из-за которой при перетаскивании маркера места по карте не подгружались новые координаты и не заполнялся popup. ([7003e09](https://github.com/Shecspi/MoiGoroda/commit/7003e09a024b4afe0280ea6f260efe7ec98bef68))

- *(place-collection)* Исправлено вылезание выпадающего списка за пределы экрана на маленьких устройствах ([9368c02](https://github.com/Shecspi/MoiGoroda/commit/9368c024ddf5742c32d05249d9dd735724436d3c))

- Исправлено редактирование сохранённого места ([2d9aef2](https://github.com/Shecspi/MoiGoroda/commit/2d9aef26c18c37cce1841097d8e624f5dc9aa825))

- *(sidebar)* Удалён вывод отладочной информации в консоль при работет сайдбара ([99dd1a0](https://github.com/Shecspi/MoiGoroda/commit/99dd1a07e02acd77f017e3ecca3698223dd243f7))

- Исправлена ошибка в Github Actions workflow, из-за которой доставка на сервер не осуществлялась ([6c16b16](https://github.com/Shecspi/MoiGoroda/commit/6c16b16bd130f2a6e665df7298676aa6f59fd5f1))

- *(admin)* Мелкие изменения в админке - добавлены отображаемые модели, добавлены некоторые поля в список отображения ([88ced74](https://github.com/Shecspi/MoiGoroda/commit/88ced740124c1356171dfee81c81cff61e732840))

- *(collections)* Исправлена статистика посещённых городов в персональных коллекциях ([0de109e](https://github.com/Shecspi/MoiGoroda/commit/0de109e04f317c4c676ad2ff1e1b51093ac5a8a7))

- *(collections)* Исправлено отображение цветов бейджей городов в персональных коллекциях ([bf367bc](https://github.com/Shecspi/MoiGoroda/commit/bf367bce2561b8a47e180d79ae667192161c291a))

- *(districts)* Добавлена возможность просмотра карты районов города неавторизованными пользователями ([c991fa3](https://github.com/Shecspi/MoiGoroda/commit/c991fa3b9dd78b3c21ea42c9bb62fe51601ff8f5))

- *(place-collection)* Исправлена ошибка, из-за которой при перетаскивании маркера места по карте не подгружались новые координаты и не заполнялся popup. ([a82f1a7](https://github.com/Shecspi/MoiGoroda/commit/a82f1a7b628c45cdb5579203b71c5558d9c27c82))

- *(place-collection)* Исправлено вылезание выпадающего списка за пределы экрана на маленьких устройствах ([1026521](https://github.com/Shecspi/MoiGoroda/commit/1026521eb1a70230e920032f3b0f0533fc660c8b))

- *(notification)* Активирован сигнал уведомления подписчиков при добавлении города ([8f30c08](https://github.com/Shecspi/MoiGoroda/commit/8f30c08e3843a0a753e65a48aca3f5142ef8cb77))

- *(city)* Улучшена вёрстка модальных окон карты и статистики города ([b9c8f3d](https://github.com/Shecspi/MoiGoroda/commit/b9c8f3dbae4bbd823f3c067b75d122832560b596))

- Удалена неиспользуемая страница signup_success ([be81e50](https://github.com/Shecspi/MoiGoroda/commit/be81e50797419cfb7ad9e1f64e8ed76d233e2953))

- *(city)* Исправлена XSS в city_search.js ([16c0363](https://github.com/Shecspi/MoiGoroda/commit/16c0363baa4bfb19461a958b2b9ccfaa121630b5))

- *(region)* Отсортирован выпадающий список стран в админке по алфавиту ([09b41c6](https://github.com/Shecspi/MoiGoroda/commit/09b41c6f824efbdadde88155cbe7fc6eb9900bf0))

- *(city)* Отсортирован выпадающий список стран на странице добавления города ([c91635e](https://github.com/Shecspi/MoiGoroda/commit/c91635e526633e6e61eec01688a497571bc59706))

- Кнопка вызова окна уведомлений на мобильных устройствах привязана к модальному окну ([91d7eae](https://github.com/Shecspi/MoiGoroda/commit/91d7eae608842a73809446268678d7effc7a303e))

- *(city)* Исправлена svg иконка на карточке города ([403a3c9](https://github.com/Shecspi/MoiGoroda/commit/403a3c939e676f9903dca661b19bf92c198e8e64))

- *(city)* Обновлена форма добавления города — Preline-селекты, z-index выпадающих списков и правки UX ([17a3354](https://github.com/Shecspi/MoiGoroda/commit/17a3354aa563c75dbbe480432c63f31e97424a38))

- *(city)* Заменён виджет поля «Дата посещения» на кастомный ([938ec71](https://github.com/Shecspi/MoiGoroda/commit/938ec71773a6a528ff2ee9bc5374c231f3563bde))

- *(notification)* Отключен периодический опрос уведомлений ([5be1fe1](https://github.com/Shecspi/MoiGoroda/commit/5be1fe122b15848ede10395e5e2008689689b92f))

- Корректная половина звезды средней оценки и общий компонент рейтинга ([ebcf0aa](https://github.com/Shecspi/MoiGoroda/commit/ebcf0aa8296f82bbde55092c1c16004ef581b58e))

- *(city)* Скрыт блок региона на странице города без региона ([e207672](https://github.com/Shecspi/MoiGoroda/commit/e2076727c163701fba54ea5f68cf21dee8008f30))


#### 🧪 Тестирование

- *(region)* Добавлены тесты генератора изображений карты городов региона ([13fd6ab](https://github.com/Shecspi/MoiGoroda/commit/13fd6abdac08c30626a74e4cd422e003428d85f6))


#### Fear

- *(city)* Календарь даты посещения: переключение года и месяца кнопками ([a37cf72](https://github.com/Shecspi/MoiGoroda/commit/a37cf7204f7975bd730eab9e9723929d7e003933))


#### Изменено

- Цветовые настройки карты районов — панель на карте (кнопка-шестерёнка), сброс цветов, выравнивание и размер текста ([f4967e1](https://github.com/Shecspi/MoiGoroda/commit/f4967e1625bb637335554bb04b070eae46958426))

- Кнопка «Сбросить» в настройках цветов карты районов — стили Preline, уменьшенные отступы, явный hover/focus ([52d0505](https://github.com/Shecspi/MoiGoroda/commit/52d0505e0a7c0d1a738dd5ba39480ee1b064548b))

- Цветовые настройки карты районов — панель на карте (кнопка-шестерёнка), сброс цветов, выравнивание и размер текста ([ba21e12](https://github.com/Shecspi/MoiGoroda/commit/ba21e12f788077a0d8de5278b4e77bdc65f0cbcd))

- Кнопка «Сбросить» в настройках цветов карты районов — стили Preline, уменьшенные отступы, явный hover/focus ([16986b1](https://github.com/Shecspi/MoiGoroda/commit/16986b13fda468aeb5981c3f66aaec196dd3da86))


#### Коллекции

- Редактирование названия, блок контекста, переключатель красный/зелёный ([11f7d07](https://github.com/Shecspi/MoiGoroda/commit/11f7d077696000ccfa1fc8ccce2f50d456aafcb0))

- Редактирование названия, блок контекста, переключатель красный/зелёный ([880db07](https://github.com/Shecspi/MoiGoroda/commit/880db07ebdc594341e3151b7c4dc8e65805351ef))


#### Сделано

- Цветовые пикеры для заливки полигонов посещённых и непосещённых районов с throttle перерисовки ([67868d5](https://github.com/Shecspi/MoiGoroda/commit/67868d58ca234d3bac190f9b9d8d73baf42e9bb2))

- Сохранение цветов карты районов в БД (модель DistrictMapColorSettings, API, загрузка/сохранение на фронте) ([b93baf3](https://github.com/Shecspi/MoiGoroda/commit/b93baf3886f87d5f76eabfe0e44ba9c916fb47e9))

- Цветовые пикеры для заливки полигонов посещённых и непосещённых районов с throttle перерисовки ([dafaacf](https://github.com/Shecspi/MoiGoroda/commit/dafaacfb594f89ed6c076963b7fd5277127d42f2))

- Сохранение цветов карты районов в БД (модель DistrictMapColorSettings, API, загрузка/сохранение на фронте) ([4e301a3](https://github.com/Shecspi/MoiGoroda/commit/4e301a30e203a552121ce1382d6764a36add0cea))


## [ 3.0 ] - 2025-11-27

#### 🚀 Новые функции

- *(region)* Добавлена возможность поиска регионов в списке регионов ([8d7472d](https://github.com/Shecspi/MoiGoroda/commit/8d7472dd4b23ca1737ed01665063b0ade47a61af))

- *(collection)* Добавлен поиск по коллекциям ([26d842d](https://github.com/Shecspi/MoiGoroda/commit/26d842d1ea81847f1d6370c44f395f83b8e2e8f1))

- *(city)* Добавлен поиск по городам ([eb1d030](https://github.com/Shecspi/MoiGoroda/commit/eb1d030e50666461c06d5d06ea19f71701a4f381))

- *(collection)* Добавлена возможность отмечать коллекции как избранные ([1958ea9](https://github.com/Shecspi/MoiGoroda/commit/1958ea9d369c198832d239cf1c700c304a1433e2))

- *(design)* Унификация дизайна страниц коллекций и создание модульной CSS архитектуры ([b29b4da](https://github.com/Shecspi/MoiGoroda/commit/b29b4daea87cecfb70bab328954d242c0f9b209d))


#### 🐛 Исправление ошибок

- *(bug32)* Исправлена ссылка на профиль пользователя в списке уведомлений ([adfcc09](https://github.com/Shecspi/MoiGoroda/commit/adfcc0921885e974fc3f2ec165fd98d9c55d01f3))

- *(region)* На странице карты городов выбранного региона в заголовке теперь отображается название страны рядом с названием региона) ([41c494f](https://github.com/Shecspi/MoiGoroda/commit/41c494f737d34daa75101c969c7c5acf92a45a71))

- *(place)* Список категорий теперь возращается в алфавитном порядке ([45fe481](https://github.com/Shecspi/MoiGoroda/commit/45fe481f3b58e3d444ac94dfe1a40505f6899bca))

- Добавлена проверка владельца записи в VisitedCity_Update ([8cae5eb](https://github.com/Shecspi/MoiGoroda/commit/8cae5eb8f62463a9ba3ab4bf0bd6bbd142ef8ada))

- Добавлена проверка владельца записи в VisitedCity_Update ([12b8aaa](https://github.com/Shecspi/MoiGoroda/commit/12b8aaa84c2b953e51803c014f651ee2e9c01eae))

- Добавлена проверка владельца записи в VisitedCity_Update ([5f6bb2a](https://github.com/Shecspi/MoiGoroda/commit/5f6bb2aae4eba04dab4bcfe46c75c59474117271))

- *(collection)* Исправлен z-index элементов поиска для корректного отображения сайдбара ([179b69b](https://github.com/Shecspi/MoiGoroda/commit/179b69b93cdb31034aea85cb3a575c2254388c8b))

- *(collection)* Исправлена анимация page-header-divider (убрано ужимание после расширения) ([b791ffd](https://github.com/Shecspi/MoiGoroda/commit/b791ffd8d3467211f965c08e213dbcd2ae767c3c))


#### 🚜 Рефакторинг

- Рефакторинг тестов и улучшения инфраструктуры проекта ([88a3c03](https://github.com/Shecspi/MoiGoroda/commit/88a3c038bc27b682a6eb3d9b73ff19a15cba26bd))


#### 🎨 Дизайн

- *(news)* Улучшен дизайн изображений на карточке новости для отделения изображения от фона и умещения его в размеры карточки ([2d1ba39](https://github.com/Shecspi/MoiGoroda/commit/2d1ba390360969a66ca162d736f55f67d7b35d87))


#### CI

- Разрешить запуск тестов для ветки fix-ci-tests без деплоя ([b2b5c17](https://github.com/Shecspi/MoiGoroda/commit/b2b5c170d6cbc7bc56d5d98e4a2cde9788cdebe3))

- Разделены проверки и деплой ([20be3a2](https://github.com/Shecspi/MoiGoroda/commit/20be3a2c2e9a980c24968cee226905451745d057))

- Collectstatic теперь bash-скрипт ([2dcf31f](https://github.com/Shecspi/MoiGoroda/commit/2dcf31f4041b6e4919ad28d7cea74a499d2ce8c8))

- Перезапуск gunicorn через bash ([0df447a](https://github.com/Shecspi/MoiGoroda/commit/0df447a3c7feca1eca70fb1ea71800b860e35a27))

- Встроены команды деплоя прямо в workflow ([07e1584](https://github.com/Shecspi/MoiGoroda/commit/07e158423362a070465dac525b01a7cbd09839f5))


#### Cleanup

- Удалены отладочные элементы, упрощены комментарии ([033d526](https://github.com/Shecspi/MoiGoroda/commit/033d5264a3ab2248b2e63348250e757dee7aeb6c))


#### Debug

- Добавлен диагностический скрипт + запуск только одного теста ([cfd27d4](https://github.com/Shecspi/MoiGoroda/commit/cfd27d4db1ec63b82d90a6f1fd80fa91a1ba7295))

- Добавлена диагностика в vite_asset для отладки DEBUG ([0e3a35a](https://github.com/Shecspi/MoiGoroda/commit/0e3a35af4c24f0b1dd55683a2a6d57034576f54d))

- Добавлена диагностика загрузки settings.py ([c73db2b](https://github.com/Shecspi/MoiGoroda/commit/c73db2bf73ecdd2881d107867be7f0f0715f8a49))


#### Fix

- Исправлена работа vite_asset в тестах (Django принудительно устанавливает DEBUG=False) ([be7cfa8](https://github.com/Shecspi/MoiGoroda/commit/be7cfa868a47ca1aa0f5dc55798a009f781ed6cb))


#### Исправлено

- Сайдбар теперь скрыт по умолчанию на мобильных устройствах при загрузке страницы ([1b31985](https://github.com/Shecspi/MoiGoroda/commit/1b31985dae69d7eabdfcf9f66f28df5c175d090c))


## [ 2.5 ] - 2025-09-05

#### 🚀 Новые функции

- *(country)* Добавлена возможность отмечать на карте посещённые страны ([3a7422b](https://github.com/Shecspi/MoiGoroda/commit/3a7422b50c332f5fd920fd2cd5c148bca2395735))

- *(region)* На карте городов региона отображаются границы этого региона ([d39be94](https://github.com/Shecspi/MoiGoroda/commit/d39be947ee2a3026f957586c822014b627fbe3e0))

- *(region)* На карте регионов для каждого региона добавлено всплывающее окно с ссылками на список и карту городов выбранного региона ([fa5691d](https://github.com/Shecspi/MoiGoroda/commit/fa5691d559099ee8cd7c7fbcdf41282bf82d8917))

- *(region)* Карта регионов переведена на использование OpenStreetMap ([fc74adf](https://github.com/Shecspi/MoiGoroda/commit/fc74adf9256163f00b69b719d245531bb6372196))

- *(region)* Карта городов региона переведена на использование OpenStreetMap ([a063727](https://github.com/Shecspi/MoiGoroda/commit/a063727e770b4dd6725bf41b057dd8f939efee57))

- *(region)* Карта городов региона теперь отображается с высокой детализацией границ ([01b4c02](https://github.com/Shecspi/MoiGoroda/commit/01b4c02ad1fd07132a2a2a968717d5da5b1c1071))

- *(city)* Добавлена возможность использования Markdown-разметки в поле "Впечатления о городе" ([51d24f0](https://github.com/Shecspi/MoiGoroda/commit/51d24f09a9a9faf511bd6cb6f5e356c2e4f18fbc))

- *(country)* Карта стран мира переведена на использование OpenStreetMap ([c9a6e8f](https://github.com/Shecspi/MoiGoroda/commit/c9a6e8f724d7ef06563d28cb9e893a535a08d3c6))

- *(screenshot)* Добавлена возможность сделать скриншот карты посещенных страны, регионов и городов региона. ([f458918](https://github.com/Shecspi/MoiGoroda/commit/f45891800b6bbdeb1bf66bcc4b5daa8783392d19))

- *(city)* Карта городов страны переведена на использование карт OpenStreetMap с возможностью создания скриншотов карты ([7556548](https://github.com/Shecspi/MoiGoroda/commit/7556548689ed8719a0936524f5eb0f7d3a8cfd7e))

- *(map)* На карту всех посещённых городов добавлена возможность добавить границы страны и регионов страны ([f4b1387](https://github.com/Shecspi/MoiGoroda/commit/f4b1387fa3133a2bb2df37394f0adf6bfdedf3aa))

- *(place)* Появилась возможность отмечать на карте произвольные места, а не только города ([d31706b](https://github.com/Shecspi/MoiGoroda/commit/d31706be735683c2908b8c3fcfa6cc5401414b99))

- *(city)* При добавлении посещённого города можно автоматически заполнить поле "Дата посещения" на сегодняшнее или вчерашнее число ([5682a52](https://github.com/Shecspi/MoiGoroda/commit/5682a520bc8cb5f8706cb8dadd1281e6f57b0562))

- *(city)* Добавлена возможность отмечать как посещённый один город несколько раз ([212ee98](https://github.com/Shecspi/MoiGoroda/commit/212ee988ea3f2a05aaca246f54b2779e077316b9))

- *(city)* На страницу информации о городе добавлена возможность посмотреть его местоположение на карте ([80b9ce7](https://github.com/Shecspi/MoiGoroda/commit/80b9ce7f4155c0ca96617affa811e52194adf6ba))

- *(city)* Добавлено отображение статистики города среди всех пользователей сервиса ([4368655](https://github.com/Shecspi/MoiGoroda/commit/43686552916a209932d1a32ba0ce63edb02249b3))

- *(city)* Добавлена возможность отмечать города любой страны мира ([981f205](https://github.com/Shecspi/MoiGoroda/commit/981f205ee27f4ca98836a75ef9a3f89686ec5e56))

- *(subscriptions)* На страницу профиля добавлены списки подписок и подписчиков с возможностью их удаления ([0035e25](https://github.com/Shecspi/MoiGoroda/commit/0035e257ff33ba1b5d3d51cfcc6942c59a3a548b))

- *(subscriptions)* При добавлении посещённого города всем подписчикам приходит уведомление об этом ([65e1bd0](https://github.com/Shecspi/MoiGoroda/commit/65e1bd09164db99eeb0ce4ac67c67426513c7a5d))


#### 🐛 Исправление ошибок

- *(sidebar)* Исправлен баг с циклической прокруткой содержимого при скролле на сайдбаре ([ec8512a](https://github.com/Shecspi/MoiGoroda/commit/ec8512a5d279840a62d42c8dd1b9db7dc372677e))

- *(share)* Исправлено отображение посещенных городов на странице просмотра статистики другого пользователя ([5faf279](https://github.com/Shecspi/MoiGoroda/commit/5faf279afbd549a598d024ed6c85fb31268f736c))

- *(couontry)* Добавлен заголовок для страницы карты стран мира ([5fdb443](https://github.com/Shecspi/MoiGoroda/commit/5fdb443098bbb207e2e8bc84555c0c1681be1656))

- *(dashboard)* Исправлена ошибка сортировки добавленных стран в дашборде ([6690a8e](https://github.com/Shecspi/MoiGoroda/commit/6690a8e7c180def197add7c959f10ec9bede197c))

- *(stats)* Исправление ошибки, из-за которой не обрабатывался последний месяц года и статистика не загружалась ([c3b938d](https://github.com/Shecspi/MoiGoroda/commit/c3b938d472ba57ff9852afec7c444f56477627ba))

- *(stats)* На странице статистики пользователя изменены сообщения об отсутствии посещённых городов на корректные как для личной статистики, так и для статистики другого пользователя ([ff41aa9](https://github.com/Shecspi/MoiGoroda/commit/ff41aa9ee79f6e6cf80d354fcddf859292fc6f97))

- *(collection)* Исправлена ошибка, из-за которой неавторизованные пользователи могли получать страницу 500, когда пытались воспользоваться сортировкой ([e5ca63a](https://github.com/Shecspi/MoiGoroda/commit/e5ca63aa8156b59aa2fb3dfd32c49927e58af6d1))

- *(city)* Исправлено появление "None" на странице города, если год основания не указан ([7885f72](https://github.com/Shecspi/MoiGoroda/commit/7885f72c404d59b0118718a6ac23cb93bb79b155))

- *(bug30)* В модальное окно "Статистика города" добавлен вертикальный скролл ([2326eca](https://github.com/Shecspi/MoiGoroda/commit/2326ecaff1fac57e38f78ff7927148db1fb15cda))

- *(bug31)* Исправлено некорректное отображение надписи "Нет деления на регионы" на карте регионов, если не посещено ни одного региона ([61abb39](https://github.com/Shecspi/MoiGoroda/commit/61abb39d2c39ba3c1434ef6ac1ba1a7c3d3154ab))

- *(news)* Изменены кавычки в заголовке страницы новостей на типографические ([ff7c27c](https://github.com/Shecspi/MoiGoroda/commit/ff7c27cddca4654ebae952bd6bd0935403ed8f88))


#### 🚜 Рефакторинг

- *(sentry)* В проекте больше не используется Sentry ([b052c21](https://github.com/Shecspi/MoiGoroda/commit/b052c2132651658fd5bad0a905548782c8a304fc))


#### 🎨 Дизайн

- *(sidebar)* Сайдбар зафиксирован на всю ширину на больших экранах и отсоединён от прокрутки основной части страницы ([a4c906e](https://github.com/Shecspi/MoiGoroda/commit/a4c906e5d36a4a9706163d4f8ad292b2b69cfb53))


## [ 2.4 ] - 2024-08-13

#### 🚀 Новые функции

- *(pre-commit)* Добавлены проверки форматирования на этапе pre-commit ([87e10e4](https://github.com/Shecspi/MoiGoroda/commit/87e10e452b30f6f40ad7a61f3b2dfe767a99ed81))

- *(subscription)* Подписка на пользователей и возможность смотреть их города на одной карте вместе со своими ([2d52e15](https://github.com/Shecspi/MoiGoroda/commit/2d52e15e56f22aa846555b40773a5b361825a930))

- *(new_regions)* Добавлены города 4 новых регионов России ([fcc0be3](https://github.com/Shecspi/MoiGoroda/commit/fcc0be38f7b73d4561c6289ffa4b4c298abd276c))

- *(visited_city)* Добавление посещённых городов с общей карты ([e35762d](https://github.com/Shecspi/MoiGoroda/commit/e35762d26fb07d1067dd7aec88408d2341d6fb98))


#### 🐛 Исправление ошибок

- *(dashboard)* Исправлен неверный подсчёт количества регистраций пользователей ([ad377c1](https://github.com/Shecspi/MoiGoroda/commit/ad377c1275405a68548e99cd6dd53f5710647946))

- *(initial_db)* Актуализирован файл для начальной инициализации БД ([1559839](https://github.com/Shecspi/MoiGoroda/commit/15598393a6f9ce8ea9151229eaed650dce637fa0))

- *(openpyxl)* Обновлена версия openpyxl в зависимостях до 3.1.3 ([d65783a](https://github.com/Shecspi/MoiGoroda/commit/d65783ac8e28457ef27132a6667365580b5947f0))

- Исправление некорректного склонения слов в тулбаре на странице карты городов ([ed7b7be](https://github.com/Shecspi/MoiGoroda/commit/ed7b7be635e654080c77def9e1b03466ac0a764a))


#### ⚡ Производительность

- Автоматическая генерация файла изменений CHANGELOG.md ([d2bccce](https://github.com/Shecspi/MoiGoroda/commit/d2bccce2b79803e858cbb3add62e5cfeae92f296))


#### 🎨 Дизайн

- Улучшена адаптивная вёрстка страниц сайта для разных размеров экранов ([1f63639](https://github.com/Shecspi/MoiGoroda/commit/1f636395458ca806821eb5abde59433d3ec52f74))

- *(magnet)* Термин "магнит" заменён на "сувенир из города" ([3fd4dc9](https://github.com/Shecspi/MoiGoroda/commit/3fd4dc916bfe15e018240e45fe2170c0d7915915))


#### Db

- Обновлён initial_db.json с новым городом Бугры ([5bf19c8](https://github.com/Shecspi/MoiGoroda/commit/5bf19c8058818f07d779be65c743531491dc5df5))


#### Рефакторинг

- Разбивка на файлы + удаление неиспользуемого кода ([b26037f](https://github.com/Shecspi/MoiGoroda/commit/b26037ff6f406130bc3025408b8e82569a607c59))


## [ 2.3 ] - 31.03.2024

#### 🚀 Новые функции
- *(stats)* Добавлена возможность предоставить доступ к своей статистике посторонним
#### 🚜 Рефакторинг
- *(logger)* Отказ от использования миксина LoggingMixin в пользу services/logger.py
#### 🧪 Тестирование
- Увеличено покрытие кода логированием

## [ 2.2 ] - 18.02.2024

#### 🚀 Новые функции
- *(stats)* Полностью переработана страница "Личная статистика", добавлено много полезной информации и графики

## [ 2.1 ] - 03.01.2024

#### 🚀 Новые функции
- *(collection)* Добавлена страница просмотра городов коллекций по аналогии с городами региона - можно смотреть списком и на карте
- *(profile)* Страница "Профиль" разделена на 2 отдельные страницы - "Профиль", где теперь находится только персональная информация
с возможностью её изменения, а также "Личная статистика", куда была перенесена вся статистика по посещённым городам
- *(news)* Появилось отображение новых ещё непрочитанных новостей в боковом меню и в списке новостей. Теперь все пользователи будут видеть обновления сервиса

## [ 2.0.1 ] - 14.09.2023

#### 🚀 Новые функции
- *(logger)* Улучшено логирование
- *(seo)* Добавлена оптимизация для поисковых систем
- *(errors)* Добавлены страницы ошибок 403, 404, 500
#### 🐛 Исправление ошибок
- *(region)* На странице /region/<pk>/list для неавторизованного пользователя отображалось меню сортировки и фильтрации. Но в коде прописано, что у неавторизованного пользователя такой возможности быть не должно. Поэтому теперь без авторизации эти кнопки заблокированы

## [ 2.0 ] - 20.08.2023

#### 🚀 Новые функции
- *(db)* Переход с базы данных SQLite на PostgreSQL
#### 🎨 Дизайн
- Глобальное обновление дизайна всего сайта
#### 🧪 Тестирование
- Написано большое количество тестов
#### 🐛 Исправление ошибок
- *(city)* Неверная сортировка на странице городов конкретного региона и в профиле
- *(city)* Попытка отфильтровать города в общем списке и списке по региону приводила к ошибке

## [ 1.4 ] - 07.07.2023

#### 🚀 Новые функции
- Произведён переход с PIP на Poetry
- На страницы со списков городов, регионов и коллекций добавлена панель со статистической информацией
- *(city)* На страницу добавления нового посещённого города был добавлен вспомогательный текст для всех элементов формы, который более подробно объясняет, что означают эти элементы формы

## [ 1.3 ] - 22.06.2023

#### 🚀 Новые функции
- *(collection)* Добавлен функционал "Коллекции". Теперь можно собирать посещённые города не только по регионам, но и по другим различным коллекциям (например, Золотое кольцо или все города на Волге)

## [ 1.2 ] - 28.04.2023

#### 🚀 Новые функции
- *(region)* Обновлена страница выдачи городов конкретного региона. Теперь в списке отображаются все города региона, а не только посещённые. Это удобно, чтобы планировать будущие поездки или просто смотреть информацию о регионе
- *(city)* Обновлён дизайн списка городов (в общем списке и по региону). Теперь на странице городов региона посещённые выделяются зелёным цветом
- *(region)* Реализован доступ неавторизованным пользователям на страницу со списком регионов и списком городов в конкретном регионе
- *(news)* Новости переведены на Markdown-формат. Также добавлен Markdown-радактор в админ-панель
- *(logger)* Улучшено логирование - добавлена возможность отправки системных ошибок на электронную почту
