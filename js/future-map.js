(function () {
  "use strict";

  const ns = "http://www.w3.org/2000/svg";
  const copyByLanguage = {
    en: { proposal: "Proposal", caveat: "Critical caveat", region: "Region", status: "Status", open: "Open source", yes: "yes", no: "no", links: "Original materials", shown: "entries shown", empty: "No entries match these filters." },
    ru: { proposal: "Что предлагают", caveat: "Критическая оговорка", region: "Регион", status: "Статус", open: "Открытый код", yes: "да", no: "нет", links: "Оригинальные материалы", shown: "позиций показано", empty: "По этим фильтрам ничего не найдено." },
    uk: { proposal: "Що пропонують", caveat: "Критичне застереження", region: "Регіон", status: "Статус", open: "Відкритий код", yes: "так", no: "ні", links: "Оригінальні матеріали", shown: "позицій показано", empty: "За цими фільтрами нічого не знайдено." }
  };

  function localized(value, language) {
    if (typeof value === "string") return value;
    return value && (value[language] || value.en || value.ru || value.uk) || "";
  }

  function element(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text) item.textContent = text;
    return item;
  }

  function addDetail(details, label, value) {
    const paragraph = element("p", "future-map__meta");
    paragraph.append(element("strong", "", `${label}: `), document.createTextNode(value));
    details.appendChild(paragraph);
  }

  function init(root) {
    const dataElement = root.querySelector(".future-map__data");
    const svg = root.querySelector(".future-map__svg");
    const details = root.querySelector(".future-map__details");
    if (!dataElement || !svg || !details) return;

    let data;
    try {
      data = JSON.parse(dataElement.textContent);
      if (typeof data === "string") data = JSON.parse(data);
    } catch (_) { return; }
    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.edges)) return;
    const language = data.lang || "en";
    const copy = copyByLanguage[language] || copyByLanguage.en;
    const nodes = new Map(data.nodes.map((node) => [node.id, node]));
    const cards = [...root.querySelectorAll(".future-map__card")];
    const search = root.querySelector("[data-map-search]");
    const count = root.querySelector("[data-map-count]");
    let role = "all";
    let theme = "all";

    function matches(node) {
      const roleMatch = role === "all" || node.role === role || (role === "open-source" && node.open_source);
      const themeMatch = theme === "all" || (node.themes || []).includes(theme);
      const query = (search && search.value || "").trim().toLocaleLowerCase(language);
      const haystack = [node.name, node.summary, node.proposal, node.caveat, node.region, node.status]
        .map((value) => localized(value, language)).join(" ").toLocaleLowerCase(language);
      return roleMatch && themeMatch && (!query || haystack.includes(query));
    }

    function showDetails(node) {
      details.replaceChildren();
      details.appendChild(element("h3", "", localized(node.name, language)));
      details.appendChild(element("p", "", localized(node.summary, language)));
      addDetail(details, copy.proposal, localized(node.proposal, language));
      addDetail(details, copy.caveat, localized(node.caveat, language));
      addDetail(details, copy.region, localized(node.region, language));
      addDetail(details, copy.status, localized(node.status, language));
      addDetail(details, copy.open, node.open_source ? copy.yes : copy.no);
      const heading = element("h4", "", copy.links);
      const links = element("div", "future-map__links");
      (node.links || []).forEach((link) => {
        const anchor = element("a", "", link.label);
        anchor.href = link.url;
        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";
        links.appendChild(anchor);
      });
      details.append(heading, links);
    }

    function draw(visibleNodes) {
      svg.replaceChildren();
      const title = document.createElementNS(ns, "title");
      title.textContent = root.getAttribute("aria-label") || "Map";
      svg.appendChild(title);
      if (!visibleNodes.length) {
        const label = document.createElementNS(ns, "text");
        label.setAttribute("x", "500"); label.setAttribute("y", "90"); label.setAttribute("text-anchor", "middle");
        label.textContent = copy.empty; svg.appendChild(label); svg.setAttribute("viewBox", "0 0 1000 180"); return;
      }
      const columns = Math.min(4, Math.max(1, Math.ceil(Math.sqrt(visibleNodes.length * 1.5))));
      const width = 1000, cellWidth = width / columns, cellHeight = 118;
      const positions = new Map();
      visibleNodes.forEach((node, index) => positions.set(node.id, { x: (index % columns) * cellWidth + cellWidth / 2, y: Math.floor(index / columns) * cellHeight + 64 }));
      const height = Math.ceil(visibleNodes.length / columns) * cellHeight + 20;
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
      data.edges.forEach((edge) => {
        const from = positions.get(edge.from), to = positions.get(edge.to);
        if (!from || !to) return;
        const line = document.createElementNS(ns, "line");
        line.setAttribute("x1", from.x); line.setAttribute("y1", from.y); line.setAttribute("x2", to.x); line.setAttribute("y2", to.y);
        line.setAttribute("class", "future-map__edge"); svg.appendChild(line);
      });
      visibleNodes.forEach((node) => {
        const position = positions.get(node.id);
        const group = document.createElementNS(ns, "g");
        group.setAttribute("class", `future-map__node future-map__node--${node.role}`);
        group.setAttribute("tabindex", "0"); group.setAttribute("role", "button"); group.setAttribute("aria-label", localized(node.name, language));
        const box = document.createElementNS(ns, "rect");
        box.setAttribute("x", position.x - cellWidth * .4); box.setAttribute("y", position.y - 38);
        box.setAttribute("width", cellWidth * .8); box.setAttribute("height", "76"); box.setAttribute("rx", "12");
        const label = document.createElementNS(ns, "text");
        label.setAttribute("x", position.x); label.setAttribute("y", position.y + 4); label.setAttribute("text-anchor", "middle");
        const name = localized(node.name, language);
        label.textContent = name.length > 30 ? `${name.slice(0, 28)}…` : name;
        group.append(box, label); svg.appendChild(group);
        group.addEventListener("click", () => showDetails(node));
        group.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); showDetails(node); } });
      });
    }

    function update() {
      const visible = data.nodes.filter(matches);
      cards.forEach((card) => { card.hidden = !visible.some((node) => node.id === card.dataset.nodeId); });
      if (count) count.textContent = `${visible.length} / ${data.nodes.length} ${copy.shown}`;
      draw(visible);
    }

    root.querySelectorAll("[data-map-filter]").forEach((button) => button.addEventListener("click", () => {
      role = button.dataset.mapFilter;
      root.querySelectorAll("[data-map-filter]").forEach((item) => item.classList.toggle("is-active", item === button)); update();
    }));
    root.querySelectorAll("[data-map-theme]").forEach((button) => button.addEventListener("click", () => {
      theme = button.dataset.mapTheme;
      root.querySelectorAll("[data-map-theme]").forEach((item) => item.classList.toggle("is-active", item === button)); update();
    }));
    root.querySelectorAll("[data-map-inspect]").forEach((button) => button.addEventListener("click", () => {
      const node = nodes.get(button.dataset.mapInspect); if (node) { showDetails(node); details.scrollIntoView({ behavior: "smooth", block: "nearest" }); }
    }));
    if (search) search.addEventListener("input", update);
    update();
  }

  document.querySelectorAll(".future-map").forEach(init);
}());
