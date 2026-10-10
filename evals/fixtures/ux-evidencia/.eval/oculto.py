"""Verificador oculto de UX/accesibilidad para public/evidencia.html. Imprime OCULTOS_OK o OCULTOS_FALLA <motivos>."""
import re
import sys
from html.parser import HTMLParser


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs, self.labels_for, self.label_depth, self.wrapped = [], set(), 0, 0
        self.buttons, self.imgs, self.alerts, self.clickable_divs = 0, [], 0, 0

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit", "button"):
            self.inputs.append(a)
            if self.label_depth:
                self.wrapped += 1
                a["_wrapped"] = True
        if tag == "button" or (tag == "input" and a.get("type") == "submit"):
            self.buttons += 1
        if tag in ("div", "span") and "onclick" in a:
            self.clickable_divs += 1
        if tag == "img":
            self.imgs.append(a)
        if a.get("role") == "alert" or a.get("aria-live") in ("assertive", "polite"):
            self.alerts += 1

    def handle_endtag(self, tag):
        if tag == "label" and self.label_depth:
            self.label_depth -= 1


html = open("public/evidencia.html", encoding="utf-8").read()
p = P()
p.feed(html)
fallas = []
for i in p.inputs:
    etiquetado = i.get("_wrapped") or (i.get("id") in p.labels_for) or i.get("aria-label") or i.get("aria-labelledby")
    if not etiquetado:
        fallas.append(f"campo sin etiqueta: {i.get('name')}")
if p.buttons == 0 or p.clickable_divs:
    fallas.append("el envío no es un <button>/submit real")
if any(not i.get("alt") and i.get("alt") != "" for i in p.imgs if "alt" not in i):
    fallas.append("imagen sin alt")
if not p.alerts and not re.search(r"aria-describedby|aria-invalid", html):
    fallas.append("errores no anunciados (sin role=alert/aria-live/aria-describedby)")
print("OCULTOS_OK" if not fallas else "OCULTOS_FALLA " + "; ".join(fallas))
