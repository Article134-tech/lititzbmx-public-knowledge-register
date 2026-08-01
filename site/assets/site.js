document.addEventListener("DOMContentLoaded", () => {
  const menuButton = document.querySelector(".nav-toggle");
  const menu = document.getElementById("primary-nav");
  if (menuButton && menu) {
    const closeMenu = () => {
      menuButton.setAttribute("aria-expanded", "false");
      menu.classList.remove("is-open");
      document.body.classList.remove("menu-open");
    };
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") !== "true";
      menuButton.setAttribute("aria-expanded", String(open));
      menu.classList.toggle("is-open", open);
      document.body.classList.toggle("menu-open", open && innerWidth <= 980);
    });
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    addEventListener("resize", () => { if (innerWidth > 980) closeMenu(); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") { closeMenu(); menuButton.focus(); }
    });
  }

  const clearHighlights = (root) => {
    root.querySelectorAll("mark[data-filter-mark]").forEach((mark) => {
      mark.replaceWith(document.createTextNode(mark.textContent));
    });
    root.normalize();
  };

  const highlight = (root, query) => {
    if (!query) return;
    const needle = query.toLowerCase();
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent || parent.closest("script,style,mark,.status,button,select,option")) return NodeFilter.FILTER_REJECT;
        return node.nodeValue.toLowerCase().includes(needle) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      const text = node.nodeValue;
      const index = text.toLowerCase().indexOf(needle);
      if (index < 0) return;
      const fragment = document.createDocumentFragment();
      fragment.append(text.slice(0, index));
      const mark = document.createElement("mark");
      mark.dataset.filterMark = "true";
      mark.textContent = text.slice(index, index + query.length);
      fragment.append(mark, text.slice(index + query.length));
      node.replaceWith(fragment);
    });
  };

  document.querySelectorAll("[data-filter-tools]").forEach((tools) => {
    const target = document.getElementById(tools.dataset.target);
    const input = tools.querySelector("[data-filter-input]");
    const reset = tools.querySelector("[data-filter-reset]");
    const matchCount = tools.querySelector("[data-filter-count]");
    const visibleCount = tools.querySelector("[data-visible-count]");
    const empty = tools.querySelector("[data-filter-empty]");
    const more = tools.querySelector("[data-filter-more]");
    const sort = tools.querySelector("[data-record-sort]");
    const selects = [...tools.querySelectorAll("[data-record-filter]")];
    if (!target || !input || !reset || !matchCount || !empty) return;

    const items = [...target.querySelectorAll("[data-filter-item]")];
    const total = items.length;
    const pageSize = Number.parseInt(target.dataset.pageSize || "0", 10) || 0;
    let visibleLimit = pageSize || Number.POSITIVE_INFINITY;

    const sortItems = (list) => {
      if (!sort) return list;
      const mode = sort.value;
      const value = (item, key) => (item.dataset[key] || "").toLowerCase();
      return [...list].sort((a, b) => {
        if (mode === "id-desc") return value(b, "id").localeCompare(value(a, "id"));
        if (mode === "oldest") return value(a, "year").localeCompare(value(b, "year")) || value(a, "id").localeCompare(value(b, "id"));
        if (mode === "newest") return value(b, "year").localeCompare(value(a, "year")) || value(a, "id").localeCompare(value(b, "id"));
        if (mode === "title") return value(a, "title").localeCompare(value(b, "title"));
        if (mode === "category") return value(a, "categoryLabel").localeCompare(value(b, "categoryLabel")) || value(a, "id").localeCompare(value(b, "id"));
        return value(a, "id").localeCompare(value(b, "id"));
      });
    };

    const update = ({ resetPage = true } = {}) => {
      if (resetPage) visibleLimit = pageSize || Number.POSITIVE_INFINITY;
      clearHighlights(target);
      const query = input.value.trim();
      const lowerQuery = query.toLowerCase();

      let matches = items.filter((item) => {
        const searchMatch = !lowerQuery || item.textContent.toLowerCase().includes(lowerQuery);
        const filterMatch = selects.every((select) => {
          const expected = select.value;
          if (!expected) return true;
          const key = select.dataset.recordFilter;
          return (item.dataset[key] || "") === expected;
        });
        return searchMatch && filterMatch;
      });

      matches = sortItems(matches);
      if (sort) matches.forEach((item) => target.appendChild(item));

      const matchSet = new Set(matches);
      items.forEach((item) => { item.hidden = true; });
      let shown = 0;
      matches.forEach((item, index) => {
        const show = index < visibleLimit;
        item.hidden = !show;
        if (show) {
          shown += 1;
          if (query) highlight(item, query);
        }
      });

      matchCount.textContent = String(matches.length);
      if (visibleCount) visibleCount.textContent = String(shown);
      empty.hidden = matches.length !== 0;
      if (more) {
        more.hidden = !pageSize || shown >= matches.length;
        if (!more.hidden) more.textContent = `Load ${Math.min(pageSize, matches.length - shown)} more`;
      }

      const summary = tools.querySelector(".filter-summary");
      if (summary && !visibleCount) {
        summary.lastChild.textContent = pageSize
          ? ` matching · ${shown} visible of ${total} total`
          : ` of ${total} ${tools.dataset.noun || "items"} shown`;
      }
    };

    input.addEventListener("input", () => update());
    selects.forEach((select) => select.addEventListener("change", () => update()));
    if (sort) sort.addEventListener("change", () => update());
    if (more) more.addEventListener("click", () => {
      visibleLimit += pageSize;
      update({ resetPage: false });
    });
    reset.addEventListener("click", () => {
      input.value = "";
      selects.forEach((select) => { select.value = ""; });
      if (sort) sort.value = "id-asc";
      update();
      input.focus();
    });

    update();
  });
});
