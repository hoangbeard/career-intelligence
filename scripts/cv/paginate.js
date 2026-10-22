// Splits a rendered CV into fixed-size pages without cutting a block in half.
// Runs inside Chromium; scripts/export_cv.py loads it and calls
// CvPagination.render(options).
//
// Each child of the measure root (or of a .resume-section) is one block. A
// block that does not fit on the current page moves to the next one. Long
// plain paragraphs and lists can be split into smaller fragments (lines,
// list items) so a page is not left half empty. `\newpage` in the Markdown
// becomes a forced page break.
(() => {
  const outerHeight = (element) => {
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);
    return rect.height + (parseFloat(style.marginTop) || 0) + (parseFloat(style.marginBottom) || 0);
  };

  const escapeHtml = (value) =>
    value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const lineHeightOf = (element) => {
    const style = window.getComputedStyle(element);
    const lineHeight = parseFloat(style.lineHeight);
    return Number.isFinite(lineHeight) ? lineHeight : (parseFloat(style.fontSize) || 16) * 1.2;
  };

  const isPlainParagraph = (element) =>
    element instanceof HTMLParagraphElement &&
    Array.from(element.childNodes).every((node) => node.nodeType === Node.TEXT_NODE);

  const isList = (element) => element instanceof HTMLUListElement || element instanceof HTMLOListElement;

  const measureParagraphText = (paragraph, text, isLast) => {
    const clone = paragraph.cloneNode(false);
    clone.classList.add("resume-paragraph-fragment");
    clone.textContent = text;
    if (!isLast) clone.style.marginBottom = "0";
    paragraph.after(clone);
    const height = outerHeight(clone);
    clone.remove();
    return height;
  };

  const splitParagraph = (paragraph, blockHeight) => {
    const text = (paragraph.textContent || "").replace(/\s+/g, " ").trim();
    if (text.length < 80) return undefined;
    const lineHeight = lineHeightOf(paragraph);
    if (blockHeight < lineHeight * 1.8) return undefined;

    const chunks = [];
    let current = "";
    for (const word of text.split(/\s+/)) {
      const next = current ? `${current} ${word}` : word;
      if (current && measureParagraphText(paragraph, next, false) > lineHeight * 1.65) {
        chunks.push(current);
        current = word;
      } else {
        current = next;
      }
    }
    if (current) chunks.push(current);
    if (chunks.length < 2) return undefined;

    return chunks.map((chunk, index) => {
      const isLast = index === chunks.length - 1;
      const margin = isLast ? "" : ' style="margin-bottom:0"';
      return {
        html: `<p class="resume-paragraph-fragment"${margin}>${escapeHtml(chunk)}</p>`,
        height: measureParagraphText(paragraph, chunk, isLast),
      };
    });
  };

  const listFragment = (list, item, index, isLast) => {
    const fragment = list.cloneNode(false);
    const computed = window.getComputedStyle(list);
    fragment.classList.add("resume-list-fragment");
    fragment.style.marginLeft = computed.marginLeft;
    fragment.style.marginTop = index === 0 ? computed.marginTop : "0px";
    fragment.style.marginBottom = isLast ? computed.marginBottom : "0px";
    if (fragment instanceof HTMLOListElement) {
      const start = list.start > 0 ? list.start : 1;
      fragment.start = start + index;
    }
    fragment.append(item.cloneNode(true));
    return fragment;
  };

  const splitList = (list) => {
    const items = Array.from(list.children).filter((child) => child instanceof HTMLLIElement);
    if (items.length < 2) return undefined;
    return items.map((item, index) => {
      const isLast = index === items.length - 1;
      const fragment = listFragment(list, item, index, isLast);
      list.after(fragment);
      const height = outerHeight(fragment);
      fragment.remove();
      return { html: fragment.outerHTML, height };
    });
  };

  const measureBlocks = (container) =>
    Array.from(container.children)
      .flatMap((child) => (child.classList.contains("resume-section") ? Array.from(child.children) : [child]))
      .map((child) => {
        const height = outerHeight(child);
        return {
          html: child.outerHTML,
          height,
          pageBreak: child.dataset.pageBreak === "true",
          fragments: isPlainParagraph(child) ? splitParagraph(child, height) : isList(child) ? splitList(child) : undefined,
        };
      });

  const paginate = (blocks, maxHeight) => {
    const pages = [];
    let current = [];
    let currentHeight = 0;
    let overflow = false;

    const flush = () => {
      if (!current.length) return;
      pages.push({ blocks: current, overflow });
      current = [];
      currentHeight = 0;
      overflow = false;
    };
    const add = (block) => {
      if (current.length && currentHeight + block.height > maxHeight) flush();
      current.push(block);
      currentHeight += block.height;
      overflow = overflow || block.height > maxHeight;
    };

    for (const block of blocks) {
      if (block.pageBreak) {
        flush();
        continue;
      }
      if (block.fragments?.length && (block.height > maxHeight || currentHeight + block.height > maxHeight)) {
        block.fragments.forEach(add);
        continue;
      }
      add(block);
    }
    flush();
    return pages.length ? pages : [{ blocks: [], overflow: false }];
  };

  // Measures the CV, splits it into pages and replaces the measure root with
  // one .resume-page per page. Returns the page count and the 1-based numbers
  // of pages whose content does not fit (a single block taller than a page).
  const render = ({ maxContentHeight }) => {
    const measureRoot = document.querySelector(".resume-measure-root");
    const printRoot = document.querySelector(".resume-print-root");
    const pages = paginate(measureBlocks(measureRoot), maxContentHeight);
    for (const page of pages) {
      const article = measureRoot.cloneNode(false);
      article.classList.remove("resume-measure-root");
      article.style.height = article.style.minHeight;
      article.innerHTML = page.blocks.map((block) => block.html).join("");
      printRoot.append(article);
    }
    measureRoot.remove();
    return {
      pageCount: pages.length,
      overflowPages: pages.flatMap((page, index) => (page.overflow ? [index + 1] : [])),
    };
  };

  window.CvPagination = { measureBlocks, paginate, render };
})();
