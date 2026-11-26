// Header search: trips (places), tags and post titles, from /index.json.
(function () {
  var root = document.querySelector('[data-search]');
  if (!root) return;

  var input = root.querySelector('input');
  var panel = root.querySelector('[role="listbox"]');
  var LIMITS = { trips: 4, tags: 5, posts: 6 };
  var LABELS = { trips: 'Trips', tags: 'Tags', posts: 'Posts' };
  var index = null;
  var loading = null;
  var options = [];
  var active = -1;

  root.hidden = false;

  function normalize(text) {
    return String(text).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function prepare(data) {
    ['trips', 'tags', 'posts'].forEach(function (kind) {
      data[kind].forEach(function (item) {
        item.name = normalize(item.title);
        item.haystack = kind === 'posts'
          ? normalize([item.title, item.trip].concat(item.tags).join(' '))
          : item.name;
      });
    });
    return data;
  }

  function load() {
    if (!loading) {
      loading = fetch(root.dataset.index)
        .then(function (response) {
          if (!response.ok) throw new Error('Search index returned ' + response.status);
          return response.json();
        })
        .then(function (data) { index = prepare(data); })
        .catch(function (error) {
          loading = null;
          throw error;
        });
    }
    return loading;
  }

  // Lower is better; -1 means no match. Every typed word has to appear somewhere.
  function score(item, query, words) {
    for (var i = 0; i < words.length; i++) {
      if (item.haystack.indexOf(words[i]) === -1) return -1;
    }
    if (item.name.indexOf(query) === 0) return 0;
    if ((' ' + item.name).indexOf(' ' + words[0]) !== -1) return 1;
    if (item.name.indexOf(words[0]) !== -1) return 2;
    return 3;
  }

  function find(kind, query, words) {
    var hits = [];
    index[kind].forEach(function (item) {
      var s = score(item, query, words);
      if (s !== -1) hits.push({ item: item, score: s });
    });
    hits.sort(function (a, b) {
      if (a.score !== b.score) return a.score - b.score;
      if (kind === 'posts') return a.item.date < b.item.date ? 1 : -1;
      return (b.item.count || 0) - (a.item.count || 0);
    });
    return hits.slice(0, LIMITS[kind]).map(function (hit) { return hit.item; });
  }

  function detail(kind, item) {
    if (kind === 'posts') return item.trip + ' · ' + item.date.slice(0, 4);
    return item.count + (item.count === 1 ? ' post' : ' posts');
  }

  function close() {
    panel.hidden = true;
    panel.textContent = '';
    options = [];
    active = -1;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
  }

  function message(text) {
    panel.textContent = '';
    var note = document.createElement('p');
    note.className = 'site-search__note';
    note.textContent = text;
    panel.appendChild(note);
    options = [];
    active = -1;
    panel.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function render() {
    var query = normalize(input.value).trim();
    if (!query) return close();
    var words = query.split(/\s+/);

    panel.textContent = '';
    options = [];
    active = -1;
    input.removeAttribute('aria-activedescendant');

    ['trips', 'tags', 'posts'].forEach(function (kind) {
      var items = find(kind, query, words);
      if (!items.length) return;

      var group = document.createElement('div');
      group.setAttribute('role', 'group');
      group.setAttribute('aria-label', LABELS[kind]);

      var heading = document.createElement('p');
      heading.className = 'site-search__heading';
      heading.setAttribute('aria-hidden', 'true');
      heading.textContent = LABELS[kind];
      group.appendChild(heading);

      items.forEach(function (item) {
        var link = document.createElement('a');
        link.href = item.url;
        link.id = 'site-search-option-' + options.length;
        link.className = 'site-search__option';
        link.setAttribute('role', 'option');
        link.setAttribute('aria-selected', 'false');
        link.tabIndex = -1;

        var title = document.createElement('span');
        title.textContent = item.title;
        var meta = document.createElement('span');
        meta.className = 'site-search__meta';
        meta.textContent = detail(kind, item);

        link.appendChild(title);
        link.appendChild(meta);
        group.appendChild(link);
        options.push(link);
      });

      panel.appendChild(group);
    });

    if (!options.length) return message('No trips, tags or posts match.');
    panel.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function update() {
    if (index) return render();
    load().then(render, function () { message('Search is unavailable right now.'); });
  }

  function select(next) {
    if (!options.length) return;
    if (active !== -1) options[active].setAttribute('aria-selected', 'false');
    active = (next + options.length) % options.length;
    options[active].setAttribute('aria-selected', 'true');
    options[active].scrollIntoView({ block: 'nearest' });
    input.setAttribute('aria-activedescendant', options[active].id);
  }

  input.addEventListener('focus', function () {
    load().catch(function () {});
    if (input.value.trim()) update();
  });
  input.addEventListener('input', update);

  input.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      select(active + 1);
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      select(active === -1 ? options.length - 1 : active - 1);
    } else if (event.key === 'Enter') {
      var target = options[active === -1 ? 0 : active];
      if (target) {
        event.preventDefault();
        window.location.href = target.href;
      }
    } else if (event.key === 'Escape') {
      if (panel.hidden) input.blur();
      close();
    }
  });

  document.addEventListener('click', function (event) {
    if (!root.contains(event.target)) close();
  });

  // "/" focuses the search box unless the reader is already typing somewhere.
  document.addEventListener('keydown', function (event) {
    if (event.key !== '/' || event.metaKey || event.ctrlKey || event.altKey) return;
    var el = document.activeElement;
    if (el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
    event.preventDefault();
    input.focus();
  });
})();
