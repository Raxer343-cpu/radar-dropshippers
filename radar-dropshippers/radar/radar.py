"""Radar de tiendas · Raíz Lab / Tu Manito
Revisa cada día el catálogo público (/products.json) de tiendas Shopify de la competencia
y registra qué cambió: productos nuevos (pruebas), retirados (pruebas que murieron),
cambios de precio y productos agotados o reactivados.
Solo usa información pública de tiendas. No guarda datos de personas.
"""
import csv, json, os, time, datetime, urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIENDAS = os.path.join(RAIZ, "radar", "tiendas.csv")
SNAP = os.path.join(RAIZ, "data", "snapshots")
CAMBIOS = os.path.join(RAIZ, "data", "cambios.csv")
RESUMEN = os.path.join(RAIZ, "data", "resumen.md")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
HOY = os.environ.get("RADAR_FECHA") or datetime.date.today().isoformat()


def bajar(dominio, fetch=None):
    """Lista de productos, o None si la tienda no expone /products.json."""
    productos, pagina = [], 1
    while pagina <= 8:
        url = f"https://{dominio}/products.json?limit=250&page={pagina}"
        try:
            if fetch:
                data = fetch(url)
            else:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    data = json.loads(r.read().decode("utf-8", "replace"))
        except Exception:
            return None if pagina == 1 else productos
        lote = data.get("products", [])
        if not lote:
            break
        productos += lote
        if len(lote) < 250:
            break
        pagina += 1
        time.sleep(1.5)
    return productos


def resumir(p):
    variantes = p.get("variants", [])
    precios = [float(v.get("price") or 0) for v in variantes] or [0.0]
    return {
        "id": p.get("id"),
        "titulo": (p.get("title") or "").strip(),
        "handle": p.get("handle"),
        "precio": min(precios),
        "disponible": any(v.get("available") for v in variantes),
        "creado": (p.get("created_at") or "")[:10],
        "publicado": (p.get("published_at") or "")[:10],
        "actualizado": (p.get("updated_at") or "")[:10],
        "tipo": p.get("product_type") or "",
        "imagen": ((p.get("images") or [{}])[0].get("src") or "").split("?")[0],
    }


def comparar(dominio, antes, ahora):
    cambios = []
    a = {str(x["id"]): x for x in antes}
    b = {str(x["id"]): x for x in ahora}
    url = lambda x: f"https://{dominio}/products/{x['handle']}"
    for k, x in b.items():
        if k not in a:
            cambios.append([HOY, dominio, "nuevo", x["titulo"], "", x["precio"], url(x)])
            continue
        y = a[k]
        if abs(y["precio"] - x["precio"]) > 0.5:
            cambios.append([HOY, dominio, "precio", x["titulo"], y["precio"], x["precio"], url(x)])
        if y["disponible"] and not x["disponible"]:
            cambios.append([HOY, dominio, "agotado", x["titulo"], "", x["precio"], url(x)])
        if not y["disponible"] and x["disponible"]:
            cambios.append([HOY, dominio, "reactivado", x["titulo"], "", x["precio"], url(x)])
    for k, y in a.items():
        if k not in b:
            cambios.append([HOY, dominio, "retirado", y["titulo"], y["precio"], "", url(y)])
    return cambios


def correr(fetch=None):
    with open(TIENDAS, encoding="utf-8") as f:
        tiendas = [r for r in csv.DictReader(f) if r.get("dominio") and (r.get("activa") or "si").strip() != "no"]
    os.makedirs(SNAP, exist_ok=True)
    nuevos, filas = [], []
    for t in tiendas:
        dom = t["dominio"].strip().lower().replace("https://", "").replace("http://", "").strip("/")
        prods = bajar(dom, fetch)
        ruta = os.path.join(SNAP, dom.replace("/", "_") + ".json")
        if prods is None:
            filas.append((dom, t.get("nombre", ""), "sin /products.json (no es Shopify o bloquea)", 0, 0))
            continue
        ahora = sorted((resumir(p) for p in prods), key=lambda x: x["publicado"], reverse=True)
        antes = None
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                antes = json.load(f)["productos"]
        c = comparar(dom, antes, ahora) if antes is not None else []
        nuevos += c
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump({"dominio": dom, "fecha": HOY, "productos": ahora}, f, ensure_ascii=False, indent=1)
        filas.append((dom, t.get("nombre", ""), "primera foto" if antes is None else "ok", len(ahora), len(c)))
        time.sleep(1)

    existe = os.path.exists(CAMBIOS)
    with open(CAMBIOS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["fecha", "dominio", "tipo", "producto", "antes", "ahora", "url"])
        w.writerows(nuevos)

    with open(RESUMEN, "w", encoding="utf-8") as f:
        f.write(f"# Radar de tiendas · {HOY}\n\n")
        f.write("| Tienda | Nombre | Estado | Productos | Cambios hoy |\n|---|---|---|---|---|\n")
        for d, n, e, p, c in filas:
            f.write(f"| {d} | {n} | {e} | {p} | {c} |\n")
        f.write("\n## Cambios de hoy\n\n")
        if nuevos:
            f.write("| Tienda | Tipo | Producto | Antes | Ahora |\n|---|---|---|---|---|\n")
            for c in nuevos:
                f.write(f"| {c[1]} | {c[2]} | {c[3][:60]} | {c[4]} | {c[5]} |\n")
        else:
            f.write("Sin cambios (o es la primera foto de la tienda).\n")
    print(f"{len(filas)} tiendas · {len(nuevos)} cambios")
    return filas, nuevos


if __name__ == "__main__":
    correr()
