(() => {
  const PAGE = document.documentElement.dataset.page || 'home';
  const C = {
    ru: {
      brand: 'Мухамед', n1: 'Правила сети', n4: 'Мультиссылка', n2: 'Мониторинг сети', n3: 'YouTube-проєкти',
      bhl: 'Сокращатель ссылок', edge: 'Мухамед Ads — Сокращатель ссылок',
      m1: 'Длинные адреса — в короткие ссылки', m2: 'Один клик — одна ссылка', m3: 'Мгновенно, точно, надёжно',
      m4: 'Только безопасные http и https', m5: 'Мухамед Ads', m6: 'Креативная и технологическая сеть',
      m7: 'Умные ссылки', m8: 'Сожми адрес — делись без границ'
    },
    uk: {
      brand: 'Мухамед', n1: 'Правила мережі', n4: 'Мультипосилання', n2: 'Моніторинг мережі', n3: 'YouTube-проєкти',
      bhl: 'Скорочувач посилань', edge: 'Мухамед Ads — Скорочувач посилань',
      m1: 'Довгі адреси — в короткі посилання', m2: 'Один клік — одне посилання', m3: 'Миттєво, точно, надійно',
      m4: 'Лише безпечні http та https', m5: 'Мухамед Ads', m6: 'Креативна та технологічна мережа',
      m7: 'Розумні посилання', m8: 'Стисни адресу — ділись без меж'
    },
    en: {
      brand: 'Muhamed', n1: 'Network rules', n4: 'Multilink', n2: 'Network monitoring', n3: 'YouTube projects',
      bhl: 'Link shortener', edge: 'Muhamed Ads — Link shortener',
      m1: 'Long addresses — into short links', m2: 'One click — one link', m3: 'Instant, precise, reliable',
      m4: 'Only safe http and https', m5: 'Muhamed Ads', m6: 'Creative & Technology Network',
      m7: 'Smart links', m8: 'Compress the address — share without limits'
    }
  };
  const P = {
    ru: {
      home: {
        title: 'Мухамед Ads — креативно-технологическая сеть | Сократитель',
        desc: 'Предоставляем удобный инструмент для создания коротких ссылок, упрощая обмен адресами и делая переход к нужным ресурсам быстрее и комфортнее.',
        bs1: 'Запуск сервиса', bs2: 'Хранилище ссылок', bs3: 'Защита переходов', bs4: 'Сервис готов',
        kick: 'Умный сокращатель сети', h1a: 'Умные', h1b: 'ссылки', h1c: 'превращайте длинные адреса в короткие',
        typed: ['Вставьте длинный адрес', 'Нажмите — адрес сожмётся', 'Ссылка в буфере — делитесь'],
        lead: 'Любой длинный адрес — в одну короткую ссылку за мгновение.\nОна копируется сама — вам остаётся только отправить её дальше.',
        f1: 'ссылок создано в сети', f2: 'переходов по ссылкам', f4: 'переходов у самой популярной ссылки',
        fl: 'Ваша длинная ссылка', ph: 'https://example.com/очень/длинная/ссылка', go: 'Сократить',
        hint: '', tg1: 'Мгновенно', tg2: 'Любые адреса', tg3: 'Удобно делиться',
        res: 'Ваша короткая ссылка готова', cp: 'Копировать', cpd: 'Скопировано', op: 'Открыть', to: 'Ведёт на', again: 'Сократить ещё', ed: 'Изменить адрес', sv: 'Сохранить', edok: 'Адрес обновлён', copied: 'Ссылка скопирована', e_forbidden: 'Эту ссылку может менять только её автор.',
        sht: 'Умный сокращатель',
        busy: 'Сжимаем адрес…',
        sx_h: 'Как работает сокращатель ссылок', sx_p: 'Бесплатный сервис коротких ссылок без регистрации: вставьте длинный адрес и получите компактную ссылку, которой удобно делиться в мессенджерах, соцсетях и на любых площадках.', st1t: 'Вставьте адрес', st1p: 'Скопируйте любую длинную ссылку с http или https и вставьте её в поле выше.', st2t: 'Нажмите «Сократить»', st2p: 'Короткая ссылка создаётся за мгновение и сразу копируется в буфер обмена.', st3t: 'Делитесь', st3p: 'Отправляйте ссылку друзьям и клиентам — переход работает на любых устройствах.', fq_h: 'Частые вопросы', q1: 'Как сократить ссылку?', a1: 'Вставьте длинный адрес в поле на главной странице и нажмите «Сократить». Короткая ссылка создастся мгновенно и сама скопируется в буфер обмена.', q2: 'Сокращатель бесплатный?', a2: 'Да. Создание коротких ссылок бесплатное, регистрация не нужна.', q3: 'Сколько живёт короткая ссылка?', a3: 'Ссылка работает бессрочно, пока её не удалят из хранилища. Мы делаем резервные копии базы ссылок.', q4: 'Можно ли изменить адрес, на который ведёт короткая ссылка?', a4: 'Да, автор может изменить конечный адрес, не меняя саму короткую ссылку. Автор определяется по браузеру, в котором ссылка была создана.', q5: 'Какие ссылки можно сокращать?', a5: 'Любые адреса с протоколами http и https. Ссылки других сервисов-сокращателей и самого нашего сайта сокращать нельзя.', q6: 'Безопасно ли переходить по коротким ссылкам?', a6: 'Перед переходом показывается страница с итоговым доменом, а сам редирект работает только на безопасные http и https адреса.', more: 'Как это работает',
        e_url_required: 'Вставьте ссылку.', e_url_invalid: 'Это не похоже на ссылку. Нужен адрес с http:// или https://.',
        e_url_self: 'Нельзя сокращать уже короткую ссылку этого сервиса.', e_rate_limited: 'Слишком часто. Подождите минуту.',
        e_storage_down: 'Хранилище сейчас недоступно. Попробуйте чуть позже.', e_net: 'Нет связи с сервером. Попробуйте ещё раз.',
      },
      go: {
        title: 'Перенаправление трафика | Мухамед Ads', desc: 'Расшифровываем короткий код, прокладываем маршрут и открываем нужную страницу.',
        kick: 'Перенаправление трафика', h1a: 'Редирект', h1b: 'трафика', h1c: 'маршрут построен — летим к вашей цели',
        typed: ['Расшифровываем короткий код', 'Прокладываем маршрут к цели', 'Запускаем переход — держитесь'],
        lead: 'Трафик уже в пути — осталось несколько мгновений.\nНе закрывайте вкладку: переход начнётся автоматически.',
        sht: 'Маршрутизатор ссылок',
        sk1: 'Расшифровка кода', sk2: 'Запрос в хранилище', sk3: 'Прокладка маршрута', sk4: 'Запуск перехода',
        ok: 'Маршрут готов, открываем страницу', dst: 'пункт назначения', nf: 'Такой ссылки не существует', er: 'Не удалось получить адрес', retry: 'Повторить', now: 'Перейти сразу',
        b2: 'Сократить ссылку'
      },
      missing: {
        nf: 'Сократите новую ссылку',
        title: 'Ссылка не найдена | Мухамед Ads', desc: 'Такой короткой ссылки не существует.',
        kick: 'Ошибка 404', h1a: 'Ссылка', h1b: 'не найдена', h1c: 'такой короткой ссылки у нас нет',
        typed: ['Проверьте код в адресе ссылки', 'Возможно, ссылку уже удалили', 'Создайте новую за мгновение'],
        lead: 'Скорее всего, в коде опечатка или ссылку удалили.\nНичего страшного, создайте новую — она будет готова сразу.',
        b2: 'Сократить ссылку'
      }
    },
    uk: {
      home: {
        title: 'Мухамед Ads — креативно-технологічна мережа | Скорочувач',
        desc: 'Надаємо зручний інструмент для створення коротких посилань, спрощуючи обмін адресами та роблячи перехід до потрібних ресурсів швидшим і комфортнішим.',
        bs1: 'Запуск сервісу', bs2: 'Сховище посилань', bs3: 'Захист переходів', bs4: 'Сервіс готовий',
        kick: 'Розумний скорочувач мережі', h1a: 'Розумні', h1b: 'посилання', h1c: 'перетворюйте довгі адреси на короткі',
        typed: ['Вставте довгу адресу', 'Натисніть — адресу стиснуто', 'Посилання в буфері — діліться'],
        lead: 'Будь-яка довга адреса — в одне коротке посилання за мить.\nВоно копіюється саме — вам лишається лише надіслати його далі.',
        f1: 'посилань створено в мережі', f2: 'переходів за посиланнями', f4: 'переходів у найпопулярнішого посилання',
        fl: 'Ваше довге посилання', ph: 'https://example.com/дуже/довге/посилання', go: 'Скоротити',
        hint: '', tg1: 'Миттєво', tg2: 'Будь-які адреси', tg3: 'Зручно ділитися',
        res: 'Ваше коротке посилання готове', cp: 'Копіювати', cpd: 'Скопійовано', op: 'Відкрити', to: 'Веде на', again: 'Скоротити ще', ed: 'Змінити адресу', sv: 'Зберегти', edok: 'Адресу оновлено', copied: 'Посилання скопійовано', e_forbidden: 'Це посилання може змінювати лише його автор.',
        sht: 'Розумний скорочувач',
        busy: 'Стискаємо адресу…',
        sx_h: 'Як працює скорочувач посилань', sx_p: 'Безкоштовний сервіс коротких посилань без реєстрації: вставте довгу адресу й отримайте компактне посилання, яким зручно ділитися в месенджерах, соцмережах та на будь-яких майданчиках.', st1t: 'Вставте адресу', st1p: 'Скопіюйте будь-яке довге посилання з http або https і вставте його в поле вище.', st2t: 'Натисніть «Скоротити»', st2p: 'Коротке посилання створюється миттєво й одразу копіюється в буфер обміну.', st3t: 'Діліться', st3p: 'Надсилайте посилання друзям і клієнтам — перехід працює на будь-яких пристроях.', fq_h: 'Поширені запитання', q1: 'Як скоротити посилання?', a1: 'Вставте довгу адресу в поле на головній сторінці й натисніть «Скоротити». Коротке посилання створиться миттєво й саме скопіюється в буфер обміну.', q2: 'Скорочувач безкоштовний?', a2: 'Так. Створення коротких посилань безкоштовне, реєстрація не потрібна.', q3: 'Скільки живе коротке посилання?', a3: 'Посилання працює безстроково, доки його не видалять зі сховища. Ми робимо резервні копії бази посилань.', q4: 'Чи можна змінити адресу, на яку веде коротке посилання?', a4: 'Так, автор може змінити кінцеву адресу, не змінюючи саме коротке посилання. Автора визначає браузер, у якому посилання було створене.', q5: 'Які посилання можна скорочувати?', a5: 'Будь-які адреси з протоколами http та https. Посилання інших скорочувачів і нашого сайту скорочувати не можна.', q6: 'Чи безпечно переходити за короткими посиланнями?', a6: 'Перед переходом показується сторінка з підсумковим доменом, а сам редирект працює лише на безпечні http та https адреси.', more: 'Як це працює',
        e_url_required: 'Вставте посилання.', e_url_invalid: 'Це не схоже на посилання. Потрібна адреса з http:// або https://.',
        e_url_self: 'Не можна скорочувати вже коротке посилання цього сервісу.', e_rate_limited: 'Занадто часто. Зачекайте хвилину.',
        e_storage_down: 'Сховище зараз недоступне. Спробуйте трохи згодом.', e_net: 'Немає звʼязку із сервером. Спробуйте ще раз.',
      },
      go: {
        title: 'Перенаправлення трафіку | Мухамед Ads', desc: 'Розшифровуємо короткий код, прокладаємо маршрут і відкриваємо потрібну сторінку.',
        kick: 'Перенаправлення трафіку', h1a: 'Редирект', h1b: 'трафіку', h1c: 'маршрут збудовано — летимо до вашої цілі',
        typed: ['Розшифровуємо короткий код', 'Прокладаємо маршрут до цілі', 'Запускаємо перехід — тримайтеся'],
        lead: 'Трафік уже в дорозі — лишилося кілька миттєвостей.\nНе закривайте вкладку: перехід почнеться автоматично.',
        sht: 'Маршрутизатор посилань',
        sk1: 'Розшифровка коду', sk2: 'Запит до сховища', sk3: 'Прокладання маршруту', sk4: 'Запуск переходу',
        ok: 'Маршрут готовий, відкриваємо сторінку', dst: 'пункт призначення', nf: 'Такого посилання не існує', er: 'Не вдалося отримати адресу', retry: 'Повторити', now: 'Перейти одразу',
        b2: 'Скоротити посилання'
      },
      missing: {
        nf: 'Скоротіть нове посилання',
        title: 'Посилання не знайдено | Мухамед Ads', desc: 'Такого короткого посилання не існує.',
        kick: 'Помилка 404', h1a: 'Посилання', h1b: 'не знайдено', h1c: 'такого короткого посилання немає',
        typed: ['Перевірте код в адресі посилання', 'Можливо, посилання вже видалили', 'Створіть нове за мить'],
        lead: 'Найімовірніше, у коді помилка або посилання видалили.\nНічого страшного, створіть нове — воно буде готове одразу.',
        b2: 'Скоротити посилання'
      }
    },
    en: {
      home: {
        title: 'Muhamed Ads — creative & technology network | Shortener',
        desc: 'We provide a convenient tool for creating short links, making it easier to share addresses and getting you to the resources you need faster and more comfortably.',
        bs1: 'Starting the service', bs2: 'Link storage', bs3: 'Securing redirects', bs4: 'Service ready',
        kick: 'Smart network shortener', h1a: 'Smart', h1b: 'links', h1c: 'turn long addresses into short links',
        typed: ['Paste a long address', 'Press — it gets compressed', 'Link is copied — share it'],
        lead: 'Any long address becomes one short link in a heartbeat.\nIt copies itself — all that is left is to send it on.',
        f1: 'links created in the network', f2: 'visits through links', f4: 'visits on the most popular link',
        fl: 'Your long link', ph: 'https://example.com/a/very/long/link', go: 'Shorten',
        hint: '', tg1: 'Instant', tg2: 'Any address', tg3: 'Easy to share',
        res: 'Your short link is ready', cp: 'Copy', cpd: 'Copied', op: 'Open', to: 'Leads to', again: 'Shorten another', ed: 'Change address', sv: 'Save', edok: 'Address updated', copied: 'Link copied', e_forbidden: 'Only the author can change this link.',
        sht: 'Smart shortener',
        busy: 'Compressing…',
        sx_h: 'How the link shortener works', sx_p: 'A free short link service with no sign-up: paste a long address and get a compact link that is easy to share in messengers, social networks and anywhere else.', st1t: 'Paste the address', st1p: 'Copy any long http or https link and paste it into the field above.', st2t: 'Press “Shorten”', st2p: 'The short link is created instantly and copied to your clipboard right away.', st3t: 'Share it', st3p: 'Send the link to friends and customers — it works on any device.', fq_h: 'FAQ', q1: 'How do I shorten a link?', a1: 'Paste a long address into the field on the home page and press “Shorten”. The short link is created instantly and copied to your clipboard automatically.', q2: 'Is the shortener free?', a2: 'Yes. Creating short links is free and no registration is required.', q3: 'How long does a short link last?', a3: 'A link works indefinitely until it is removed from storage. We keep backups of the link database.', q4: 'Can I change where a short link points?', a4: 'Yes, the author can change the destination without changing the short link itself. The author is identified by the browser the link was created in.', q5: 'Which links can be shortened?', a5: 'Any address with the http or https protocol. Links from other shorteners and from this site cannot be shortened.', q6: 'Is it safe to open short links?', a6: 'A page showing the final domain appears before the jump, and the redirect only works for safe http and https addresses.', more: 'How it works',
        e_url_required: 'Paste a link.', e_url_invalid: 'That doesn’t look like a link. Use an address with http:// or https://.',
        e_url_self: 'You can’t shorten a short link of this service.', e_rate_limited: 'Too fast. Please wait a minute.',
        e_storage_down: 'Storage is unavailable right now. Try again shortly.', e_net: 'No connection to the server. Try again.',
      },
      go: {
        title: 'Traffic redirection | Muhamed Ads', desc: 'Decoding the short code, plotting the route and opening the right page.',
        kick: 'Traffic redirection', h1a: 'Traffic', h1b: 'redirect', h1c: 'route locked in — heading to your target',
        typed: ['Decoding the short code', 'Plotting the route to the target', 'Launching the jump — hold tight'],
        lead: 'Your traffic is already on its way — just a few moments left.\nKeep the tab open: the jump starts automatically.',
        sht: 'Link router',
        sk1: 'Code decoding', sk2: 'Storage request', sk3: 'Route plotting', sk4: 'Jump launch',
        ok: 'Route ready, opening the page', dst: 'destination', nf: 'This link does not exist', er: 'Could not get the address', retry: 'Retry', now: 'Go now',
        b2: 'Shorten a link'
      },
      missing: {
        nf: 'Shorten a new link',
        title: 'Link not found | Muhamed Ads', desc: 'This short link does not exist.',
        kick: 'Error 404', h1a: 'Link', h1b: 'not found', h1c: 'this short link does not exist',
        typed: ['Check the code in the link address', 'The link may have been removed already', 'Create a new one in a moment'],
        lead: 'Most likely the code has a typo, or the link was removed.\nNo worries, create a new one — it will be ready right away.',
        b2: 'Shorten a link'
      }
    }
  };
  window.SHORT_D = {};
  ['ru', 'uk', 'en'].forEach(l => { window.SHORT_D[l] = Object.assign({}, C[l], P[l][PAGE] || P[l].home); });
})();
