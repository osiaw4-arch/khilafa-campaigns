"""
Deploy-ready Flask app for "Islamic History — Major Wars & Battles"

Run locally:
  pip install -r requirements.txt
  python islamic_history_app.py

Production (gunicorn):
  gunicorn -b 0.0.0.0:$PORT islamic_history_app:app
"""
import os
import unicodedata
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

BATTLES = [
    {"id":"badr","name":"Battle of Badr","era":"early","date":"624 CE (2 AH)","location":"Near Badr, Hejaz (Arabia)","belligerents":"Early Muslims of Medina vs Quraysh of Mecca","commanders":"Prophet Muhammad (PBUH) — Abu Sufyan","outcome":"Decisive Muslim victory","casualties":"Meccan ~70 killed; Muslim 14 killed (traditional sources vary)","summary":"The first large-scale pitched battle between the Muslims of Medina and the Quraysh of Mecca. A turning point that solidified Muhammad’s political and military position and boosted Muslim morale and recruitment."},
    {"id":"uhud","name":"Battle of Uhud","era":"early","date":"625 CE (3 AH)","location":"Mount Uhud, near Medina","belligerents":"Muslims of Medina vs Quraysh of Mecca","commanders":"Prophet Muhammad; Abu Sufyan, Khalid ibn al-Walid","outcome":"Tactical victory for Quraysh; strategic stalemate","casualties":"Muslim casualties higher; notable death: Hamza ibn Abdul-Muttalib","summary":"Quraysh sought revenge for Badr. Initial Muslim advantage was lost when archers left their positions; the battle exposed the importance of discipline and command cohesion."},
    {"id":"khandaq","name":"Battle of the Trench (Khandaq)","era":"early","date":"627 CE (5 AH)","location":"Medina","belligerents":"Muslims of Medina (defensive) vs coalition of Quraysh and allied tribes","commanders":"Prophet Muhammad; Quraysh coalition leaders","outcome":"Muslim defensive success; coalition withdrew","casualties":"Low direct casualties; significant strategic victory for Muslims","summary":"Also called the Siege of Medina—Muslims dug a trench to defend the city. The siege failed largely due to weather, logistical issues and internal dissension among the coalition, consolidating Muslim control in Medina."},
    {"id":"ridda","name":"Ridda Wars (Apostasy Wars)","era":"early","date":"632–633 CE","location":"Arabian Peninsula","belligerents":"Rashidun Caliphate (Abu Bakr) vs various tribes and breakaway polities","commanders":"Caliph Abu Bakr; local tribal leaders","outcome":"Rashidun victory and reunification of Arabia","casualties":"Varied by campaign","summary":"Series of campaigns to bring tribes back under central authority after Prophet Muhammad’s death—crucial for consolidation and the later expansion beyond Arabia."},
    {"id":"qadisiyyah","name":"Battle of al-Qadisiyyah","era":"conquests","date":"c. 636 CE","location":"Near the Euphrates, Iraq","belligerents":"Rashidun Caliphate vs Sassanian Empire","commanders":"Sa'd ibn Abi Waqqas vs Rostam Farrokhzad","outcome":"Decisive Muslim victory; opened Iraq to Muslim rule","casualties":"Heavy Sassanian losses; Muslims also significant casualties","summary":"Key battle in the Muslim conquest of Persia. Routed Sassanian field forces and led to collapse of centralized Sassanian control."},
    {"id":"yarmouk","name":"Battle of Yarmouk","era":"conquests","date":"636 CE","location":"Near the Yarmouk River (Syria/Jordan)","belligerents":"Rashidun Caliphate vs Byzantine Empire","commanders":"Khalid ibn al-Walid","outcome":"Decisive Muslim victory; Byzantine loss of Syria","casualties":"Heavy Byzantine casualties; exact numbers uncertain","summary":"One of the most decisive battles that established Muslim control over Syria and the Levant, significantly weakening Byzantine influence."},
    {"id":"conquest_egypt","name":"Muslim Conquest of Egypt","era":"conquests","date":"639–642 CE","location":"Egypt","belligerents":"Rashidun forces vs Byzantine holdouts in Egypt","commanders":"Amr ibn al-As","outcome":"Egypt enters Muslim rule","casualties":"Progressive campaigns with sieges","summary":"A sequence of campaigns culminating in the capture of Alexandria and the incorporation of Egypt into the Rashidun/early Caliphates."},
    {"id":"tours","name":"Battle of Tours (Poitiers)","era":"medieval","date":"732 CE","location":"Near Poitiers, France","belligerents":"Umayyad/Islamic raiding forces vs Frankish forces","commanders":"Abdul Rahman Al-Ghafiqi vs Charles Martel","outcome":"Frankish victory; halted northward expansion into Western Europe","casualties":"Both sides suffered casualties; Umayyad commander killed","summary":"Often viewed as a strategic halt to large-scale Umayyad advance into Western Europe—its long-term impact debated by historians."},
    {"id":"crusades_first","name":"First Crusade & Battles (1096–1099)","era":"medieval","date":"1096–1099 CE","location":"Levant / Jerusalem region","belligerents":"European Crusaders vs Seljuk/other Muslim polities","commanders":"Crusader leaders vs local Muslim rulers","outcome":"Crusader capture of Jerusalem (1099) and establishment of Crusader states","casualties":"High civilian and military casualties","summary":"A major series of campaigns originating in Europe that led to long-lasting conflict between Crusader states and Muslim polities."},
    {"id":"ayn_jalut","name":"Battle of Ayn Jalut","era":"mongol","date":"1260 CE","location":"Ayn Jalut","belligerents":"Mamluk Sultanate vs Mongol Empire","commanders":"Qutuz and Baibars vs Kitbuqa","outcome":"Mamluk victory; first major defeat of Mongols in the region","casualties":"Significant Mongol losses","summary":"Stopped the Mongol advance into Egypt and North Africa and secured Mamluk prestige."},
    {"id":"baghdad1258","name":"Siege & Sack of Baghdad (1258)","era":"mongol","date":"1258 CE","location":"Baghdad (Iraq)","belligerents":"Mongol Empire vs Abbasid Caliphate","commanders":"Hulagu Khan vs Caliph Al-Musta'sim","outcome":"Mongol capture and sack of Baghdad; end of the Abbasid caliphate in Baghdad","casualties":"Massive civilian casualties; cultural and scholarly losses","summary":"A cultural and political catastrophe—destruction of libraries, centers of learning."},
    {"id":"kosovo1389","name":"Battle of Kosovo (1389)","era":"ottoman","date":"1389 CE","location":"Balkans","belligerents":"Ottoman Empire vs Serbian-led coalition","commanders":"Murad I vs Prince Lazar","outcome":"Ottoman strategic expansion into the Balkans","casualties":"Both sides heavy","summary":"Part of Ottoman expansion into Southeastern Europe."},
    {"id":"lepanto","name":"Battle of Lepanto","era":"ottoman","date":"1571 CE","location":"Gulf of Patras","belligerents":"Holy League vs Ottoman Empire","commanders":"Don Juan of Austria vs Ali Pasha","outcome":"Holy League naval victory; slowed Ottoman naval dominance","casualties":"Heavy losses on both sides","summary":"A major naval engagement marking the limits of Ottoman naval expansion."},
    {"id":"napoleon_egypt","name":"Napoleon's Campaign in Egypt (1798–1801)","era":"modern","date":"1798–1801","location":"Egypt","belligerents":"French Republic vs Ottomans/British/Mamluk remnants","commanders":"Napoleon Bonaparte","outcome":"French occupation ended; longer-term consequences","casualties":"Significant military engagements","summary":"A European expedition with scientific and political consequences."},
    {"id":"ww1_me","name":"World War I — Ottoman Fronts & Arab Revolt","era":"modern","date":"1914–1918","location":"Arabia, Levant, Mesopotamia","belligerents":"Ottoman Empire vs Allied forces and Arab Revolt insurgents","commanders":"T.E. Lawrence and British generals","outcome":"Dissolution of Ottoman control in Arab lands","casualties":"Hundreds of thousands","summary":"End of the Ottoman political order in the Middle East."},
    {"id":"arab_israeli1948","name":"1948 Arab–Israeli War","era":"modern","date":"1947–1949","location":"Palestine / Israel","belligerents":"Israel vs coalition of Arab states","commanders":"Various","outcome":"Establishment of the State of Israel; armistice lines (1949)","casualties":"Tens of thousands","summary":"A foundational conflict for the modern Middle East."}
]

def normalize(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s)
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).lower()

def search_battles(q):
    qn = normalize(q)
    if not qn:
        return BATTLES
    out = []
    for b in BATTLES:
        hay = ' '.join([b.get('name',''), b.get('summary',''), b.get('location',''), b.get('belligerents',''), b.get('date',''), b.get('era','')])
        if qn in normalize(hay):
            out.append(b)
    return out

TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Islamic History — Major Wars & Battles</title>
  <style>
    body{font-family: Arial, Helvetica, sans-serif; background:#0b1220; color:#e6eef8; margin:0;}
    .wrap{max-width:1000px;margin:24px auto;padding:18px}
    header{display:flex;align-items:center;gap:12px}
    .logo{background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:10px;font-weight:700}
    .controls{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
    input[type=search]{flex:1;padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:inherit;min-width:260px}
    .filter{padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:#94a3b8;cursor:pointer}
    .grid{margin-top:18px}
    .battle{background:rgba(255,255,255,0.02);padding:12px;border-radius:10px;margin-bottom:10px}
    .meta{color:#94a3b8;font-size:13px;margin-bottom:8px}
    .tag{display:inline-block;padding:4px 8px;border-radius:6px;background:rgba(255,255,255,0.02);margin-right:6px;font-size:12px}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="logo">Islamic History</div>
      <div>
        <h1>Islamic History — Major Wars & Battles</h1>
        <div style="color:#94a3b8">Search and filter important battles across eras.</div>
      </div>
    </header>

    <div class="controls">
      <input id="q" type="search" placeholder="Search battles, years, places..." value="{{ q|e }}" />
      <button class="filter" onclick="doFilter('all')">All</button>
      <button class="filter" onclick="doFilter('early')">Early</button>
      <button class="filter" onclick="doFilter('conquests')">Conquests</button>
      <button class="filter" onclick="doFilter('medieval')">Medieval</button>
      <button class="filter" onclick="doFilter('mongol')">Mongol</button>
      <button class="filter" onclick="doFilter('ottoman')">Ottoman</button>
      <button class="filter" onclick="doFilter('modern')">Modern</button>
    </div>

    <div id="grid" class="grid">
      {% for b in results %}
      <article class="battle">
        <h2 id="{{ b.id }}">{{ b.name }}</h2>
        <div class="meta"><span class="tag">{{ b.date }}</span> <span class="tag">{{ b.location }}</span> <span class="tag">Era: {{ b.era }}</span></div>
        <div><strong>Belligerents:</strong> {{ b.belligerents }}</div>
        <div><strong>Commanders:</strong> {{ b.commanders }}</div>
        <div><strong>Outcome:</strong> {{ b.outcome }}</div>
        <div><strong>Casualties:</strong> {{ b.casualties }}</div>
        <div style="margin-top:8px">{{ b.summary }}</div>
      </article>
      {% else %}
      <div class="battle"><h3>No results</h3><div style="color:#94a3b8">Try a different keyword.</div></div>
      {% endfor %}
    </div>

  </div>

  <script>
    // client-side: live search hits /api/search
    const qEl = document.getElementById('q');
    let t;
    qEl.addEventListener('input', ()=>{ clearTimeout(t); t = setTimeout(()=>{
        fetch('/api/search?q=' + encodeURIComponent(qEl.value))
          .then(r=>r.json()).then(data=>render(data));
    }, 220); });

    function doFilter(era){
      fetch('/api/search?era=' + era + '&q=' + encodeURIComponent(qEl.value))
        .then(r=>r.json()).then(data=>render(data));
    }

    function render(data){
      const grid = document.getElementById('grid');
      grid.innerHTML = '';
      if(!data || data.length === 0){ grid.innerHTML = '<div class="battle"><h3>No results</h3><div style="color:#94a3b8">Try a different keyword.</div></div>'; return; }
      data.forEach(b=>{
        const art = document.createElement('article'); art.className='battle';
        art.innerHTML = `<h2 id="${b.id}">${b.name}</h2>`+
          `<div class="meta"><span class="tag">${b.date}</span> <span class="tag">${b.location}</span> <span class="tag">Era: ${b.era}</span></div>`+
          `<div><strong>Belligerents:</strong> ${b.belligerents}</div>`+
          `<div><strong>Commanders:</strong> ${b.commanders}</div>`+
          `<div><strong>Outcome:</strong> ${b.outcome}</div>`+
          `<div><strong>Casualties:</strong> ${b.casualties}</div>`+
          `<div style="margin-top:8px">${b.summary}</div>`;
        grid.appendChild(art);
      });
    }
  </script>
</body>
</html>
'''

@app.route('/')
def index():
    q = request.args.get('q', '')
    era = request.args.get('era', '')
    results = search_battles(q)
    if era and era != 'all':
        results = [b for b in results if b.get('era') == era]
    return render_template_string(TEMPLATE, results=results, q=q)

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    era = request.args.get('era', '')
    results = search_battles(q)
    if era and era != 'all':
        results = [b for b in results if b.get('era') == era]
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))  # 8000 works well on many hosts
    app.run(host='0.0.0.0', port=port)
