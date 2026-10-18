if (window.location.pathname.endsWith('/index.html')) {
  const url = new URL(window.location.href);
  url.pathname = url.pathname.slice(0, -'index.html'.length);
  window.history.replaceState(window.history.state, '', url.pathname + url.search + url.hash);
}
