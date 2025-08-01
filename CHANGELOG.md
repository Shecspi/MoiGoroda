# Changelog

В этом файле задокументированы все значимые изменения проекта "Мои города".

## [ Подготовка нового релиза ]

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


#### 🐛 Исправление ошибок

- *(sidebar)* Исправлен баг с циклической прокруткой содержимого при скролле на сайдбаре ([ec8512a](https://github.com/Shecspi/MoiGoroda/commit/ec8512a5d279840a62d42c8dd1b9db7dc372677e))

- *(share)* Исправлено отображение посещенных городов на странице просмотра статистики другого пользователя ([5faf279](https://github.com/Shecspi/MoiGoroda/commit/5faf279afbd549a598d024ed6c85fb31268f736c))

- *(couontry)* Добавлен заголовок для страницы карты стран мира ([5fdb443](https://github.com/Shecspi/MoiGoroda/commit/5fdb443098bbb207e2e8bc84555c0c1681be1656))

- *(dashboard)* Исправлена ошибка сортировки добавленных стран в дашборде ([6690a8e](https://github.com/Shecspi/MoiGoroda/commit/6690a8e7c180def197add7c959f10ec9bede197c))

- *(stats)* Исправление ошибки, из-за которой не обрабатывался последний месяц года и статистика не загружалась ([c3b938d](https://github.com/Shecspi/MoiGoroda/commit/c3b938d472ba57ff9852afec7c444f56477627ba))

- *(stats)* На странице статистики пользователя изменены сообщения об отсутствии посещённых городов на корректные как для личной статистики, так и для статистики другого пользователя ([ff41aa9](https://github.com/Shecspi/MoiGoroda/commit/ff41aa9ee79f6e6cf80d354fcddf859292fc6f97))

- *(collection)* Исправлена ошибка, из-за которой неавторизованные пользователи могли получать страницу 500, когда пытались воспользоваться сортировкой ([e5ca63a](https://github.com/Shecspi/MoiGoroda/commit/e5ca63aa8156b59aa2fb3dfd32c49927e58af6d1))


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
