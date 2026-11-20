(() => {
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const D = {
    ru: {
      net: 'Креативная и технологическая сеть',
      f3: 'ревизия',
      n5: 'Язык',
      n6: 'Частые вопросы',
      s1: 'Игровые новости и обзоры',
      s2: 'Свободная музыка с драйвом',
      s3: 'Эфиры и общение со зрителями',
      s4: 'Обзоры и подборки аниме',
      s5: 'Кино, сериалы и мультфильмы',
      nm3: 'Стримус'
    },
    uk: {
      net: 'Креативна та технологічна мережа',
      f3: 'ревізія',
      n5: 'Мова',
      n6: 'Поширені запитання',
      s1: 'Ігрові новини та огляди',
      s2: 'Вільна музика з драйвом',
      s3: 'Ефіри та спілкування з глядачами',
      s4: 'Огляди та добірки аніме',
      s5: 'Кіно, серіали та мультфільми',
      nm3: 'Стримус'
    },
    en: {
      net: 'Creative & Technology Network',
      f3: 'updated',
      n5: 'Language',
      n6: 'FAQ',
      s1: 'Gaming news and reviews',
      s2: 'Free music with drive',
      s3: 'Streams and chatting with viewers',
      s4: 'Anime reviews and picks',
      s5: 'Movies, series and cartoons',
      nm3: 'Streamus'
    }
  };
  if (window.SHORT_D) Object.keys(window.SHORT_D).forEach(l => Object.assign(D[l] || (D[l] = {}), window.SHORT_D[l]));
  const LANGS = ['ru', 'uk', 'en'];
  const store = {
    get() { try { return localStorage.getItem('lang'); } catch (e) { return null; } },
    set(v) { try { localStorage.setItem('lang', v); } catch (e) {} }
  };
  function apply(l) {
    if (!D[l]) l = 'ru';
    const t = D[l];
    document.documentElement.lang = l;
    document.title = t.title;
    const md = document.querySelector('meta[name="description"]');
    if (md) md.content = t.desc;
    $$('[data-i18n]').forEach(el => {
      const v = t[el.dataset.i18n];
      if (v == null) return;
      if (el.classList.contains('lead')) {
        el.textContent = '';
        String(v).split('\n').forEach((ln, i) => {
          const sp = document.createElement('span');
          sp.className = 'ln';
          sp.style.setProperty('--li', i);
          sp.textContent = ln;
          el.appendChild(sp);
        });
        return;
      }
      el.textContent = v;
      if (el.hasAttribute('data-text')) el.setAttribute('data-text', v);
    });
    $$('[data-brand]').forEach(el => {
      el.innerHTML = t.brand + ' <b>Ads</b>';
      el.setAttribute('data-text', t.brand + ' Ads');
    });
    $$('.typed .t').forEach(el => { el.dataset.type = JSON.stringify(t.typed); el.dispatchEvent(new Event('retype')); });
    $$('.lang-cur').forEach(el => el.textContent = l === 'uk' ? 'UA' : l.toUpperCase());
    $$('[data-lang]').forEach(b => {
      const on = b.dataset.lang === l;
      b.classList.toggle('on', on);
      b.setAttribute('aria-pressed', on);
    });
  }
  function set(l) { store.set(l); apply(l); document.dispatchEvent(new Event('langchange')); }
  $$('[data-lang]').forEach(b => b.addEventListener('click', () => set(b.dataset.lang)));
  window.setLang = set;
  window.getLangDict = () => D[document.documentElement.lang] || D.ru;
  apply(store.get() || 'ru');
})();
