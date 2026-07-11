#!/usr/bin/env python3
"""Generate index.html — the KWSL Market Update Vault.

Scans this repo for every native monthly report (report-<month>-<year>.html) and
merges in the older editions still hosted on Heyzine, sorts newest-first, and
renders an archive that embeds each report (cover preview + click-to-open).

Auto-updating: drop a new month's report file in the repo and it appears here.
Part of the monthly build, like the consumer edition.
"""
import glob, os, re

REPO = os.path.dirname(os.path.abspath(__file__))
MONTHS = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
          'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}
MNAME = {v: k.capitalize() for k, v in MONTHS.items()}

# Older editions that predate this repo — still live as Heyzine flipbooks on
# mykwsl.hflip.co. Kept here so the Vault shows the full history. If Heyzine is
# retired, rebuild these months natively and delete their entries.
# (year, month, flipbook url, cover-thumbnail url [Heyzine og:image])
LEGACY = [
    (2026, 2, 'https://mykwsl.hflip.co/kwslfeb2026', 'https://cdn.heyzine.com/files/uploaded/b7dcc1a5ad29f29e312fb7d3d80c4901949214dd-5.pdf-thumb.jpg'),
    (2026, 1, 'https://mykwsl.hflip.co/kwsljan2026', 'https://cdn.heyzine.com/files/uploaded/v3/7ae725842a2f92c963fb223da49454e1503f24f6-1.pdf-thumb.jpg'),
    (2025, 12, 'https://mykwsl.hflip.co/kwsldec2025', 'https://cdn.heyzine.com/files/uploaded/v3/aec1e60523bf6a8e41b359f2d327bcbb84551f09-3.pdf-thumb.jpg'),
    (2025, 11, 'https://mykwsl.hflip.co/kwslnov2025', 'https://cdn.heyzine.com/files/uploaded/208caa4fe3188a3c04c1eea1be444d90ac29d363-2.pdf-thumb.jpg'),
    (2025, 10, 'https://mykwsl.hflip.co/kwsloct2025', 'https://cdn.heyzine.com/files/uploaded/v3/d16c9ceeeaea0604d82b5640880b34defd462abd-3.pdf-thumb.jpg'),
    (2025, 9, 'https://mykwsl.hflip.co/kwslsept2025', 'https://cdn.heyzine.com/files/uploaded/v3/9eabe732497e9e96c41194e3268a5e124195f777-2.pdf-thumb.jpg'),
    (2025, 8, 'https://mykwsl.hflip.co/kwslaug2025', 'https://cdn.heyzine.com/files/uploaded/v3/b2b3cebece4770d15866f5a7c87687925b07451c-2.pdf-thumb.jpg'),
]

PV_SCALE = 0.402
NEW_DESIGN_FROM = (2026, 7)  # iron-ore redesign boundary (nav-crop differs by era)

def crop_px(year, month):
    nav = 162 if (year, month) >= NEW_DESIGN_FROM else 257
    return round(nav * PV_SCALE)

def discover():
    """Return {(year,month): {'agent':file,'consumer':file}} for native repo reports."""
    found = {}
    for f in glob.glob(os.path.join(REPO, 'report-*-*.html')):
        b = os.path.basename(f)
        m = re.match(r'report-([a-z]+)-(\d{4})(-consumer)?\.html$', b)
        if not m:
            continue
        mon, yr, cons = m.group(1).lower(), int(m.group(2)), bool(m.group(3))
        if mon not in MONTHS:
            continue
        found.setdefault((yr, MONTHS[mon]), {})['consumer' if cons else 'agent'] = b
    mar = 'phoenix-market-report-march-2026-v5.html'
    if os.path.exists(os.path.join(REPO, mar)):
        found.setdefault((2026, 3), {}).setdefault('agent', mar)
    return found

def timeline():
    """Merged, newest-first list of records (native + heyzine)."""
    recs = []
    native = discover()
    legacy_keys = {(y, m) for (y, m, *_ ) in LEGACY}
    for (y, m), files in native.items():
        if (y, m) in legacy_keys:
            continue  # a native rebuild supersedes the Heyzine copy
        recs.append({'year': y, 'month': m, 'type': 'native', **files})
    for (y, m, url, thumb) in LEGACY:
        recs.append({'year': y, 'month': m, 'type': 'heyzine', 'url': url, 'thumb': thumb})
    recs.sort(key=lambda r: (r['year'], r['month']), reverse=True)
    return recs

def native_card(r):
    title = f"{MNAME[r['month']]} {r['year']}"
    agent = r.get('agent')
    consumer = r.get('consumer')
    consumer_btn = (f'<a class="btn ghost" href="{consumer}" target="_blank" rel="noopener">Consumer&nbsp;edition</a>'
                    if consumer else '')
    return f'''      <article class="card" data-q="{title.lower()} {MNAME[r['month']].lower()} {r['year']}">
        <button class="pv" onclick="openReport('{agent}','{title}')" aria-label="Open {title} report">
          <iframe loading="lazy" src="{agent}" title="{title} preview" scrolling="no" tabindex="-1" style="top:-{crop_px(r['year'], r['month'])}px"></iframe>
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

def heyzine_card(r):
    title = f"{MNAME[r['month']]} {r['year']}"
    url = r['url']
    return f'''      <article class="card" data-q="{title.lower()} {MNAME[r['month']].lower()} {r['year']}">
        <button class="pv pv-flip" onclick="openReport('{url}','{title}')" aria-label="Open {title} magazine">
          <img class="pv-img" loading="lazy" src="{r['thumb']}" alt="{title} cover">
          <span class="pv-badge">Heyzine archive</span>
          <span class="pv-open">View magazine</span>
        </button>
        <div class="meta">
          <h2>{title}</h2>
          <p>Greater Phoenix Market Report</p>
          <div class="actions">
            <button class="btn" onclick="openReport('{url}','{title}')">View magazine ↗</button>
          </div>
        </div>
      </article>'''

def build():
    recs = timeline()
    cards = '\n'.join(native_card(r) if r['type'] == 'native' else heyzine_card(r) for r in recs)
    html = TEMPLATE.replace('{{CARDS}}', cards)
    open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(html)
    print(f"Wrote index.html — {len(recs)} reports "
          f"({sum(r['type']=='native' for r in recs)} native, {sum(r['type']=='heyzine' for r in recs)} heyzine): "
          + ', '.join(f"{MNAME[r['month']]} {r['year']}" for r in recs))

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
    --overlay:.86;
    --display:'Archivo',sans-serif; --body:'Inter',sans-serif; --mono:'IBM Plex Mono',monospace;
  }
  /* Light / day theme — shares the kwsl-theme preference with the reports. Amber stays amber. */
  html[data-theme="light"]{
    --dark:#f5f2ec; --panel:#efeae1; --elevated:#e6e1d7; --hair:#d8d2c6; --surround:#e9e4db;
    --ink:#242119; --ink-2:#565349; --ink-3:#847f75; --amber:#F5A623;
    --overlay:.80;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:var(--surround);color:var(--ink);font-family:var(--body);
       background-image:linear-gradient(var(--hair) 1px,transparent 1px),linear-gradient(90deg,var(--hair) 1px,transparent 1px);
       background-size:44px 44px;background-position:center;}
  body::before{content:"";position:fixed;inset:0;background:var(--surround);opacity:var(--overlay);pointer-events:none;z-index:-1;}
  a{color:inherit;text-decoration:none;}
  .wrap{max-width:1120px;margin:0 auto;padding:0 24px 80px;}

  header{padding:64px 0 40px;text-align:center;position:relative;}
  .toplink{position:absolute;top:28px;font-family:var(--mono);font-size:11px;letter-spacing:.1em;
          text-transform:uppercase;color:var(--ink-2);border:1px solid var(--hair);padding:9px 15px;transition:.2s;cursor:pointer;background:none;}
  .toplink:hover{border-color:var(--amber);color:var(--amber);}
  .portal{right:0;} .theme-tog{left:0;}
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3);
           display:inline-flex;align-items:center;gap:11px;margin-bottom:18px;}
  .eyebrow::before,.eyebrow::after{content:"";width:18px;height:3px;background:var(--amber);}
  h1{font-family:var(--display);font-weight:800;font-size:clamp(34px,6vw,58px);letter-spacing:.01em;margin:0 0 10px;}
  header p{color:var(--ink-2);font-size:15px;margin:0 auto 28px;max-width:540px;}
  .search{width:100%;max-width:480px;margin:0 auto;display:block;background:var(--panel);border:1px solid var(--hair);
          color:var(--ink);font-size:14px;font-family:var(--body);padding:14px 18px;border-radius:2px;}
  .search:focus{outline:none;border-color:var(--amber);}
  .search::placeholder{color:var(--ink-3);}

  .grid{display:grid;grid-template-columns:repeat(auto-fill,330px);justify-content:center;gap:28px;}
  .card{background:var(--panel);border:1px solid var(--hair);border-radius:3px;overflow:hidden;
        display:flex;flex-direction:column;transition:border-color .2s,transform .2s;}
  .card:hover{border-color:#57545c;transform:translateY(-2px);}
  /* Native preview = the report's own cover: iframe at 816px (mobile layout), nav cropped, scaled to width. */
  .pv{position:relative;width:100%;height:424px;overflow:hidden;background:var(--dark);border:0;border-bottom:1px solid var(--hair);
      cursor:pointer;display:block;padding:0;}
  .pv iframe{position:absolute;left:0;width:816px;height:1400px;border:0;pointer-events:none;
             transform:scale(.402);transform-origin:top left;}  /* top set per-card inline (nav crop) */
  /* Heyzine preview = the flipbook's cover thumbnail (og:image), filling the frame. */
  .pv-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top;}
  .pv-badge{position:absolute;top:12px;left:12px;font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;
            color:var(--ink);background:var(--amber);padding:4px 8px;border-radius:2px;font-weight:600;z-index:2;}
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

  /* fullscreen report/flipbook modal */
  #modal{position:fixed;inset:0;background:var(--surround);z-index:100;display:none;flex-direction:column;}
  #modal.open{display:flex;}
  .modal-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 18px;
             background:var(--elevated);border-bottom:1px solid var(--hair);flex:0 0 auto;}
  .modal-title{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2);}
  .modal-x{background:none;border:1px solid var(--hair);color:var(--ink-2);font-size:16px;line-height:1;
           width:38px;height:38px;border-radius:50%;cursor:pointer;transition:.2s;}
  .modal-x:hover{border-color:var(--amber);color:var(--amber);}
  #modal iframe{flex:1 1 auto;width:100%;border:0;background:var(--surround);}
  @media(max-width:560px){ header{padding:64px 0 30px;} .toplink{top:16px;} }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <button class="toplink theme-tog" id="themeTog" onclick="toggleTheme()" title="Switch light / dark">&#9788; Light</button>
      <a class="toplink portal" href="http://portal.mykwsl.com/" target="_blank" rel="noopener">Agent Portal ↗</a>
      <div class="eyebrow">Keller Williams Realty &middot; Sonoran Living</div>
      <h1>Market Update Vault</h1>
      <p>A running archive of every Greater Phoenix market report we&rsquo;ve published — newest first. Search a month or year, tap any cover to open it.</p>
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
  // Theme — shares localStorage['kwsl-theme'] with the reports so the whole site stays in sync.
  function isLight(){ return document.documentElement.getAttribute('data-theme') === 'light'; }
  function applyTheme(mode){
    var light = (mode === 'light');
    document.documentElement.setAttribute('data-theme', light ? 'light' : 'dark');
    var b = document.getElementById('themeTog');
    if(b) b.innerHTML = light ? '&#9790; Dark' : '&#9788; Light';
    try{ localStorage.setItem('kwsl-theme', light ? 'light' : 'dark'); }catch(e){}
  }
  function toggleTheme(){ applyTheme(isLight() ? 'dark' : 'light'); }
  (function(){ var s='dark'; try{ s=localStorage.getItem('kwsl-theme')||'dark'; }catch(e){} applyTheme(s); })();

  function openReport(url, title){
    document.getElementById('modalTitle').textContent = title || 'Market Report';
    document.getElementById('modalFrame').src = url;
    document.getElementById('modal').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeReport(){
    document.getElementById('modal').classList.remove('open');
    document.getElementById('modalFrame').src = 'about:blank';
    document.body.style.overflow = '';
  }
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeReport(); });

  document.getElementById('search').addEventListener('input', function(){
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
