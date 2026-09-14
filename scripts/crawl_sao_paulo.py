"""Checkpointed traversal of every public agency/page in the SP Imóvel directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import threading
import time

import requests
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Extract.SPImovelScraper import DIRECTORY_URL, DIRECTORY_API, parse_directory_page, parse_directory_html, parse_agency_page


class Fetcher:
    def __init__(self, interval):
        self.interval = interval
        self.lock = threading.Lock()
        self.next_request = 0
        self.local = threading.local()

    def get(self, url, **kwargs):
        if not hasattr(self.local, 'session'):
            self.local.session = requests.Session()
            self.local.session.headers['User-Agent'] = 'Mozilla/5.0'
        with self.lock:
            wait = max(0, self.next_request - time.monotonic())
            self.next_request = max(self.next_request, time.monotonic()) + self.interval
        if wait:
            time.sleep(wait)
        r = self.local.session.get(url, timeout=(10, 25), **kwargs)
        r.raise_for_status()
        return r


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
    temporary.replace(path)


def crawl_agency(agency, fetcher, checkpoint, resume, pages_limit=None):
    cache_file = checkpoint / f"{agency['id']}.json"
    state = json.loads(cache_file.read_text()) if resume and cache_file.exists() else {
        'agency': agency, 'status': 'pending', 'properties': [], 'next_page': 1, 'seen_signatures': [], 'all_ids': [],
    }
    if state['status'] == 'complete':
        return state
    state['status'] = 'running'
    try:
        while True:
            page = state['next_page']
            params = {'PageNumber': page} if page > 1 else {}
            response = fetcher.get(agency['url'], params=params)
            rows, pages, signature, expected = parse_agency_page(response.text, agency)
            if page > 1:
                expected = state['expected_ads']
                pages = state['expected_pages']
            state['expected_ads'] = expected
            state['expected_pages'] = pages
            state['last_update'] = datetime.now(timezone.utc).isoformat()
            repeated = bool(signature and list(signature) in state['seen_signatures'])
            state['consecutive_repeated_pages'] = state.get('consecutive_repeated_pages', 0) + 1 if repeated else 0
            if state['consecutive_repeated_pages'] >= 4:
                raise ValueError(f'Página {page} repetida quatro vezes; cobertura incompleta')
            if not signature and expected > 0 and page <= pages:
                raise ValueError(f'Página {page} vazia antes de completar catálogo')
            if not repeated:
                state['seen_signatures'].append(list(signature))
            state['all_ids'] = list(set(state['all_ids']) | set(signature))
            state['properties'] = list({p['link']: p for p in state['properties'] + rows}.values())
            state['next_page'] = page + 1
            complete = len(state['all_ids']) >= expected
            exhausted = page >= pages * 4
            if complete or exhausted:
                state['status'] = 'complete' if complete else 'partial'
                state.pop('error', None)
                # Count includes rentals/other cities excluded from the app intentionally.
                if len(state['all_ids']) < expected:
                    state['status'] = 'partial'
                    state['error'] = f"Catálogo mudou durante a coleta ou contém anúncios repetidos: {len(state['all_ids'])}/{expected}"
            atomic_json(cache_file, state)
            if complete or exhausted:
                break
            if pages_limit and page >= pages_limit:
                state['status'] = 'sampled'
                atomic_json(cache_file, state)
                break
    except Exception as exc:
        state['status'] = 'partial' if state['properties'] else 'failed'
        state['error'] = str(exc)
        atomic_json(cache_file, state)
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--interval', type=float, default=0.5, help='Global seconds between requests; default 2 req/s')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--limit-agencies', type=int, help='Only for development; omit for all directory entries')
    parser.add_argument('--discover-only', action='store_true')
    parser.add_argument('--registry-file', type=Path, help='Previously discovered directory report')
    parser.add_argument('--pages-per-agency', type=int, help='Optional sampling limit; omit for full catalogues')
    args = parser.parse_args()
    fetcher = Fetcher(max(0.25, args.interval))
    args.checkpoint.mkdir(parents=True, exist_ok=True)
    if args.registry_file:
        registry = json.loads(args.registry_file.read_text())
        count = registry['expected_directory_entries']
        agencies = {a['id']: a for a in registry['agencies']}
        discovery_errors = registry.get('discovery_errors', [])
    else:
        root = BeautifulSoup(fetcher.get(DIRECTORY_URL).text, 'html.parser')
        count = int(root.select_one('input[name="txtCount"]')['value'])
        per_page = int(root.select_one('input[name="txtItens"]')['value'])
        directory_filter = root.select_one('#ck_filtro_lista_imobiliaria')['value']
        agencies = {}
        discovery_errors = []
        page, repeated_pages = 1, 0
        # Use the same public pagination endpoint and headers as the site's UI.
        while len(agencies) < count and page <= math.ceil(count / per_page):
            try:
                rows = parse_directory_html(str(root)) if page == 1 else parse_directory_page(
                    fetcher.get(DIRECTORY_API, params={'pageNumber': page, 'paramStr': directory_filter},
                        headers={'Referer': DIRECTORY_URL, 'X-Requested-With': 'XMLHttpRequest'}).json())
                if not rows:
                    raise ValueError('Página do diretório sem entradas reconhecidas')
                before = len(agencies)
                for agency in rows:
                    agencies[agency['id']] = agency
                repeated_pages = repeated_pages + 1 if len(agencies) == before else 0
                print(f'Diretório: página {page}, {len(agencies)}/{count} entradas', flush=True)
                if repeated_pages >= 4:
                    discovery_errors.append({'page': page, 'error': 'Quatro páginas repetidas; diretório incompleto'})
                    break
            except Exception as exc:
                discovery_errors.append({'page': page, 'error': str(exc)})
            page += 1
        if len(agencies) < count:
            discovery_errors.append({'error': f'Diretório incompleto: {len(agencies)}/{count}'})
    atomic_json(args.report, {'directory': DIRECTORY_URL, 'expected_directory_entries': count,
        'discovered': len(agencies), 'discovery_errors': discovery_errors, 'agencies': list(agencies.values()), 'results': []})
    if args.discover_only:
        return
    selected = list(agencies.values())[:args.limit_agencies] if args.limit_agencies else list(agencies.values())
    previous = json.loads(args.catalog.read_text()) if args.catalog.exists() else {'properties': []}
    previous_rows = {p['link']: p for p in previous['properties']}
    results = []
    def save():
        now = datetime.now(timezone.utc).isoformat()
        merged = previous_rows.copy()
        for state in results:
            agency_id = state['agency']['id']
            if state['status'] == 'complete':
                merged = {k: p for k, p in merged.items() if not (p.get('source_portal') == 'SPImovel' and p.get('agency_id') == agency_id)}
            for p in state['properties']:
                p['data_scrape'] = state.get('last_update', now)
                merged[p['link']] = p
        summary = {s: sum(r['status'] == s for r in results) for s in ['complete', 'partial', 'failed', 'sampled']}
        metadata = {'directory': DIRECTORY_URL, 'expected_directory_entries': count, 'discovered': len(agencies),
            'attempted': len(results), 'selected': len(selected), 'discovery_errors': discovery_errors,
            'summary': summary, 'pages_per_agency_limit': args.pages_per_agency, 'last_update': now, 'agencies': list(agencies.values()),
            'results': [{k: v for k, v in r.items() if k not in ['properties', 'seen_signatures', 'all_ids']} | {'sale_ads_in_sp': len(r['properties'])} for r in results]}
        atomic_json(args.report, metadata)
        atomic_json(args.catalog, {'last_update': now, 'failures': previous.get('failures', {}),
            'coverage': {k: v for k, v in metadata.items() if k not in ['agencies', 'results']}, 'properties': list(merged.values())})
    with ThreadPoolExecutor(max_workers=max(1, min(4, args.workers))) as executor:
        futures = [executor.submit(crawl_agency, a, fetcher, args.checkpoint, args.resume, args.pages_per_agency) for a in selected]
        for future in as_completed(futures):
            state = future.result()
            results.append(state)
            print(f"Agências: {len(results)}/{len(selected)} | {state['agency']['nome']}: {state['status']}, {len(state['properties'])} anúncios SP", flush=True)
            if len(results) % 10 == 0 or len(results) == len(selected):
                save()
    save()
    print('Coleta concluída. Consulte o relatório para distinguir cobertura completa, parcial e falhas.', flush=True)


if __name__ == '__main__':
    main()
