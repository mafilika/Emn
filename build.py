#!/usr/bin/env python3
"""EMN Projects site builder. Edit CONFIG and the SERVICES/TOWNS data, then run: python3 build.py
Output goes to ./public (what Netlify publishes)."""
import json, re, shutil, pathlib, datetime

# ---------- CONFIG: change these ----------
DOMAIN = "emnprojectsairconditioning.online"   # no https://
TEL    = "+27000000000"                        # e.g. +27821234567
WA     = "27000000000"                         # WhatsApp number, digits only
BRAND  = "EMN Projects Airconditioning"
# ------------------------------------------

SERVICES = [
 dict(slug="air-conditioning-installation", name="Air Conditioning Installation", short="aircon installation", icon="🏠",
  intro="Correct sizing, clean installation and a compliant electrical setup for split, multi-split and cassette air conditioners. We install all brands for homes, offices and shops.",
  points=["Load calculation and correct unit sizing","Wall-mounted, floor, cassette and multi-split systems","Neat pipework, drainage and cabling","Electrical certificate of compliance","Commissioning and handover"],
  faq=[("How much does aircon installation cost?","The price depends on the unit size, brand and installation distance. Send us your requirements and we give a transparent, itemised quote."),("Do you install all aircon brands?","Yes, we install all major brands and can advise which size and model suits your space.")]),
 dict(slug="air-conditioning-service-repairs", name="Air Conditioning Service & Repairs", short="aircon repairs and servicing", icon="🔧",
  intro="Routine servicing, fault finding, repairs and preventive maintenance to keep your air conditioners efficient and reliable. Refrigerant work is done by F-Gas certified technicians.",
  points=["Full service: filters, coils, drains and electrical checks","Gas leak detection, repair and re-gas","Fault diagnosis and component replacement","Maintenance contracts for businesses","Emergency breakdown response"],
  faq=[("How often should my aircon be serviced?","At least once a year, ideally before summer. Commercial and high-use units benefit from a service every 3 to 6 months."),("Why is my aircon not cooling?","Common causes are dirty filters, low refrigerant, a faulty fan or capacitor, or a blocked drain. A technician can diagnose it quickly.")]),
 dict(slug="cold-rooms", name="Cold Room Installation & Repairs", short="cold room installation and repairs", icon="🧊",
  intro="Design, supply, service and install cold rooms and freezer rooms with precise temperature control for restaurants, butcheries, retailers and food producers.",
  points=["Walk-in cold rooms and freezer rooms","Evaporator, condensing unit and controller repairs","Insulated panels, doors and floors","Temperature monitoring and alarms","Same-day commercial emergency response"],
  faq=[("Can you repair a cold room the same day?","We offer commercial emergency response across Gauteng, and many cold room faults are fixed the same day to protect your stock."),("Do you build new cold rooms?","Yes. We design, supply and install new cold rooms and freezer rooms sized for your business.")]),
 dict(slug="ducting-systems", name="Ducting Systems", short="HVAC ducting", icon="🌬️",
  intro="Efficient duct design and installation for balanced airflow and reduced noise in offices, shops, warehouses and restaurants.",
  points=["Duct design and airflow balancing","Insulated, sealed ducting for efficiency","Ventilation and extraction systems","Low-noise installations","Modifications to existing ducting"],
  faq=[("What is ducted air conditioning?","Ducted systems distribute cooled air from a central unit through ducts to several rooms or zones, giving even temperatures with hidden equipment."),("Can you fix noisy or unbalanced ducting?","Yes. We inspect, rebalance and modify ducting to improve airflow and cut noise.")]),
]
TOWNS = ["Roodepoort","Johannesburg","Randburg","Sandton","Krugersdorp","Soweto","Midrand","Pretoria"]
slug = lambda t: re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
URL = f"https://{DOMAIN}"
OUT = pathlib.Path("public")

def tok(t): return t.replace("{{TEL}}",TEL).replace("{{WA}}",WA).replace("{{DOMAIN}}",DOMAIN)

HEAD = """<!DOCTYPE html><html lang="en-ZA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:locale" content="en_ZA"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">
<meta name="theme-color" content="#0b5bd3"><link rel="stylesheet" href="/assets/style.css"><script type="application/ld+json">{ld}</script></head><body>
<header><div class="w nav"><a class="brand" href="/"><span class="logo">EMN</span><span>{brand}<small>Aircon, Cold Rooms &amp; Ducting · Gauteng</small></span></a>
<button class="menu" aria-label="Toggle menu" aria-expanded="false">☰</button><nav aria-label="Main"><ul><li><a href="/#services">Services</a></li><li><a href="/#areas">Areas</a></li><li><a href="/#faq">FAQ</a></li><li><a href="#quote">Free Quote</a></li></ul></nav></div></header><main>"""
FORM = """<section id="quote"><div class="w" style="max-width:640px"><h2>Get a Free Quote</h2><form id="qf" class="card">
<input id="n" required placeholder="Your name" autocomplete="name" aria-label="Your name"><input id="p" required placeholder="Phone or WhatsApp" type="tel" autocomplete="tel" aria-label="Phone or WhatsApp">
<select id="s" aria-label="Service">{opts}</select><textarea id="m" rows="4" placeholder="Message (optional)" aria-label="Message"></textarea>
<div class="cta" style="margin:0"><button class="btn" type="submit">Send Request</button><a class="btn o" href="tel:{tel}">Call Now</a></div></form></div></section>"""
FOOT = """</main><footer><div class="w"><strong>{brand}</strong> · Roodepoort, Gauteng, South Africa<br>© <span id="y"></span> {brand}. All rights reserved.</div></footer>
<div class="fab"><a href="tel:{tel}" aria-label="Call now">📞</a><a class="w2" href="https://wa.me/{wa}" rel="noopener" aria-label="WhatsApp">💬</a></div><script src="/assets/main.js" defer></script></body></html>"""

def faq_html(faq): return "".join(f"<details{' open' if i==0 else ''}><summary>{q}</summary><p>{a}</p></details>" for i,(q,a) in enumerate(faq))
def links(items): return '<div class="links">'+"".join(f'<a href="{h}">{t}</a>' for h,t in items)+"</div>"

def page(path, title, desc, h1, lead, body, faq, service=None, town=None, crumbs=()):
    url = f"{URL}{path}"
    biz = {"@type":["HVACBusiness","LocalBusiness"],"@id":f"{URL}/#business","name":BRAND,"url":URL+"/","telephone":TEL,"address":{"@type":"PostalAddress","addressLocality":"Roodepoort","addressRegion":"Gauteng","addressCountry":"ZA"}}
    graph = [biz,{"@type":"WebPage","name":title,"url":url,"description":desc,"isPartOf":{"@id":f"{URL}/#business"}},
      {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":URL+u} for i,(n,u) in enumerate(crumbs)]}]
    if service: graph.append({"@type":"Service","name":service+(f" in {town}" if town else ""),"serviceType":service,"provider":{"@id":f"{URL}/#business"},"areaServed":{"@type":"City","name":town or "Gauteng"}})
    graph.append({"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]})
    ld = json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False)
    crumb = " › ".join(f'<a href="{u}">{n}</a>' for n,u in crumbs[:-1]) + (" › "+crumbs[-1][0] if crumbs else "")
    opts = "".join(f"<option>{s['name']}</option>" for s in SERVICES)+"<option>Other</option>"
    html = (HEAD.format(title=title,desc=desc,url=url,ld=ld,brand=BRAND)
      + f'<div class="w crumb">{crumb}</div><section class="hero" style="padding-top:24px"><div class="w"><h1>{h1}</h1><p class="lead">{lead}</p>'
      + f'<div class="cta"><a class="btn" href="tel:{TEL}">📞 Call Now</a><a class="btn g" href="https://wa.me/{WA}">WhatsApp Us</a><a class="btn o" href="#quote">Free Quote</a></div>'
      + '<ul class="badges"><li>10+ Years Experience</li><li>F-Gas Certified</li><li>All Brands</li><li>Guaranteed Workmanship</li></ul></div></section>'
      + body + f'<section class="alt"><div class="w"><h2>Frequently Asked Questions</h2>{faq_html(faq)}</div></section>' + FORM.format(opts=opts,tel=TEL)
      + FOOT.format(brand=BRAND,tel=TEL,wa=WA))
    f = OUT/path.strip("/")/"index.html"; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(html,encoding="utf-8")

shutil.rmtree(OUT,ignore_errors=True); OUT.mkdir()
shutil.copytree("assets",OUT/"assets")
for p in (OUT/"assets").iterdir(): p.write_text(tok(p.read_text()),encoding="utf-8")
urls = ["/"]
home = [("Home","/")]
svc_links = [(f"/services/{s['slug']}/",s["name"]) for s in SERVICES]
twn_links = [(f"/areas/{slug(t)}/",t) for t in TOWNS]

# Service pages
for s in SERVICES:
    path=f"/services/{s['slug']}/"; urls.append(path)
    body=(f'<section><div class="w"><h2>What our {s["short"]} service includes</h2><ul class="card" style="padding-left:40px">'+"".join(f"<li>{x}</li>" for x in s["points"])+"</ul>"
      f'<h2 style="margin-top:28px">{s["name"]} across Gauteng</h2><p class="lead">We serve homes and businesses in your area.</p>'+links([(f"/areas/{slug(t)}/",t) for t in TOWNS])
      +'<h2 style="margin-top:28px">Our other services</h2>'+links([(h,n) for h,n in [(f"/services/{o["slug"]}/",o["name"]) for o in SERVICES if o is not s]])+"</div></section>")
    page(path,f"{s['name']} in Roodepoort & Gauteng | {BRAND}",f"{s['name']} by F-Gas certified technicians in Roodepoort, Johannesburg and across Gauteng. 10+ years experience, honest quotes. Call or WhatsApp today.",
      f"{s['name']} in Roodepoort &amp; Gauteng",s["intro"],body,s["faq"],service=s["name"],crumbs=home+[("Services","/#services"),(s["name"],path)])

# Town pages
for t in TOWNS:
    path=f"/areas/{slug(t)}/"; urls.append(path)
    cards="".join(f'<article class="card"><div class="ic">{s["icon"]}</div><h3>{s["name"]} in {t}</h3><p>{s["intro"].split(".")[0]}.</p><a class="btn" href="/services/{s["slug"]}/">View service</a></article>' for s in SERVICES)
    body=f'<section><div class="w"><h2>HVAC &amp; refrigeration services in {t}</h2><p class="lead">Call-outs, installations and maintenance for homes and businesses in {t}.</p><div class="grid">{cards}</div><h2 style="margin-top:28px">Other areas we serve</h2>'+links([(f"/areas/{slug(o)}/",o) for o in TOWNS if o!=t])+"</div></section>"
    faq=[(f"Do you offer aircon installation and repairs in {t}?",f"Yes. {BRAND} installs, services and repairs air conditioners in {t} and across Gauteng."),
         (f"Can you service cold rooms in {t}?",f"Yes. We design, install and repair cold rooms and offer commercial emergency response in {t}.")]
    page(path,f"Aircon, Cold Rooms & Ducting in {t} | {BRAND}",f"Aircon installation, servicing, cold rooms and ducting in {t}. F-Gas certified technicians, free quotes, same-day commercial response.",
      f"Aircon, Cold Rooms &amp; Ducting in {t}",f"F-Gas certified technicians serving {t}: air conditioning installation, servicing and repairs, cold rooms and ducting systems.",body,faq,service="HVAC & Refrigeration",town=t,crumbs=home+[("Areas","/#areas"),(t,path)])

# Homepage from template, with links into the new pages
idx = tok((pathlib.Path("templates/index.html")).read_text(encoding="utf-8"))
it = iter(SERVICES)
idx = re.sub(r'<button class="btn" data-more>Read More</button>',lambda m:(lambda s:m.group(0)+f'<a class="fl" href="/services/{s["slug"]}/">Full details →</a>')(next(it)),idx)
for t in TOWNS: idx = idx.replace(f"<span>{t}</span>",f'<span><a href="/areas/{slug(t)}/">{t}</a></span>')
(OUT/"index.html").write_text(idx,encoding="utf-8")

# 404, sitemap, robots, llms.txt
(OUT/"404.html").write_text(HEAD.format(title="Page not found | "+BRAND,desc="Page not found",url=URL+"/404.html",ld="{}",brand=BRAND)+'<section><div class="w"><h1>Page not found</h1><p><a class="btn" href="/">Back to home</a></p></div></section>'+FOOT.format(brand=BRAND,tel=TEL,wa=WA),encoding="utf-8")
today=datetime.date.today().isoformat()
(OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{URL}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)+"</urlset>\n")
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n")
(OUT/"llms.txt").write_text(f"# {BRAND}\n\n> F-Gas certified air conditioning, cold room and ducting contractor in Roodepoort, serving all of Gauteng, South Africa. 10+ years experience, all brands installed, free quotes.\n\n## Services\n"
  +"".join(f"- [{s['name']}]({URL}/services/{s['slug']}/): {s['intro']}\n" for s in SERVICES)+"\n## Areas served\n"+"".join(f"- [{t}]({URL}/areas/{slug(t)}/)\n" for t in TOWNS)+f"\n## Contact\n- Phone: {TEL}\n- WhatsApp: https://wa.me/{WA}\n- Website: {URL}/\n")
print("Built",len(urls),"pages into ./public")
