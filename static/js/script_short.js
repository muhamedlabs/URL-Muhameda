(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const T = () => (window.getLangDict ? window.getLangDict() : {});
  const PAGE = document.documentElement.dataset.page;

    function home() {
    const form = $('#shForm'), inp = $('#shUrl'), err = $('#shErr'), hint = $('#shHint'), go = $('#shGo');
    const res = $('#shRes'), short = $('#shShort'), copy = $('#shCopy');
    let lastErr = '', busy = false, lastRes = null;
    const setPh = () => { inp.placeholder = T().ph || inp.placeholder; };
    setPh(); document.addEventListener('langchange', () => { setPh(); if (lastErr) showErr(lastErr); });

    function showErr(code) {
      lastErr = code;
      err.textContent = T()['e_' + code] || T().e_net || code;
      err.hidden = false; hint.hidden = true;
    }
    function clearErr() { lastErr = ''; err.hidden = true; hint.hidden = false; }

    const tt = $('#toast'), tx = $('#toastTx');
    let tm = 0;
    function toast(key) {
      tx.textContent = T()[key] || '';
      tt.classList.remove('on'); void tt.offsetWidth; tt.classList.add('on');
      clearTimeout(tm); tm = setTimeout(() => tt.classList.remove('on'), 2200);
    }
    async function copyText(v) {
      try { await navigator.clipboard.writeText(v); }
      catch (_) { const t = document.createElement('textarea'); t.value = v; document.body.appendChild(t); t.select(); try { document.execCommand('copy'); } catch (__) {} t.remove(); }
    }
    const setTt = () => $$('[data-tt]').forEach(b => { b.title = T()[b.dataset.tt] || ''; b.setAttribute('aria-label', b.title); });
    setTt(); document.addEventListener('langchange', setTt);

    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (busy) return;
      const url = inp.value.trim();
      if (!url) { showErr('url_required'); inp.focus(); return; }
      clearErr(); busy = true; go.disabled = true;
      const lab = $('span', go), old = lab.textContent; lab.textContent = T().busy || '…';
      try {
        const r = await fetch('/api/shorten', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok) { showErr(j.error || (r.status === 429 ? 'rate_limited' : r.status === 503 ? 'storage_down' : 'net')); return; }
        lastRes = j;
        short.textContent = j.short_url.replace(/^https?:\/\//, '');
        short.href = j.short_url;
        form.hidden = true; res.hidden = false;
        copyText(j.short_url).then(() => toast('copied'));
      } catch (_) { showErr('net'); }
      finally { busy = false; go.disabled = false; lab.textContent = T().go || old; }
    });
    inp.addEventListener('input', () => { if (lastErr) clearErr(); });

    copy.addEventListener('click', async () => {
      if (!lastRes) return;
      const lab = $('span', copy), ico = $('i', copy);
      await copyText(lastRes.short_url);
      toast('copied');
      lab.textContent = T().cpd || 'OK'; ico.className = 'fa-solid fa-check';
      setTimeout(() => { lab.textContent = T().cp; ico.className = 'fa-solid fa-copy'; }, 1800);
    });
    $('#shAgain').addEventListener('click', () => { res.hidden = true; form.hidden = false; inp.value = ''; inp.focus(); });
  }

    function seekPage() {
    const B = document.body, code = B.dataset.code || '';
    const DELAY = Math.max(0, parseFloat(B.dataset.delay || '5'));
    const box = $('#seek'), num = $('#skNum'), bar = $('#skBar');
    const lis = $$('#skSteps li'), msg = $('#skMsg'), act = $('#skAct');
    let run = 0, found = null;

    const resolve = async () => {
      const ac = new AbortController(), to = setTimeout(() => ac.abort(), 8000);
      let r; try { r = await fetch('/api/resolve/' + encodeURIComponent(code), { cache: 'no-store', signal: ac.signal }); } finally { clearTimeout(to); }
      if (r.status === 404) return { missing: true };
      if (!r.ok) throw new Error('http ' + r.status);
      const j = await r.json();
      return j.ok ? j : { missing: true };
    };
    const paint = (n, all) => lis.forEach((li, i) => {
      const done = all || i < n;
      li.classList.toggle('done', done); li.classList.toggle('on', !all && i === n);
      $('i', li).className = 'fa-solid ' + (done ? 'fa-check' : ['fa-fingerprint', 'fa-database', 'fa-magnifying-glass', 'fa-route'][i]);
    });
    
    const say = (key) => { msg.hidden = false; msg.textContent = T()[key] || ''; msg.dataset.k = key; };
    document.addEventListener('langchange', () => { if (!msg.hidden) say(msg.dataset.k); });

    function end(kind, url) {
      cancelAnimationFrame(end.raf);
      bar.style.transform = 'scaleX(1)';
      if (kind === 'go') {
        box.dataset.state = 'go'; num.textContent = '100'; paint(0, true);
        document.documentElement.classList.add('leaving');
        setTimeout(() => location.replace(url), reduce ? 0 : 520);
      } else {
        box.dataset.state = kind; paint(-1, false); say(kind === 'nf' ? 'nf' : 'er');
        if (kind === 'er') act.hidden = false;
      }
    }

    async function start() {
      const my = ++run; found = null; act.hidden = true; msg.hidden = true; box.dataset.state = 'search';
      const t0 = performance.now(), total = DELAY * 1000;
      let first = null, firstErr = null, firstDone = false, started1 = false, final = null, fin = false, step = -1;
      const tick = now => {
        if (my !== run) return;
        const el = now - t0, k = total ? Math.min(el / total, 1) : 1;
        bar.style.transform = 'scaleX(' + k.toFixed(4) + ')';
        num.textContent = String(Math.round(k * 100)).padStart(2, '0');
        const st = k < .22 ? 0 : k < .5 ? 1 : k < .8 ? 2 : 3;
        if (st !== step) { step = st; paint(st, false); }
        if (k >= .2 && !started1) { started1 = true; resolve().then(j => { first = j; }).catch(e => { firstErr = e; }).finally(() => { firstDone = true; }); }
        if (k >= .72 && !fin) {
          fin = true;
          resolve().then(j => { final = j; }).catch(() => { final = firstErr ? { err: true } : (first || { err: true }); });
        }
        if (k >= 1 && final) {
          if (final.missing) return end('nf');
          if (final.err) return end('er');
          return end('go', final.url);
        }
        end.raf = requestAnimationFrame(tick);
      };
      end.raf = requestAnimationFrame(tick);
    }
    $('#skRetry').addEventListener('click', start);
    start();
  }

    function oneScreen() {
    const el = $('#fit'), hero = $('.hero');
    if (!el || !hero) return;
    const root = document.documentElement;
    const mq = matchMedia('(min-width:1181px), (hover:hover) and (pointer:fine) and (min-width:700px), (orientation:landscape) and (min-aspect-ratio:3/2) and (min-width:700px)');
    let raf = 0;
    const calc = () => {
      raf = 0;
      root.classList.toggle('onescreen', mq.matches);
      if (!mq.matches) { el.style.removeProperty('--k'); return; }
      const cs = getComputedStyle(hero);
      const aw = hero.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      const ah = hero.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
      const h = el.offsetHeight || 1;
      const w = Math.max(1, ...[...el.children].map(c => c.offsetWidth));
      const up = 1;
      const k = Math.max(.35, Math.min(ah / h, aw / w, up));
      el.style.setProperty('--k', k.toFixed(4));
    };
    const ask = () => { if (!raf) raf = requestAnimationFrame(calc); };
    calc();
    addEventListener('resize', ask);
    mq.addEventListener ? mq.addEventListener('change', ask) : mq.addListener(ask);
    document.addEventListener('langchange', ask);
    if (window.ResizeObserver) new ResizeObserver(ask).observe(el);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(ask);
    addEventListener('load', ask);
  }
  oneScreen();

    function backdrop() {
    const box = $('#bgimg');
    if (!box || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const plates = [...box.querySelectorAll('i')];
    let n = 0;
    const swap = () => {
      const old = plates[n];
      n = (n + 1) % plates.length;
      const nxt = plates[n];
      old.classList.remove('on'); old.classList.add('prev');
      nxt.classList.add('on', 'glt');
      setTimeout(() => { old.classList.remove('prev'); nxt.classList.remove('glt'); }, 1500);
    };
    window.__bgTransition = () => {
      box.classList.add('tr');
      setTimeout(swap, 550);
      setTimeout(() => box.classList.remove('tr'), 1900);
    };
    setInterval(() => { if (!document.hidden) window.__bgTransition(); }, 12000);
  }
  backdrop();

  if (PAGE === 'home') home(); else if (PAGE === 'go') seekPage();
})();
