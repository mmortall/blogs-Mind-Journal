(function () {
  "use strict";

  const ns = "http://www.w3.org/2000/svg";
  const copyByLanguage = {
    en: { proposal: "Proposal", caveat: "Critical caveat", region: "Region", status: "Status", open: "Open source", yes: "yes", no: "no", links: "Mind Journal and original materials", article: "Mind Journal article", shown: "entries shown", empty: "No entries match these filters.", fullscreen: "Full screen", exitFullscreen: "Exit full screen", fit: "Fit map", left: "public / resource planning", center: "hybrid coordination", right: "market / private autonomy", top: "participatory / direct democracy", bottom: "expert / technocratic control", xAxis: "Economic coordination", yAxis: "Political agency" },
    ru: { proposal: "Что предлагают", caveat: "Критическая оговорка", region: "Регион", status: "Статус", open: "Открытый код", yes: "да", no: "нет", links: "Mind Journal и оригинальные материалы", article: "Статья Mind Journal", shown: "позиций показано", empty: "По этим фильтрам ничего не найдено.", fullscreen: "На весь экран", exitFullscreen: "Выйти из полноэкранного режима", fit: "Вписать карту", left: "общественное / ресурсное планирование", center: "смешанная координация", right: "рынок / частная автономия", top: "участие / прямая демократия", bottom: "экспертное / технократическое управление", xAxis: "Экономическая координация", yAxis: "Политическое участие" },
    uk: { proposal: "Що пропонують", caveat: "Критичне застереження", region: "Регіон", status: "Статус", open: "Відкритий код", yes: "так", no: "ні", links: "Mind Journal та оригінальні матеріали", article: "Стаття Mind Journal", shown: "позицій показано", empty: "За цими фільтрами нічого не знайдено.", fullscreen: "На весь екран", exitFullscreen: "Вийти з повноекранного режиму", fit: "Вписати мапу", left: "суспільне / ресурсне планування", center: "змішана координація", right: "ринок / приватна автономія", top: "участь / пряма демократія", bottom: "експертне / технократичне управління", xAxis: "Економічна координація", yAxis: "Політична участь" }
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
    const canvas = root.querySelector(".future-map__canvas");
    const fullscreenButton = root.querySelector("[data-map-fullscreen]");
    const fitButton = root.querySelector("[data-map-fit]");
    const filterButtons = [...root.querySelectorAll("[data-map-filter]")];
    const themeButtons = [...root.querySelectorAll("[data-map-theme]")];
    let role = "all";
    let theme = "all";

    function setActive(buttons, activeButton) {
      buttons.forEach((button) => {
        const active = button === activeButton;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-pressed", String(active));
      });
    }

    function updateFullscreenButton() {
      if (!fullscreenButton) return;
      const active = document.fullscreenElement === root || root.classList.contains("is-expanded");
      fullscreenButton.textContent = active ? copy.exitFullscreen : copy.fullscreen;
      fullscreenButton.setAttribute("aria-pressed", String(active));
    }

    async function toggleFullscreen() {
      try {
        if (document.fullscreenElement === root) {
          await document.exitFullscreen();
        } else if (root.requestFullscreen) {
          await root.requestFullscreen();
        } else {
          root.classList.toggle("is-expanded");
        }
      } catch (_) {
        root.classList.toggle("is-expanded");
      }
      updateFullscreenButton();
    }

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
      const local = element("a", "future-map__article-link", `${copy.article}: ${localized(node.name, language)}`);
      local.href = `${window.location.pathname}${window.location.search}#${root.id}-entry-${node.id}`;
      links.appendChild(local);
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
      const descriptionText = svg.querySelector("desc") && svg.querySelector("desc").textContent;
      svg.replaceChildren();
      const title = document.createElementNS(ns, "title");
      title.textContent = root.getAttribute("aria-label") || "Map";
      svg.appendChild(title);
      if (descriptionText) {
        const description = document.createElementNS(ns, "desc");
        description.textContent = descriptionText; svg.appendChild(description);
      }
      if (!visibleNodes.length) {
        const label = document.createElementNS(ns, "text");
        label.setAttribute("x", "500"); label.setAttribute("y", "90"); label.setAttribute("text-anchor", "middle");
        label.textContent = copy.empty; svg.appendChild(label); svg.setAttribute("viewBox", "0 0 1000 180"); return;
      }
      const width = 1000, height = 700;
      const frame = { left: 112, right: 60, top: 62, bottom: 92 };
      const plotWidth = width - frame.left - frame.right;
      const plotHeight = height - frame.top - frame.bottom;
      const xScale = (value) => frame.left + ((Number(value) + 100) / 200) * plotWidth;
      const yScale = (value) => frame.top + ((100 - Number(value)) / 200) * plotHeight;
      const positions = new Map();
      svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

      [
        { x: frame.left, width: plotWidth / 3, className: "future-map__zone future-map__zone--left" },
        { x: frame.left + plotWidth / 3, width: plotWidth / 3, className: "future-map__zone future-map__zone--center" },
        { x: frame.left + plotWidth * 2 / 3, width: plotWidth / 3, className: "future-map__zone future-map__zone--right" }
      ].forEach((zone) => {
        const rect = document.createElementNS(ns, "rect");
        rect.setAttribute("x", zone.x); rect.setAttribute("y", frame.top);
        rect.setAttribute("width", zone.width); rect.setAttribute("height", plotHeight);
        rect.setAttribute("class", zone.className); svg.appendChild(rect);
      });

      const axisX = document.createElementNS(ns, "line");
      axisX.setAttribute("x1", frame.left); axisX.setAttribute("x2", width - frame.right);
      axisX.setAttribute("y1", yScale(0)); axisX.setAttribute("y2", yScale(0));
      axisX.setAttribute("class", "future-map__axis"); svg.appendChild(axisX);
      const axisY = document.createElementNS(ns, "line");
      axisY.setAttribute("x1", xScale(0)); axisY.setAttribute("x2", xScale(0));
      axisY.setAttribute("y1", frame.top); axisY.setAttribute("y2", height - frame.bottom);
      axisY.setAttribute("class", "future-map__axis"); svg.appendChild(axisY);

      function axisLabel(text, x, y, anchor, className) {
        const label = document.createElementNS(ns, "text");
        label.textContent = text; label.setAttribute("x", x); label.setAttribute("y", y);
        label.setAttribute("text-anchor", anchor || "middle");
        label.setAttribute("class", className || "future-map__axis-label");
        svg.appendChild(label); return label;
      }
      axisLabel(copy.left, frame.left, height - 58, "start");
      axisLabel(copy.center, xScale(0), height - 58, "middle");
      axisLabel(copy.right, width - frame.right, height - 58, "end");
      axisLabel(copy.xAxis, xScale(0), height - 22, "middle", "future-map__axis-title");
      axisLabel(copy.top, frame.left + 10, frame.top + 20, "start");
      axisLabel(copy.bottom, frame.left + 10, height - frame.bottom - 10, "start");
      const yTitle = axisLabel(copy.yAxis, 24, frame.top + plotHeight / 2, "middle", "future-map__axis-title");
      yTitle.setAttribute("transform", `rotate(-90 24 ${frame.top + plotHeight / 2})`);

      visibleNodes.forEach((node) => positions.set(node.id, {
        x: xScale(node.position && node.position.x),
        y: yScale(node.position && node.position.y)
      }));
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
        const hit = document.createElementNS(ns, "circle");
        hit.setAttribute("cx", position.x); hit.setAttribute("cy", position.y); hit.setAttribute("r", "18");
        hit.setAttribute("class", "future-map__hit");
        const point = document.createElementNS(ns, "circle");
        point.setAttribute("class", "future-map__point");
        point.setAttribute("cx", position.x); point.setAttribute("cy", position.y); point.setAttribute("r", "9");
        const label = document.createElementNS(ns, "text");
        const defaultRight = position.x < width - frame.right - 145;
        const offsetX = node.label_offset ? Number(node.label_offset.x) : (defaultRight ? 13 : -13);
        const offsetY = node.label_offset ? Number(node.label_offset.y) : 4;
        label.setAttribute("x", position.x + offsetX); label.setAttribute("y", position.y + offsetY);
        label.setAttribute("text-anchor", offsetX >= 0 ? "start" : "end");
        const name = localized(node.name, language);
        label.textContent = name.length > 24 ? `${name.slice(0, 22)}…` : name;
        group.append(hit, point, label); svg.appendChild(group);
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

    filterButtons.forEach((button) => button.addEventListener("click", () => {
      role = button.dataset.mapFilter;
      setActive(filterButtons, button); update();
    }));
    themeButtons.forEach((button) => button.addEventListener("click", () => {
      theme = button.dataset.mapTheme;
      setActive(themeButtons, button); update();
    }));
    root.querySelectorAll("[data-map-inspect]").forEach((button) => button.addEventListener("click", () => {
      const node = nodes.get(button.dataset.mapInspect); if (node) { showDetails(node); details.scrollIntoView({ behavior: "smooth", block: "nearest" }); }
    }));
    if (search) search.addEventListener("input", update);
    if (fullscreenButton) fullscreenButton.addEventListener("click", toggleFullscreen);
    if (fitButton) fitButton.addEventListener("click", () => {
      update();
      if (canvas) canvas.scrollTo({ left: 0, top: 0, behavior: "smooth" });
      if (canvas) canvas.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
    document.addEventListener("fullscreenchange", updateFullscreenButton);
    updateFullscreenButton();
    update();
  }

  document.querySelectorAll(".future-map").forEach(init);
}());
