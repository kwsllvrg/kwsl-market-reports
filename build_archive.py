#!/usr/bin/env python3
"""Generate index.html — the KWSL Market Update Vault.

Scans this repo for every monthly report (report-<month>-<year>.html, plus the
legacy March file), sorts newest-first, and renders an archive page that embeds
each report by iframe (cover preview + click-to-open, interactive flipbook).

Auto-updating: run it whenever a new month's report lands and it picks it up.
Part of the monthly build, like the consumer edition.
"""
import glob, os, re

REPO = os.path.dirname(os.path.abspath(__file__))
MONTHS = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
          'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}
MNAME = {v: k.capitalize() for k, v in MONTHS.items()}

def discover():
    found = {}  # (year, month) -> {'agent':file, 'consumer':file}
    for f in glob.glob(os.path.join(REPO, 'report-*-*.html')):
        b = os.path.basename(f)
        m = re.match(r'report-([a-z]+)-(\d{4})(-consumer)?\.html$', b)
        if not m:
            continue
        mon, yr, cons = m.group(1).lower(), int(m.group(2)), bool(m.group(3))
        if mon not in MONTHS:
            continue
        key = (yr, MONTHS[mon])
        found.setdefault(key, {})['consumer' if cons else 'agent'] = b
    # legacy March file
    mar = 'phoenix-market-report-march-2026-v5.html'
    if os.path.exists(os.path.join(REPO, mar)):
        found.setdefault((2026, 3), {}).setdefault('agent', mar)
    return dict(sorted(found.items(), reverse=True))  # newest first

# The preview iframe renders each report at 816px (its mobile layout) and we crop the
# nav chrome off the top so only the cover shows. The nav height differs by design era:
# the iron-ore redesign (July 2026 onward) has a 162px nav; the older serif reports
# (through June 2026) carry a full thumb-strip and run 257px. Crop = navPx * preview scale.
PV_SCALE = 0.402
NEW_DESIGN_FROM = (2026, 7)  # iron-ore redesign boundary

def crop_px(year, month):
    nav = 162 if (year, month) >= NEW_DESIGN_FROM else 257
    return round(nav * PV_SCALE)

def card(year, month, files):
    title = f'{MNAME[month]} {year}'
    agent = files.get('agent')
    consumer = files.get('consumer')
    consumer_btn = (f'<a class="btn ghost" href="{consumer}" target="_blank" rel="noopener">Consumer&nbsp;edition</a>'
                    if consumer else '')
    return f'''      <article class="card" data-q="{title.lower()} {MNAME[month].lower()} {year}">
        <button class="pv" onclick="openReport('{agent}','{title}')" aria-label="Open {title} report">
          <iframe loading="lazy" src="{agent}" title="{title} preview" scrolling="no" tabindex="-1" style="top:-{crop_px(year, month)}px"></iframe>
          <span class="pv-open">Open&nbsp;report</span>
        </button>
        <div class="meta">
          <h2>{title}</h2>
          <p>Greater Phoenix Market Report</p>
          <div class="actions">
            <button class="btn" onclick="openReport('{agent}','{title}')">Open ↗</button>
            {consumer_btn}
          </div>
        </div>
      </article>'''

def build():
    reports = discover()
    cards = '\n'.join(card(y, m, f) for (y, m), f in reports.items())
    html = TEMPLATE.replace('{{CARDS}}', cards).replace('{{COUNT}}', str(len(reports)))
    out = os.path.join(REPO, 'index.html')
    open(out, 'w', encoding='utf-8').write(html)
    print(f'Wrote {out} — {len(reports)} reports: '
          + ', '.join(f'{MNAME[m]} {y}' for (y, m) in reports))

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>KWSL Market Update Vault</title>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
  :root{
    --dark:#1d1d1e; --panel:#252527; --elevated:#2c2c2e; --hair:#3a3a3e; --surround:#050505;
    --ink:#e6e2da; --ink-2:#ada99f; --ink-3:#8f8b82; --amber:#F5A623;
    --display:'Archivo',sans-serif; --body:'Inter',sans-serif; --mono:'IBM Plex Mono',monospace;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--surround);color:var(--ink);font-family:var(--body);
       background-image:linear-gradient(var(--hair) 1px,transparent 1px),linear-gradient(90deg,var(--hair) 1px,transparent 1px);
       background-size:44px 44px;background-position:center;}
  body::before{content:"";position:fixed;inset:0;background:var(--surround);opacity:.86;pointer-events:none;z-index:-1;}
  a{color:inherit;text-decoration:none;}
  .wrap{max-width:1120px;margin:0 auto;padding:0 24px 80px;}

  header{padding:64px 0 40px;text-align:center;position:relative;}
  .portal{position:absolute;top:28px;right:0;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
          text-transform:uppercase;color:var(--ink-2);border:1px solid var(--hair);padding:9px 15px;transition:.2s;}
  .portal:hover{border-color:var(--amber);color:var(--amber);}
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);
           display:inline-flex;align-items:center;gap:11px;margin-bottom:18px;}
  .eyebrow::before,.eyebrow::after{content:"";width:18px;height:3px;background:var(--amber);}
  h1{font-family:var(--display);font-weight:800;font-size:clamp(34px,6vw,58px);letter-spacing:.01em;margin:0 0 10px;}
  header p{color:var(--ink-2);font-size:15px;margin:0 auto 28px;max-width:520px;}
  .search{width:100%;max-width:480px;margin:0 auto;display:block;background:var(--panel);border:1px solid var(--hair);
          color:var(--ink);font-size:14px;font-family:var(--body);padding:14px 18px;border-radius:2px;}
  .search:focus{outline:none;border-color:var(--amber);}
  .search::placeholder{color:var(--ink-3);}

  .grid{display:grid;grid-template-columns:repeat(auto-fill,330px);justify-content:center;gap:28px;}
  .card{background:var(--panel);border:1px solid var(--hair);border-radius:3px;overflow:hidden;
        display:flex;flex-direction:column;transition:border-color .2s,transform .2s;}
  .card:hover{border-color:#57545c;transform:translateY(-2px);}
  /* Preview = the report's live cover: iframe at 816px renders mobile layout; we crop the
     162px nav chrome off the top and scale the full 1056px cover to fill the card width. */
  .pv{position:relative;width:100%;height:424px;overflow:hidden;background:var(--dark);border:0;border-bottom:1px solid var(--hair);
      cursor:pointer;display:block;padding:0;}
  .pv iframe{position:absolute;left:0;width:816px;height:1400px;border:0;pointer-events:none;
             transform:scale(.402);transform-origin:top left;}  /* top set per-card inline (nav crop) */
  .pv-open{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
           font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#fff;
           background:rgba(10,10,11,.55);opacity:0;transition:.2s;}
  .pv:hover .pv-open{opacity:1;}
  .meta{padding:18px 20px 20px;}
  .meta h2{font-family:var(--display);font-weight:700;font-size:21px;margin:0 0 3px;}
  .meta p{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:0 0 15px;}
  .actions{display:flex;gap:9px;flex-wrap:wrap;}
  .btn{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;
       background:var(--amber);color:#1a1206;border:0;padding:9px 15px;border-radius:2px;font-weight:600;transition:.2s;}
  .btn:hover{filter:brightness(1.08);}
  .btn.ghost{background:transparent;color:var(--ink-2);border:1px solid var(--hair);}
  .btn.ghost:hover{border-color:var(--ink-2);color:var(--ink);}
  .empty{grid-column:1/-1;text-align:center;color:var(--ink-3);padding:60px 0;font-family:var(--mono);}

  footer{text-align:center;color:var(--ink-3);font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;
         text-transform:uppercase;padding:44px 0 0;}

  /* fullscreen report modal (the "iframe experience") */
  #modal{position:fixed;inset:0;background:var(--surround);z-index:100;display:none;flex-direction:column;}
  #modal.open{display:flex;}
  .modal-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;
             background:#0e0e0f;border-bottom:1px solid var(--hair);flex:0 0 auto;}
  .modal-title{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);}
  .modal-x{background:none;border:1px solid var(--hair);color:var(--ink-2);font-size:16px;line-height:1;
           width:38px;height:38px;border-radius:50%;cursor:pointer;transition:.2s;}
  .modal-x:hover{border-color:var(--amber);color:var(--amber);}
  #modal iframe{flex:1 1 auto;width:100%;border:0;background:var(--surround);}
  @media(max-width:560px){ header{padding:52px 0 30px;} .portal{position:static;display:inline-block;margin-bottom:20px;} }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <a class="portal" href="http://portal.mykwsl.com/" target="_blank" rel="noopener">Agent Portal ↗</a>
      <div class="eyebrow">Keller Williams Realty &middot; Sonoran Living</div>
      <h1>Market Update Vault</h1>
      <p>Every Greater Phoenix market report we&rsquo;ve published — {{COUNT}} and counting. Search a month or year, click any cover to read it.</p>
      <input class="search" id="search" type="search" placeholder="Search updates (e.g. &lsquo;July&rsquo; or &lsquo;2026&rsquo;)…" autocomplete="off">
    </header>
    <main class="grid" id="grid">
{{CARDS}}
      <div class="empty" id="empty" style="display:none;">No updates match that search.</div>
    </main>
    <footer>KW Sonoran Living &middot; Greater Phoenix Market Reports</footer>
  </div>

  <div id="modal" role="dialog" aria-modal="true">
    <div class="modal-bar">
      <span class="modal-title" id="modalTitle">Market Report</span>
      <button class="modal-x" onclick="closeReport()" aria-label="Close">✕</button>
    </div>
    <iframe id="modalFrame" title="Market report"></iframe>
  </div>

<script>
  function openReport(url, title){
    document.getElementById('modalTitle').textContent = title || 'Market Report';
    var f = document.getElementById('modalFrame'); f.src = url;
    document.getElementById('modal').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeReport(){
    document.getElementById('modal').classList.remove('open');
    document.getElementById('modalFrame').src = 'about:blank';
    document.body.style.overflow = '';
  }
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeReport(); });

  var search = document.getElementById('search');
  search.addEventListener('input', function(){
    var q = this.value.trim().toLowerCase(), any = false;
    document.querySelectorAll('.card').forEach(function(c){
      var hit = !q || c.dataset.q.indexOf(q) > -1;
      c.style.display = hit ? '' : 'none';
      if(hit) any = true;
    });
    document.getElementById('empty').style.display = any ? 'none' : '';
  });
</script>
</body>
</html>'''

if __name__ == '__main__':
    build()
