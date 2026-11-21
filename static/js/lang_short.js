(() => {
  const PAGE = document.documentElement.dataset.page || 'home';
  const C = {
    ru: {
      brand: 'Мухамед', n1: 'Правила сети', n4: 'Мультиссылка', n2: 'Мониторинг сети', n3: 'YouTube-проекты',
      bhl: 'Сокращатель ссылок', edge: 'Мухамед Ads — Сокращатель ссылок',
      m1: 'Длинные адреса в короткие ссылки', m2: 'Один клик, одна ссылка', m3: 'Мгновенно, точно, надёжно',
      m4: 'Только безопасные http и https', m5: 'Мухамед Ads', m6: 'Креативная и технологическая сеть',
      m7: 'Умные ссылки', m8: 'Сожми адрес и делись без границ'
    },
    uk: {
      brand: 'Мухамед', n1: 'Правила мережі', n4: 'Мультипосилання', n2: 'Моніторинг мережі', n3: 'YouTube-проєкти',
      bhl: 'Скорочувач посилань', edge: 'Мухамед Ads — Скорочувач посилань',
      m1: 'Довгі адреси в короткі посилання', m2: 'Один клік, одне посилання', m3: 'Миттєво, точно, надійно',
      m4: 'Лише безпечні http та https', m5: 'Мухамед Ads', m6: 'Креативна та технологічна мережа',
      m7: 'Розумні посилання', m8: 'Стисни адресу й ділись без меж'
    },
    en: {
      brand: 'Muhamed', n1: 'Network rules', n4: 'Multilink', n2: 'Network monitoring', n3: 'YouTube projects',
      bhl: 'Link shortener', edge: 'Muhamed Ads — Link shortener',
      m1: 'Long addresses into short links', m2: 'One click, one link', m3: 'Instant, precise, reliable',
      m4: 'Only safe http and https', m5: 'Muhamed Ads', m6: 'Creative & Technology Network',
      m7: 'Smart links', m8: 'Compress the address and share without limits'
    }
  };
  const P = {
    ru: {
      home: {
        title: 'Мухамед Ads — креативно-технологическая сеть | Сокращатель',
        desc: 'Предоставляем удобный инструмент для создания коротких ссылок, упрощая обмен адресами и делая переход к нужным ресурсам быстрее и комфортнее.',
        bs1: 'Запуск сервиса', bs2: 'Хранилище ссылок', bs3: 'Защита переходов', bs4: 'Сервис готов',
        kick: 'Умный сокращатель сети', h1a: 'Умные', h1b: 'ссылки', h1c: 'превращайте длинные адреса в короткие',
        typed: ['Вставьте длинный адрес в поле ввода', 'Нажмите кнопку, и адрес мгновенно сожмётся', 'Ссылка уже в буфере, делитесь с кем угодно', 'Даже самый длинный адрес станет компактным', 'Короткая ссылка откроет нужную страницу без лишних шагов', 'Делитесь в мессенджерах, соцсетях и письмах'],
        lead: 'Один аккуратный адрес вместо длинной ссылки.\nОн готов сразу и копируется сам, остаётся только поделиться.',
        f1: 'ссылок создано в сети', f2: 'переходов по ссылкам', f4: 'переходов у самой популярной ссылки',
        fl: 'Ваша длинная ссылка', ph: 'https://www.muhamedlabs.pro/ads/network/shortener', go: 'Сократить',

        res: 'Ваша короткая ссылка готова', cp: 'Копировать', cpd: 'Скопировано', to: 'Ведёт на', again: 'Сократить ещё', copied: 'Ссылка скопирована',
        sht: 'Умный сокращатель',
        busy: 'Сжимаем адрес…',
        e_url_required: 'Вставьте ссылку.', e_url_invalid: 'Это не похоже на ссылку. Нужен адрес с http:// или https://.',
        e_url_self: 'Нельзя сокращать уже короткую ссылку этого сервиса.', e_rate_limited: 'Слишком часто. Подождите минуту.',
        e_storage_down: 'Хранилище сейчас недоступно. Попробуйте чуть позже.', e_net: 'Нет связи с сервером. Попробуйте ещё раз.',
      },
      go: {
        title: 'Перенаправление трафика | Мухамед Ads', desc: 'Расшифровываем короткий код, прокладываем маршрут и открываем нужную страницу.',
        kick: 'Перенаправление трафика', h1a: 'Редирект', h1b: 'трафика', h1c: 'маршрут построен, летим к вашей цели',
        typed: ['Расшифровываем короткий код', 'Прокладываем маршрут к цели', 'Запускаем переход, держитесь'],
        lead: 'Ваш трафик уже в пути, осталось всего пару мгновений.\nНе закрывайте вкладку, переход начнётся сам.',
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
        lead: 'Похоже, в адресе опечатка, или такую ссылку уже удалили.\nНе беда: создайте новую, она будет готова сразу.',
        b2: 'Сократить ссылку'
      }
    },
    uk: {
      home: {
        title: 'Мухамед Ads — креативно-технологічна мережа | Скорочувач',
        desc: 'Надаємо зручний інструмент для створення коротких посилань, спрощуючи обмін адресами та роблячи перехід до потрібних ресурсів швидшим і комфортнішим.',
        bs1: 'Запуск сервісу', bs2: 'Сховище посилань', bs3: 'Захист переходів', bs4: 'Сервіс готовий',
        kick: 'Розумний скорочувач мережі', h1a: 'Розумні', h1b: 'посилання', h1c: 'перетворюйте довгі адреси на короткі',
        typed: ['Вставте довгу адресу в поле вводу', 'Натисніть кнопку, і адресу миттєво стиснуто', 'Посилання вже в буфері, діліться з ким завгодно', 'Навіть найдовша адреса стане компактною', 'Коротке посилання відкриє потрібну сторінку без зайвих кроків', 'Діліться в месенджерах, соцмережах і листах'],
        lead: 'Одна акуратна адреса замість довгого посилання.\nВона готова одразу й копіюється сама, лишається лише поділитися.',
        f1: 'посилань створено в мережі', f2: 'переходів за посиланнями', f4: 'переходів у найпопулярнішого посилання',
        fl: 'Ваше довге посилання', ph: 'https://www.muhamedlabs.pro/ads/network/shortener', go: 'Скоротити',

        res: 'Ваше коротке посилання готове', cp: 'Копіювати', cpd: 'Скопійовано', to: 'Веде на', again: 'Скоротити ще', copied: 'Посилання скопійовано',
        sht: 'Розумний скорочувач',
        busy: 'Стискаємо адресу…',
        e_url_required: 'Вставте посилання.', e_url_invalid: 'Це не схоже на посилання. Потрібна адреса з http:// або https://.',
        e_url_self: 'Не можна скорочувати вже коротке посилання цього сервісу.', e_rate_limited: 'Занадто часто. Зачекайте хвилину.',
        e_storage_down: 'Сховище зараз недоступне. Спробуйте трохи згодом.', e_net: 'Немає звʼязку із сервером. Спробуйте ще раз.',
      },
      go: {
        title: 'Перенаправлення трафіку | Мухамед Ads', desc: 'Розшифровуємо короткий код, прокладаємо маршрут і відкриваємо потрібну сторінку.',
        kick: 'Перенаправлення трафіку', h1a: 'Редирект', h1b: 'трафіку', h1c: 'маршрут збудовано, летимо до вашої цілі',
        typed: ['Розшифровуємо короткий код', 'Прокладаємо маршрут до цілі', 'Запускаємо перехід, тримайтеся'],
        lead: 'Ваш трафік уже в дорозі, лишилося лише кілька миттєвостей.\nНе закривайте вкладку, перехід почнеться сам.',
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
        lead: 'Схоже, в адресі помилка, або таке посилання вже видалили.\nНе біда: створіть нове, воно буде готове одразу.',
        b2: 'Скоротити посилання'
      }
    },
    en: {
      home: {
        title: 'Muhamed Ads — creative & technology network | Shortener',
        desc: 'We provide a convenient tool for creating short links, making it easier to share addresses and getting you to the resources you need faster and more comfortably.',
        bs1: 'Starting the service', bs2: 'Link storage', bs3: 'Securing redirects', bs4: 'Service ready',
        kick: 'Smart network shortener', h1a: 'Smart', h1b: 'links', h1c: 'turn long addresses into short links',
        typed: ['Paste a long address into the input field', 'Press the button and it gets compressed instantly', 'The link is already copied, share it with anyone', 'Even the longest address becomes compact', 'A short link opens the right page without extra steps', 'Share it in messengers, social networks and emails'],
        lead: 'One neat address instead of a long link.\nIt is ready at once and copies itself, all that is left is to share it.',
        f1: 'links created in the network', f2: 'visits through links', f4: 'visits on the most popular link',
        fl: 'Your long link', ph: 'https://www.muhamedlabs.pro/ads/network/shortener', go: 'Shorten',

        res: 'Your short link is ready', cp: 'Copy', cpd: 'Copied', to: 'Leads to', again: 'Shorten another', copied: 'Link copied',
        sht: 'Smart shortener',
        busy: 'Compressing…',
        e_url_required: 'Paste a link.', e_url_invalid: 'That doesn’t look like a link. Use an address with http:// or https://.',
        e_url_self: 'You can’t shorten a short link of this service.', e_rate_limited: 'Too fast. Please wait a minute.',
        e_storage_down: 'Storage is unavailable right now. Try again shortly.', e_net: 'No connection to the server. Try again.',
      },
      go: {
        title: 'Traffic redirection | Muhamed Ads', desc: 'Decoding the short code, plotting the route and opening the right page.',
        kick: 'Traffic redirection', h1a: 'Traffic', h1b: 'redirect', h1c: 'route locked in, heading to your target',
        typed: ['Decoding the short code', 'Plotting the route to the target', 'Launching the jump, hold tight'],
        lead: 'Your traffic is already on the way, just a moment to go.\nKeep this tab open, the redirect starts on its own.',
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
        lead: 'Looks like the address has a typo, or the link was deleted.\nNo problem: create a new one and it is ready at once.',
        b2: 'Shorten a link'
      }
    }
  };
  window.SHORT_D = {};
  ['ru', 'uk', 'en'].forEach(l => { window.SHORT_D[l] = Object.assign({}, C[l], P[l][PAGE] || P[l].home); });
})();
