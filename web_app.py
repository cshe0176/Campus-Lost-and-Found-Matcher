"""Optional local browser interface for the COMP9001 Lost & Found project.

All item storage and matching are implemented by main.py in Python.
This module uses only standard library modules to display the same data
through a browser, without external services, libraries, or accounts.

Run: python3 web_app.py
Then open http://127.0.0.1:8765 in your browser.
The terminal version remains available with: python3 main.py
"""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import argparse

import main


CSS = r"""
:root{--bg:#f5f7fb;--text:#102344;--muted:#60718a;--navy:#091b3a;
--blue:#4169e1;--line:#dfe7f2;--white:#fff;--mint:#bdeee1;--gold:#f4c66b}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:var(--text)}
a{text-decoration:none;color:inherit}button,input,select,textarea{font:inherit}
.top{background:var(--navy);color:white;padding:20px max(5vw,25px);display:flex;
justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap}
.brand{font-size:21px;font-weight:850;letter-spacing:-.6px}.brand em{font-style:normal;color:#91c9fb}
.toplinks{display:flex;align-items:center;gap:23px;font-size:14px;color:#cedaef}
.toplinks a:hover{color:white}.label{display:inline-flex;align-items:center;border:1px solid #43608b;
background:#142e53;color:#cce5ff;border-radius:30px;font-size:12px;padding:8px 12px}
.main{max-width:1220px;margin:auto;padding:32px 28px 60px}
.hero{background:linear-gradient(118deg,#112b58 0%,#102048 64%,#203f78 100%);color:white;
border-radius:24px;min-height:242px;padding:37px 40px;display:grid;
grid-template-columns:1.35fr .65fr;gap:25px;box-shadow:0 14px 30px #12325c17;overflow:hidden}
.tag{font-size:12px;text-transform:uppercase;letter-spacing:2px;font-weight:800;color:#8cd8c6}
h1{font-size:42px;line-height:1.09;letter-spacing:-1.5px;margin:12px 0 14px}
.hero p{font-size:15px;line-height:1.75;color:#d4e1f4;max-width:590px;margin:0 0 20px}
.hero-right{align-self:center;border-radius:18px;background:#ffffff12;border:1px solid #ffffff32;padding:22px}
.hero-right h3{font-size:17px;margin:0 0 15px}.score-row{display:flex;justify-content:space-between;
font-size:12px;color:#d6e8ff;margin:9px 0}.score-row strong{color:white}.bar{height:7px;border-radius:20px;
background:#ffffff2b;overflow:hidden}.bar span{display:block;height:100%;background:linear-gradient(90deg,#83d7df,#f6cf82)}
.actions{display:flex;flex-wrap:wrap;gap:9px}.btn{display:inline-flex;align-items:center;
justify-content:center;border:0;border-radius:10px;background:#4169e1;color:white;
padding:11px 16px;font-weight:750;font-size:13px;cursor:pointer;white-space:nowrap}
.btn:hover{filter:brightness(.95)}.btn.secondary{background:white;color:#152b50}
.btn.outline{background:#edf2fb;color:#234775}.btn.gold{background:var(--gold);color:#26304a}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0 32px}
.metric{background:white;border:1px solid var(--line);padding:20px 21px;border-radius:16px}
.metric .n{display:block;font-size:31px;font-weight:900;letter-spacing:-.9px;margin:8px 0 3px}
.muted{color:var(--muted)}.tiny{font-size:12px;color:var(--muted)}
.section-title{display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap;margin:24px 0 13px}
.section-title h2{font-size:23px;letter-spacing:-.5px;margin:0}.section-title p{margin:5px 0 0;font-size:13px;color:var(--muted)}
.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:18px;align-items:start}
.panel{border:1px solid var(--line);background:white;border-radius:17px;overflow:hidden}
.panel-h{padding:20px 22px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:12px}
.panel-h h3{font-size:17px;margin:0}.panel-body{padding:20px 22px}
.report{display:flex;gap:14px;align-items:center;padding:17px 20px;border-bottom:1px solid #edf0f5}
.report:last-child{border-bottom:0}.emoji{width:48px;height:48px;border-radius:13px;background:#e9effd;
color:#244ba0;display:grid;place-items:center;font-size:23px;flex:none}.report h4{margin:0 0 4px;font-size:14px}
.report p{margin:0;font-size:12px;color:var(--muted);line-height:1.5}
.report .middle{flex:1;min-width:0}.report .middle h4,.report .middle p{overflow-wrap:anywhere}
.pill{display:inline-block;border-radius:20px;padding:5px 9px;font-size:11px;font-weight:800}
.pill.lost{background:#ffebdf;color:#a3451f}.pill.found{background:#dff7ea;color:#197b53}
.pill.resolved{background:#e9ecf1;color:#6e7885}
.link{color:#2857b5;font-size:12px;font-weight:800}.link:hover{text-decoration:underline}
.empty{padding:37px 20px;color:var(--muted);text-align:center;font-size:14px;line-height:1.7}
.note{padding:13px 16px;background:#eef5ff;border:1px solid #d7e6ff;border-radius:12px;
font-size:12px;line-height:1.6;color:#344d77;margin:0 0 15px}
form label{font-size:12px;font-weight:800;color:#475978;display:block;margin:14px 0 6px}
input,select,textarea{border:1px solid #d3ddec;border-radius:9px;padding:11px 12px;width:100%;background:#fcfdff;
color:#132a4d;font-size:14px;outline:none}input:focus,select:focus,textarea:focus{border-color:#537ce6;
box-shadow:0 0 0 3px #4169e126}textarea{min-height:88px;resize:vertical}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.alert{padding:13px 16px;border-radius:10px;margin-bottom:15px;background:#fff0e9;color:#9a371c;font-size:13px}
.match{border:1px solid #dce7f6;border-radius:14px;padding:20px;background:linear-gradient(120deg,#f9fcff,#eff5ff);
margin:13px 0}.match-top{display:flex;justify-content:space-between;gap:10px;align-items:start}
.match h3{font-size:18px;margin:4px 0}.match-score{border-radius:12px;padding:11px 13px;background:#133c6a;color:#fff;
font-size:22px;font-weight:900;min-width:91px;text-align:center}.match-score small{font-size:10px;font-weight:500;display:block}
.reasons{display:flex;flex-wrap:wrap;gap:7px;margin:13px 0}.reason{background:#e1edff;border-radius:20px;
font-size:11px;padding:6px 10px;color:#315a91;font-weight:650}
.progress{height:9px;border-radius:20px;background:#dbe5f1;overflow:hidden;margin-top:14px}.progress span{display:block;height:100%;background:#2e9a86}
.sidecopy{font-size:13px;line-height:1.7;color:#667790}.footer{margin-top:34px;font-size:11px;
color:#8794a6;text-align:center}.kicker{font-size:11px;letter-spacing:.9px;text-transform:uppercase;font-weight:850;color:#6278a2}
@media(max-width:820px){.hero,.grid{grid-template-columns:1fr}.hero{padding:28px 24px}h1{font-size:34px}
.metrics{grid-template-columns:repeat(2,1fr)}.toplinks{gap:11px}.main{padding:18px 14px 50px}}
@media(max-width:490px){.form-row{grid-template-columns:1fr}.metrics{gap:8px}.metric{padding:13px}.hero-right{display:none}}
"""


def safe(value):
    """Escape text so user-supplied fields cannot inject HTML."""
    return escape(str(value), quote=True)


def category_icon(category):
    icons = {"Bag": "🎒", "Bottle": "◉", "Electronics": "⌁", "Keys": "⚿",
             "Wallet": "▣", "Clothing": "♧", "Umbrella": "☂", "Cards": "▤", "Other": "◇"}
    return icons.get(category, "◇")


def shell(content, *, page_title="Campus Lost & Found Matcher"):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe(page_title)}</title><style>{CSS}</style></head><body>
<header class="top"><a href="/" class="brand">CAMPUS <em>LOST & FOUND</em> <span style="font-weight:500">/ MATCHER</span></a>
<nav class="toplinks"><a href="/">Dashboard</a><a href="/new?type=lost">Report lost</a>
<a href="/new?type=found">Report found</a><span class="label">● &nbsp; LOCAL PYTHON APP</span></nav></header>
<main class="main">{content}<footer class="footer">COMP9001 · University student project · Python standard library only · Information stays on this computer.<br>
Similarity scores are rule-based indicators, not proof of ownership.</footer></main></body></html>"""


def report_row(report):
    status = (f'<span class="pill resolved">Resolved</span>' if report.status == 'resolved'
              else f'<span class="pill {safe(report.report_type)}">{safe(report.report_type.title())}</span>')
    action = (f'<a class="link" href="/match?id={report.report_id}">Find matches →</a>'
              if report.status == 'active' else '<span class="tiny">Closed</span>')
    return f"""<div class="report"><div class="emoji">{category_icon(report.category)}</div>
<div class="middle"><h4>#{report.report_id} · {safe(report.colour)} {safe(report.category)}</h4>
<p>{safe(report.location)} · {safe(report.description)}</p></div>{status}{action}</div>"""


def homepage(reports):
    active = [r for r in reports if r.status == 'active']
    lost = sum(r.report_type == 'lost' for r in active)
    found = sum(r.report_type == 'found' for r in active)
    resolved = len(reports) - len(active)
    list_html = ''.join(report_row(report) for report in reversed(reports[-8:])) or '<div class="empty">No reports yet. Add your first lost or found item.</div>'
    panel = f"""<div class="hero"><div><div class="tag">FIND WHAT BELONGS · CONNECT PEOPLE</div>
<h1>Lost something?<br>Let's find a match.</h1><p>Record a missing item, describe a found item, and discover possible matches using a transparent, explainable similarity score.</p>
<div class="actions"><a class="btn gold" href="/new?type=lost">+ Report a lost item</a>
<a class="btn secondary" href="/new?type=found">+ Report a found item</a></div></div>
<div class="hero-right"><h3>HOW MATCHING WORKS</h3>
<div class="score-row"><span>Category</span><strong>40 points</strong></div><div class="bar"><span style="width:100%"></span></div>
<div class="score-row"><span>Colour</span><strong>25 points</strong></div><div class="bar"><span style="width:62.5%"></span></div>
<div class="score-row"><span>Campus location</span><strong>15 points</strong></div><div class="bar"><span style="width:37.5%"></span></div>
<div class="score-row"><span>Description keywords</span><strong>up to 20</strong></div><div class="bar"><span style="width:50%"></span></div>
<p style="margin:17px 0 0;font-size:12px;color:#cadaeb">Suggestions start at 50/100. Always verify a potential match in person.</p>
</div></div>"""
    metrics = '<div class="metrics">' + ''.join(
        f'<div class="metric"><div class="kicker">{label}</div><span class="n">{number}</span><span class="tiny">{description}</span></div>'
        for label, number, description in [
            ('Active reports', len(active), 'Available for matching'),
            ('Lost items', lost, 'Seeking their owners'),
            ('Found items', found, 'Waiting to be claimed'),
            ('Resolved', resolved, 'Closed reports')]) + '</div>'
    recent = f'<section class="panel"><div class="panel-h"><h3>Recent reports</h3><span class="tiny">Latest eight</span></div>{list_html}</section>'
    explainer = f"""<section class="panel"><div class="panel-h"><h3>Find possible matches</h3></div><div class="panel-body">
<div class="note">Choose any active report below. The program looks for reports of the opposite type in the same category, then compares colour, location and description.</div>
<form method="get" action="/match"><label for="id">Choose a report</label><select id="id" name="id" required>
{''.join(f'<option value="{r.report_id}">#{r.report_id} · {safe(r.report_type.title())} · {safe(r.colour)} {safe(r.category)}</option>' for r in active)}
</select><div style="margin-top:16px"><button class="btn" type="submit" {'disabled' if not active else ''}>Find matches →</button></div></form>
<p class="sidecopy" style="margin-top:19px">No accounts, internet connection or extra Python packages are required. All data is saved in <code>reports.json</code>.</p>
</div></section>"""
    return shell(panel + metrics + '<div class="section-title"><h2>Find, compare, reunite.</h2><p>Browse existing reports or try the matching tool.</p></div>' + '<div class="grid">' + recent + explainer + '</div>')


def new_report_page(report_type, error=''):
    if report_type not in ('lost', 'found'):
        report_type = 'lost'
    category_options = ''.join(f'<option value="{safe(cat)}">{safe(cat)}</option>' for cat in main.CATEGORIES)
    title = f'Report a {report_type} item'
    return shell(f"""<div class="section-title"><div><div class="kicker">STEP 01 · CREATE A REPORT</div><h2>{title.title()}</h2>
<p>It takes four details to create a searchable report.</p></div><a class="btn outline" href="/">← Back to dashboard</a></div>
<div class="grid"><section class="panel"><div class="panel-body">
{f'<div class="alert">{safe(error)}</div>' if error else ''}
<form method="post" action="/new"><input type="hidden" name="type" value="{report_type}">
<div class="form-row"><div><label for="cat">Item category</label><select name="category" id="cat" required>{category_options}</select></div>
<div><label for="colour">Colour</label><input id="colour" name="colour" maxlength="80" placeholder="e.g. Black" required></div></div>
<label for="location">Campus location</label><input id="location" name="location" maxlength="120" placeholder="e.g. Fisher Library" required>
<label for="desc">Description</label><textarea id="desc" name="description" maxlength="500" placeholder="e.g. Black metal bottle with a white sticker" required></textarea>
<div style="margin-top:20px"><button class="btn" type="submit">Save report →</button></div></form></div></section>
<aside class="panel"><div class="panel-h"><h3>Tips for a useful report</h3></div><div class="panel-body">
<p class="sidecopy">✓ Include a specific colour.</p><p class="sidecopy">✓ Use the same campus building name if possible.</p>
<p class="sidecopy">✓ Add distinct keywords such as a sticker, brand, pattern or material.</p>
<div class="note">Privacy tip: do not enter passwords, student ID numbers or sensitive contact details.</div>
</div></aside></div>""", page_title=title)


def compute_matches(reports, selected):
    """Use exactly the same matching algorithm as the terminal version."""
    matches = []
    for report in reports:
        if (report.report_id == selected.report_id or report.status != 'active'
                or report.report_type == selected.report_type):
            continue
        score, reasons = main.match_breakdown(selected, report)
        if score >= main.MINIMUM_MATCH_SCORE:
            matches.append((score, report, reasons))
    matches.sort(key=lambda x: (-x[0], x[1].report_id))
    return matches


def match_page(reports, requested_id, note=''):
    selected = main.find_report_by_id(reports, requested_id)
    if selected is None or selected.status != 'active':
        return shell('<div class="alert">The requested active report was not found.</div><a class="btn" href="/">Back to dashboard</a>')
    matches = compute_matches(reports, selected)
    if not matches:
        matches_html = '<div class="empty">No close matches have been reported yet.<br>Come back after more items are added.</div>'
    else:
        matches_html = ''
        for score, item, reasons in matches:
            matches_html += f"""<article class="match"><div class="match-top"><div><div class="kicker">POSSIBLE MATCH · REPORT #{item.report_id}</div>
<h3>{safe(item.colour)} {safe(item.category)}</h3><div class="tiny">{safe(item.location)} · {safe(item.description)}</div>
</div><div class="match-score">{score}<small>OUT OF 100</small></div></div>
<div class="progress"><span style="width:{score}%"></span></div>
<div class="reasons">{''.join(f'<span class="reason">{safe(reason)}</span>' for reason in reasons)}</div>
<span class="pill {safe(item.report_type)}">{safe(item.report_type.title())}</span>
</article>"""
    return shell(f"""<div class="section-title"><div><div class="kicker">STEP 02 · EXPLAINABLE MATCHING</div><h2>Possible matches for report #{selected.report_id}</h2>
<p>{safe(selected.colour)} {safe(selected.category)} · {safe(selected.location)}</p></div>
<a class="btn outline" href="/">← Back to dashboard</a></div>
{f'<div class="note">{safe(note)}</div>' if note else ''}
<div class="grid"><section class="panel"><div class="panel-h"><h3>Ranked match suggestions</h3><span class="tiny">{len(matches)} result(s)</span></div>
<div class="panel-body"><div class="note">Each score reflects matching attributes, not the probability of an actual recovery.</div>{matches_html}</div></section>
<aside class="panel"><div class="panel-h"><h3>Selected report</h3></div><div class="panel-body">
<div style="font-size:38px">{category_icon(selected.category)}</div><h2>{safe(selected.colour)} {safe(selected.category)}</h2>
<p class="sidecopy">Location: <strong>{safe(selected.location)}</strong></p><p class="sidecopy">{safe(selected.description)}</p>
<span class="pill {safe(selected.report_type)}">{safe(selected.report_type.title())}</span>
<div style="margin-top:24px" class="note">If an item has been recovered, you can close the report below so it no longer appears in future matching.</div>
<form method="post" action="/resolve" onsubmit="return confirm('Mark this report as resolved?');">
<input type="hidden" name="id" value="{selected.report_id}"><button class="btn outline" type="submit">Mark report as resolved</button></form>
</div></aside></div>""", page_title=f'Matches for report #{selected.report_id}')


class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Keep the presentation terminal free from routine access log messages.
        return

    def respond(self, text, code=200):
        encoded = text.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, path):
        self.send_response(303)
        self.send_header('Location', path)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def get_reports(self):
        return main.load_reports()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        try:
            reports = self.get_reports()
            if path == '/':
                self.respond(homepage(reports))
            elif path == '/new':
                report_type = params.get('type', ['lost'])[0]
                self.respond(new_report_page(report_type))
            elif path == '/match':
                value = params.get('id', [''])[0]
                try:
                    selected_id = int(value)
                except ValueError:
                    selected_id = 0
                self.respond(match_page(reports, selected_id))
            else:
                self.respond(shell('<h2>Page not found</h2><a class="btn" href="/">Back to dashboard</a>'), 404)
        except (OSError, ValueError) as exc:
            self.respond(shell(f'<div class="alert">Unable to load reports: {safe(exc)}</div>'), 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in ('/new', '/resolve'):
            self.respond(shell('<h2>Page not found</h2>'), 404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > 20000:
                self.respond(shell('<div class="alert">Invalid form submission.</div>'), 400)
                return
            fields = parse_qs(self.rfile.read(length).decode('utf-8'))
            get = lambda k: fields.get(k, [''])[0].strip()
            reports = self.get_reports()
            if parsed.path == '/new':
                rtype = get('type')
                category = get('category')
                colour, location, description = (get('colour'), get('location'), get('description'))
                if (rtype not in ('lost', 'found') or category not in main.CATEGORIES
                        or not all((colour, location, description)) or len(colour) > 80
                        or len(location) > 120 or len(description) > 500):
                    self.respond(new_report_page(rtype, 'Please complete all fields using valid values.'), 400)
                    return
                report = main.ItemReport(main.next_report_id(reports), rtype, category,
                                         colour, location, description)
                reports.append(report)
                main.save_reports(reports)
                self.redirect(f'/match?id={report.report_id}')
            else:
                report_id = int(get('id'))
                report = main.find_report_by_id(reports, report_id)
                if report is None:
                    self.respond(shell('<div class="alert">Report not found.</div>'), 404)
                    return
                report.status = 'resolved'
                main.save_reports(reports)
                self.redirect('/')
        except (OSError, ValueError, UnicodeError) as exc:
            self.respond(shell(f'<div class="alert">The request could not be completed: {safe(exc)}</div>'), 400)


def run_server(port=8765):
    server = ThreadingHTTPServer(('127.0.0.1', port), AppHandler)
    print('Campus Lost & Found Matcher - Visual Demo')
    print(f'Open this address in your browser: http://127.0.0.1:{server.server_port}')
    print('Press Ctrl+C in this terminal to stop the server.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nVisual demo stopped.')
    finally:
        server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Open the optional local browser view.')
    parser.add_argument('--port', type=int, default=8765)
    run_server(parser.parse_args().port)
