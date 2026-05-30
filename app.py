#!/usr/bin/env python3
"""
TemplateForge — Automated Template Factory + Marketplace
Generates CV, Notion, Landing Page & Slide templates.
Uploads to Gumroad automatically or sells directly via Stripe.
Port 5060
"""

import os, json, time, sqlite3, uuid, zipfile, io, shutil
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, make_response
from pathlib import Path

app = Flask(__name__)
BASE_DIR = os.path.dirname(__file__)
DB = os.path.join(BASE_DIR, "templates.db")
GEN_DIR = os.path.join(BASE_DIR, "generated")
STATIC_DIR = os.path.join(BASE_DIR, "static")

for d in [GEN_DIR]:
    for sub in ["cv", "notion", "landing", "slides"]:
        os.makedirs(os.path.join(d, sub), exist_ok=True)

# ── DB ────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT, category TEXT, subcategory TEXT,
            price REAL, description TEXT, tags TEXT,
            file_path TEXT, thumbnail TEXT,
            sales INTEGER DEFAULT 0, revenue REAL DEFAULT 0,
            gumroad_id TEXT, gumroad_url TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS design_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, colors TEXT, fonts TEXT,
            category TEXT, style TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── DESIGN SYSTEMS ────────────────────────────────────────
DESIGN_SYSTEMS = [
    {"name": "Minimal Light", "colors": ["#ffffff", "#1a1a2e", "#e94560", "#f0f0f0"], "fonts": "Inter, sans-serif", "style": "minimal"},
    {"name": "Dark Tech", "colors": ["#0a0a0f", "#7c3aed", "#10b981", "#1e1e2e"], "fonts": "JetBrains Mono, monospace", "style": "tech"},
    {"name": "Corporate Blue", "colors": ["#ffffff", "#1e3a5f", "#2563eb", "#f8fafc"], "fonts": "Poppins, sans-serif", "style": "corporate"},
    {"name": "Creative Warm", "colors": ["#fff8f0", "#d97706", "#dc2626", "#fef3c7"], "fonts": "Playfair Display, serif", "style": "creative"},
    {"name": "Glass Modern", "colors": ["#0f172a", "#38bdf8", "#818cf8", "#1e293b"], "fonts": "Space Grotesk, sans-serif", "style": "modern"},
    {"name": "Elegant Serif", "colors": ["#faf8f5", "#2d2d2d", "#b8860b", "#e8e0d5"], "fonts": "Cormorant Garamond, serif", "style": "elegant"},
    {"name": "Neon Dark", "colors": ["#000000", "#00ff88", "#ff00ff", "#1a1a1a"], "fonts": "Fira Code, monospace", "style": "neon"},
    {"name": "Pastel Soft", "colors": ["#fdf2f8", "#ec4899", "#8b5cf6", "#fce7f3"], "fonts": "Nunito, sans-serif", "style": "soft"},
]

# ── TEMPLATE GENERATOR ────────────────────────────────────
def generate_cv(design, name="Alex Durand", title="QA Engineer"):
    """Generate a CV HTML template"""
    ds = design
    c_bg, c_text, c_accent, c_secondary = ds["colors"]
    font = ds["fonts"]
    style_class = ds["style"]

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>CV {name}</title>
<style>
  * {{margin:0;padding:0;box-sizing:border-box;}}
  body {{background:{c_bg};color:{c_text};font-family:{font};max-width:800px;margin:40px auto;padding:20px;}}
  .header {{text-align:center;margin-bottom:30px;border-bottom:3px solid {c_accent};padding-bottom:20px;}}
  .header h1 {{font-size:28px;color:{c_accent};}}
  .header .title {{font-size:16px;color:{c_secondary};margin-top:4px;}}
  .header .contact {{font-size:12px;color:{c_secondary};margin-top:8px;}}
  .section {{margin:20px 0;}}
  .section h2 {{font-size:16px;color:{c_accent};border-left:4px solid {c_accent};padding-left:12px;margin-bottom:12px;}}
  .item {{margin-bottom:12px;}}
  .item-header {{display:flex;justify-content:space-between;font-weight:600;}}
  .item-sub {{font-size:13px;color:{c_secondary};}}
  .item-desc {{font-size:13px;margin-top:4px;line-height:1.5;}}
  .skills {{display:flex;flex-wrap:wrap;gap:8px;}}
  .skill {{padding:4px 12px;border-radius:20px;background:{c_secondary}20;font-size:12px;color:{c_text};}}
</style></head><body>
<div class="header">
  <h1>{name}</h1>
  <div class="title">{title}</div>
  <div class="contact">email@example.com · +33 6 00 00 00 00 · Paris, France · linkedin.com/in/janedoe</div>
</div>
<div class="section"><h2>Expérience</h2>
  <div class="item"><div class="item-header"><span>Senior QA Engineer</span><span>2022-Présent</span></div>
    <div class="item-sub">TechCorp · Paris</div>
    <div class="item-desc">Automatisation des tests E2E avec Playwright et Selenium. Réduction de 40% des bugs en production. Mise en place CI/CD avec GitHub Actions.</div>
  </div>
  <div class="item"><div class="item-header"><span>QA Engineer</span><span>2019-2022</span></div>
    <div class="item-sub">StartupXYZ · Lyon</div>
    <div class="item-desc">Tests manuels et automatisés. Création de plans de test. API testing avec Postman. Gestion des releases.</div>
  </div>
</div>
<div class="section"><h2>Compétences</h2>
  <div class="skills">
    <span class="skill">Playwright</span><span class="skill">Selenium</span><span class="skill">Cypress</span>
    <span class="skill">Python</span><span class="skill">JavaScript</span><span class="skill">CI/CD</span>
    <span class="skill">API Testing</span><span class="skill">Agile/Scrum</span><span class="skill">ISTQB</span>
  </div>
</div>
<div class="section"><h2>Formation</h2>
  <div class="item"><div class="item-header"><span>Master Informatique</span><span>2017-2019</span></div>
    <div class="item-sub">Université de Paris</div>
  </div>
</div>
<div class="section"><h2>Langues</h2>
  <div class="skills"><span class="skill">Français (natif)</span><span class="skill">Anglais (courant)</span><span class="skill">Espagnol (intermédiaire)</span></div>
</div>
<p style="text-align:center;font-size:11px;color:{c_secondary};margin-top:30px;">Généré par TemplateForge · templateforge.onrender.com</p>
</body></html>"""
    return html

def generate_landing(design, product_name="SaaSify", tagline="Launch your SaaS in days"):
    """Generate a landing page template"""
    ds = design
    c_bg, c_text, c_accent, c_secondary = ds["colors"]
    font = ds["fonts"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{product_name} - {tagline}</title>
<style>
  * {{margin:0;padding:0;box-sizing:border-box;}}
  body {{background:{c_bg};color:{c_text};font-family:{font};line-height:1.6;}}
  nav {{display:flex;justify-content:space-between;align-items:center;padding:16px 40px;border-bottom:1px solid {c_secondary}30;}}
  .logo {{font-weight:700;font-size:20px;color:{c_accent};}}
  .nav-links {{display:flex;gap:24px;list-style:none;}}
  .nav-links a {{color:{c_secondary};text-decoration:none;font-size:14px;}}
  .cta-btn {{padding:10px 24px;background:{c_accent};color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:14px;}}
  .hero {{text-align:center;padding:100px 20px;max-width:700px;margin:0 auto;}}
  .hero h1 {{font-size:48px;font-weight:800;margin-bottom:16px;line-height:1.2;}}
  .hero p {{font-size:18px;color:{c_secondary};margin-bottom:32px;}}
  .hero-buttons {{display:flex;gap:12px;justify-content:center;}}
  .hero-btn-outline {{padding:10px 24px;background:transparent;color:{c_accent};border:2px solid {c_accent};border-radius:8px;font-weight:600;cursor:pointer;}}
  .features {{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:32px;max-width:1000px;margin:0 auto;padding:40px 20px;}}
  .feature {{padding:24px;border:1px solid {c_secondary}20;border-radius:12px;}}
  .feature h3 {{font-size:18px;margin-bottom:8px;}}
  .feature p {{font-size:14px;color:{c_secondary};}}
  .pricing {{text-align:center;padding:60px 20px;}}
  .price-card {{display:inline-block;padding:32px;border:2px solid {c_accent};border-radius:16px;text-align:center;min-width:280px;}}
  .price {{font-size:48px;font-weight:800;}}
  .price span {{font-size:16px;color:{c_secondary};}}
  footer {{text-align:center;padding:40px;font-size:12px;color:{c_secondary};border-top:1px solid {c_secondary}20;}}
</style></head><body>
<nav><div class="logo">{product_name}</div>
  <ul class="nav-links"><li><a href="#">Features</a></li><li><a href="#">Pricing</a></li><li><a href="#">Docs</a></li></ul>
  <button class="cta-btn">Get Started</button></nav>
<div class="hero">
  <h1>{tagline}</h1>
  <p>Everything you need to ship faster. Built for indie developers and startups.</p>
  <div class="hero-buttons"><button class="cta-btn">Start Free Trial</button><button class="hero-btn-outline">View Demo</button></div></div>
<div class="features">
  <div class="feature"><h3>⚡ Lightning Fast</h3><p>Optimized for speed. Your users will love the instant page loads.</p></div>
  <div class="feature"><h3>🔒 Secure by Default</h3><p>Enterprise-grade security. SOC2 compliant, GDPR ready.</p></div>
  <div class="feature"><h3>🎨 Beautiful UI</h3><p>Modern design system. Dark mode, responsive, accessible.</p></div>
</div>
<div class="pricing">
  <div class="price-card"><h3>Pro Plan</h3><div class="price">$29<span>/mo</span></div>
    <p style="margin:16px 0;color:{c_secondary};">Everything you need</p>
    <button class="cta-btn">Get Started</button></div></div>
<footer>© 2026 {product_name}. Built with TemplateForge · templateforge.onrender.com</footer>
</body></html>"""
    return html

def generate_notion_template(design, template_type="Habit Tracker"):
    """Generate a markdown file that can be imported into Notion"""
    ds = design
    md = f"""# {template_type}
*Generated by TemplateForge*

---

## 📋 Overview
This **{template_type}** helps you track your daily habits and build consistency.

## 📊 Weekly View
| Habit | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|-------|-----|-----|-----|-----|-----|-----|-----|
| Exercise | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Read 30 min | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Meditate | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| No social media | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Code 2h | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

## 📈 Monthly Progress
- **Week 1**: _ / 5 habits
- **Week 2**: _ / 5 habits
- **Week 3**: _ / 5 habits
- **Week 4**: _ / 5 habits

## 🎯 Goals
- [ ] Hit 80% consistency this month
- [ ] Add 2 new habits next month
- [ ] Track streak length

## 🏆 Rewards
- 7-day streak: ☕ Fancy coffee
- 30-day streak: 📚 New book
- 90-day streak: 🎉 Weekend trip

## 💡 Tips
- Start small — one habit at a time
- Track at the same time every day
- Don't break the chain

---
*Style: {design['name']} — {design['style']}*
"""
    return md

def generate_slides(design, topic="Pitch Deck"):
    """Generate a simple HTML presentation"""
    ds = design
    c_bg, c_text, c_accent, c_secondary = ds["colors"]

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{topic}</title>
<style>
  * {{margin:0;padding:0;box-sizing:border-box;}}
  body {{background:{c_bg};color:{c_text};font-family:{ds['fonts']};}}
  .slide {{min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:60px;text-align:center;page-break-after:always;}}
  .slide h1 {{font-size:56px;margin-bottom:20px;}}
  .slide h2 {{font-size:36px;color:{c_accent};margin-bottom:16px;}}
  .slide h3 {{font-size:24px;margin-bottom:12px;}}
  .slide p {{font-size:18px;color:{c_secondary};max-width:600px;line-height:1.6;}}
  .slide-accent {{background:{c_accent};color:#fff;}}
  .slide-accent h2,.slide-accent p {{color:#fff;}}
  .grid {{display:grid;grid-template-columns:1fr 1fr;gap:40px;max-width:800px;text-align:left;}}
  .grid-item h3 {{margin-bottom:8px;}}
  .grid-item p {{font-size:14px;}}
</style></head><body>
<div class="slide"><h1>{topic}</h1><p>Your compelling subtitle goes here</p><p style="font-size:14px;margin-top:40px;color:{c_secondary};">Your Name · @handle · date</p></div>
<div class="slide slide-accent"><h2>The Problem</h2><p>Explain the pain point your audience faces. Make it relatable and urgent.</p></div>
<div class="slide"><h2>Our Solution</h2><p>Introduce your product or idea as the elegant answer to the problem above.</p></div>
<div class="slide"><div class="grid">
  <div class="grid-item"><h3>Market Size</h3><p>$XX Billion market growing at YY% CAGR. Massive opportunity waiting to be captured.</p></div>
  <div class="grid-item"><h3>Business Model</h3><p>SaaS subscription model with 90% gross margins. Freemium to enterprise upsell.</p></div>
  <div class="grid-item"><h3>Traction</h3><p>10,000+ users in 6 months. 40% MoM growth. Featured on Product Hunt #1.</p></div>
  <div class="grid-item"><h3>Team</h3><p>Ex-Google, ex-Stripe. 20+ years combined experience in this space.</p></div>
</div></div>
<div class="slide slide-accent"><h2>Call to Action</h2><p style="font-size:24px;">Let's build the future together.</p><p style="margin-top:20px;font-size:14px;">your@email.com · yoursite.com</p></div>
</body></html>"""
    return html

# ── TEMPLATE ENGINE ROUTES ────────────────────────────────
TEMPLATE_TYPES = {
    "cv": {"generator": generate_cv, "name": "CV", "ext": "html", "price": 9.99},
    "landing": {"generator": generate_landing, "name": "Landing Page", "ext": "html", "price": 19.99},
    "notion": {"generator": generate_notion_template, "name": "Notion Template", "ext": "md", "price": 4.99},
    "slides": {"generator": generate_slides, "name": "Slides", "ext": "html", "price": 14.99},
}

def create_template(category, design_idx=0, name_override=None):
    """Generate, save, and register a template"""
    tpl_id = str(uuid.uuid4())[:8]
    tpl_info = TEMPLATE_TYPES[category]
    design = DESIGN_SYSTEMS[design_idx % len(DESIGN_SYSTEMS)]

    product_name = name_override or f"{tpl_info['name']} - {design['name']}"

    # Generate content
    if category == "cv":
        content = generate_cv(design)
    elif category == "landing":
        content = generate_landing(design)
    elif category == "notion":
        content = generate_notion_template(design)
    elif category == "slides":
        content = generate_slides(design)
    else:
        content = ""

    # Save file
    filename = f"{tpl_id}_{category}_{design['style']}.{tpl_info['ext']}"
    filepath = os.path.join(GEN_DIR, category, filename)
    with open(filepath, "w") as f:
        f.write(content)

    # Save to DB
    conn = sqlite3.connect(DB)
    conn.execute("""
        INSERT INTO templates (id, name, category, subcategory, price, description, tags, file_path, status)
        VALUES (?,?,?,?,?,?,?,?,'published')
    """, (
        tpl_id, product_name, category, design['style'],
        tpl_info['price'],
        f"Professional {tpl_info['name']} template in {design['name']} style. Modern design, fully customizable.",
        f"{category},{design['style']},template,{tpl_info['name'].lower()}",
        filepath
    ))
    conn.commit()
    conn.close()

    return tpl_id, filepath

@app.route("/")
def landing():
    clean_types = {k: {"name": v["name"], "ext": v["ext"], "price": v["price"]} for k, v in TEMPLATE_TYPES.items()}
    return render_template("index.html", designs=DESIGN_SYSTEMS, types=clean_types)

@app.route("/generate", methods=["POST"])
def api_generate():
    data = request.get_json()
    category = data.get("category", "cv")
    design_idx = int(data.get("design", 0))
    name = data.get("name")
    count = min(int(data.get("count", 1)), 20)

    generated = []
    for _ in range(count):
        tpl_id, filepath = create_template(category, design_idx, name)
        generated.append({"id": tpl_id, "file": filepath, "type": category})

    return jsonify({"generated": len(generated), "templates": generated})

@app.route("/generate-all", methods=["POST"])
def api_generate_all():
    """Generate all combinations: 4 categories × 8 designs = 32 templates"""
    generated = []
    for category in TEMPLATE_TYPES:
        for idx in range(len(DESIGN_SYSTEMS)):
            tpl_id, filepath = create_template(category, idx)
            generated.append({"id": tpl_id, "category": category, "design": DESIGN_SYSTEMS[idx]['name']})

    return jsonify({"total": len(generated), "templates": generated})

@app.route("/api/templates")
def api_templates():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    templates = conn.execute(
        "SELECT * FROM templates WHERE status='published' ORDER BY created_at DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return jsonify([dict(t) for t in templates])

@app.route("/api/templates/<tpl_id>")
def api_template_detail(tpl_id):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    tpl = conn.execute("SELECT * FROM templates WHERE id=?", (tpl_id,)).fetchone()
    conn.close()
    if not tpl:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(tpl))

@app.route("/download/<tpl_id>")
def download(tpl_id):
    conn = sqlite3.connect(DB)
    tpl = conn.execute("SELECT file_path, name, category FROM templates WHERE id=?", (tpl_id,)).fetchone()
    conn.close()
    if not tpl or not os.path.exists(tpl[0]):
        return "Not found", 404

    return send_file(tpl[0], as_attachment=True, download_name=f"{tpl[1]}.{os.path.splitext(tpl[0])[1]}")

@app.route("/preview/<tpl_id>")
def preview(tpl_id):
    conn = sqlite3.connect(DB)
    tpl = conn.execute("SELECT file_path, name FROM templates WHERE id=?", (tpl_id,)).fetchone()
    conn.close()
    if not tpl or not os.path.exists(tpl[0]):
        return "Not found", 404
    with open(tpl[0]) as f:
        return f.read()

# ── Gumroad Integration ──────────────────────────────────
@app.route("/api/gumroad/upload", methods=["POST"])
def gumroad_upload():
    """Upload a template to Gumroad via API"""
    data = request.get_json()
    tpl_id = data.get("template_id")
    gumroad_token = data.get("gumroad_token")

    if not tpl_id or not gumroad_token:
        return jsonify({"error": "template_id and gumroad_token required"}), 400

    conn = sqlite3.connect(DB)
    tpl = conn.execute("SELECT * FROM templates WHERE id=?", (tpl_id,)).fetchone()
    conn.close()

    if not tpl:
        return jsonify({"error": "Template not found"}), 404

    # Gumroad API: create product
    import urllib.request

    payload = json.dumps({
        "access_token": gumroad_token,
        "name": tpl[1],
        "description": tpl[4],
        "price": int(tpl[3] * 100),  # cents
        "tags": tpl[5].split(","),
        "published": True
    }).encode()

    req = urllib.request.Request(
        "https://api.gumroad.com/v2/products",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if result.get("success"):
                product = result["product"]
                # Update DB with Gumroad info
                conn = sqlite3.connect(DB)
                conn.execute(
                    "UPDATE templates SET gumroad_id=?, gumroad_url=? WHERE id=?",
                    (product["id"], product["short_url"], tpl_id)
                )
                conn.commit()
                conn.close()
                return jsonify({"success": True, "gumroad_url": product["short_url"], "product_id": product["id"]})
            else:
                return jsonify({"error": "Gumroad API error", "detail": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/gumroad/batch", methods=["POST"])
def gumroad_batch():
    """Upload all published templates to Gumroad"""
    data = request.get_json()
    gumroad_token = data.get("gumroad_token")

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    templates = conn.execute(
        "SELECT * FROM templates WHERE status='published' AND gumroad_id IS NULL"
    ).fetchall()
    conn.close()

    results = []
    for tpl in templates:
        # Use internal API
        with app.test_client() as client:
            r = client.post("/api/gumroad/upload",
                json={"template_id": tpl["id"], "gumroad_token": gumroad_token})
            results.append({"id": tpl["id"], "name": tpl["name"], "result": r.get_json()})

    return jsonify({"uploaded": len(results), "results": results})

# ── Dashboard ──────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    templates = conn.execute(
        "SELECT * FROM templates WHERE status='published' ORDER BY created_at DESC"
    ).fetchall()

    stats = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(sales) as total_sales,
            SUM(revenue) as total_revenue,
            COUNT(CASE WHEN gumroad_id IS NOT NULL THEN 1 END) as on_gumroad
        FROM templates WHERE status='published'
    """).fetchone()
    conn.close()

    return render_template("dashboard.html",
        templates=templates,
        stats=dict(stats),
        designs=DESIGN_SYSTEMS,
        types=TEMPLATE_TYPES)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5060, debug=False)
