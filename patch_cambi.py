"""
Patch script v3 - fix destinazione sbagliata
"""
import os, sys, ast

FILENAME = 'treni.py'

if not os.path.exists(FILENAME):
    print(f"ERRORE: {FILENAME} non trovato!")
    sys.exit(1)

with open(FILENAME, 'r', encoding='utf-8') as f:
    content = f.read()

MARKER_START = "        elif parsed.path == '/api/cambi':"
MARKER_END   = "        elif parsed.path == '/api/treno':"

start = content.find(MARKER_START)
end   = content.find(MARKER_END)

if start == -1 or end == -1:
    print("ERRORE: blocco /api/cambi non trovato!")
    sys.exit(1)

print(f"Trovato blocco cambi: righe {content[:start].count(chr(10))+1} - {content[:end].count(chr(10))+1}")

NEW_BLOCK = """        elif parsed.path == '/api/cambi':
            from_id   = p('from')
            to_id     = p('to')
            to_nome   = p('to-nome').upper().strip()
            from_nome = p('from-nome').upper().strip()
            date      = p('date') or datetime.now().strftime('%Y-%m-%d')
            time_str  = p('time') or datetime.now().strftime('%H:%M')
            from datetime import timedelta
            MARGINE_MIN = 10
            try:
                base_dt = datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
            except:
                base_dt = datetime.now()

            INTERSCAMBI = {
                'ROMA TERMINI': 'S08409', 'MILANO CENTRALE': 'S01700',
                'BOLOGNA CENTRALE': 'S03300', 'FIRENZE S.M.N.': 'S06103',
                'NAPOLI CENTRALE': 'S09218', 'TORINO PORTA NUOVA': 'S00219',
                'VENEZIA SANTA LUCIA': 'S02528', 'GENOVA PIAZZA PRINCIPE': 'S00588',
                'PADOVA': 'S02534', 'VERONA PORTA NUOVA': 'S02112',
                'REGGIO CALABRIA': 'S11781', 'BARI CENTRALE': 'S10030',
                'PALERMO CENTRALE': 'S12101', 'CATANIA CENTRALE': 'S12325',
                'TRIESTE CENTRALE': 'S02827', 'BRESCIA': 'S02002',
                'PISA CENTRALE': 'S06401', 'ANCONA': 'S07101',
                'PESCARA CENTRALE': 'S08101', 'SALERNO': 'S09601',
                'CASSINO': 'S08662', 'FROSINONE': 'S08501',
                'LATINA': 'S08601', 'CASERTA': 'S09101',
                'REGGIO EMILIA': 'S03521', 'MODENA': 'S03501',
                'PARMA': 'S03601', 'PIACENZA': 'S03701',
                'BERGAMO': 'S01940', 'VARESE': 'S01801',
                'COMO SAN GIOVANNI': 'S01901', 'ALESSANDRIA': 'S00501',
            }

            to_kw = [w for w in to_nome.split() if len(w) > 3]

            def _match_strict(dest, nome_completo):
                \"\"\"Match rigoroso: la destinazione deve contenere tutte le parole significative.\"\"\"
                d = dest.upper().strip()
                n = nome_completo.upper().strip()
                # Match esatto o contenimento
                if n == d or n in d or d in n:
                    return True
                # Tutte le parole significative devono essere presenti
                parole = [w for w in n.split() if len(w) > 3]
                return bool(parole) and all(w in d for w in parole)

            def _get_int(nome_dest):
                nd = nome_dest.upper()
                for ni, ii in INTERSCAMBI.items():
                    pi = [w for w in ni.split() if len(w) > 3]
                    pd2 = nd.split()
                    if pi and all(p in pd2 for p in pi[:2]):
                        return ii, ni
                    if ni in nd or nd in ni:
                        return ii, ni
                return None, None

            def _cerca_int(sid, snome, arr_ms, t1):
                sols = []
                try:
                    arr_dt = datetime.fromtimestamp(arr_ms / 1000)
                except:
                    return sols
                min_dt = arr_dt + timedelta(minutes=MARGINE_MIN)

                # Prova piu fasce orarie
                tb_all = []
                seen_t = set()
                for dh in [0, 1, 2, 3, 4]:
                    dt_try = min_dt + timedelta(hours=dh)
                    orario2 = build_orario(dt_try.strftime('%H:%M'), dt_try.strftime('%Y-%m-%d'))
                    tb = api(f'/partenze/{sid}/{urllib.parse.quote(orario2)}')
                    if tb and isinstance(tb, list):
                        for tx in tb:
                            k = tx.get('numeroTreno')
                            if k and k not in seen_t:
                                seen_t.add(k)
                                tb_all.append(tx)

                print(f"[INT] {snome} trovati {len(tb_all)} treni totali, min_dt={min_dt}", flush=True)

                for t2 in tb_all:
                    dest2 = (t2.get('destinazione') or '').upper()
                    op2 = (t2.get('orarioPartenza') or
                           t2.get('millisDataPartenza') or
                           t2.get('dataPartenzaTreno'))
                    if not op2:
                        continue
                    try:
                        p2_dt = datetime.fromtimestamp(op2 / 1000)
                    except:
                        continue
                    if p2_dt < min_dt:
                        continue

                    # Match rigoroso sulla destinazione finale
                    ok = _match_strict(dest2, to_nome)
                    arr_d = t2.get('orarioArrivo')

                    if not ok:
                        # Verifica nelle fermate solo se la destinazione e plausibile
                        # (evita di controllare treni che vanno nella direzione opposta)
                        c2 = t2.get('codOrigine')
                        n2 = t2.get('numeroTreno')
                        if c2 and n2:
                            f2d = api(f'/andamentoTreno/{c2}/{n2}/{op2}')
                            if f2d and isinstance(f2d, dict):
                                fermate = f2d.get('fermate', [])
                                for fm in fermate:
                                    nf = (fm.get('stazione') or '').upper()
                                    if _match_strict(nf, to_nome):
                                        arr_d = fm.get('arrivo_teorico') or fm.get('programmata')
                                        ok = True
                                        break

                    if ok:
                        print(f"[TROVATO] cambio a {snome} con {t2.get('numeroTreno')} dest={dest2}", flush=True)
                        sols.append({
                            'tipo': 'cambio', 'treno1': t1, 'treno2': t2,
                            'stazioneCAMBIO': snome, 'oraArrCambio': arr_ms,
                            'oraPartCambio': op2,
                            'attesaMin': int((p2_dt - arr_dt).total_seconds() / 60),
                            'orarioPartenza': t1.get('orarioPartenza'),
                            'orarioArrivo': arr_d or t2.get('orarioArrivo'),
                        })
                        break
                return sols

            # Raccogli treni da A
            treni_a = []
            seen = set()
            for dh in [0, 2]:
                dt = base_dt + timedelta(hours=dh)
                or1 = build_orario(dt.strftime('%H:%M'), dt.strftime('%Y-%m-%d'))
                parz = api(f'/partenze/{from_id}/{urllib.parse.quote(or1)}')
                if parz and isinstance(parz, list):
                    for t in parz:
                        k = t.get('numeroTreno')
                        if k and k not in seen:
                            seen.add(k)
                            treni_a.append(t)

            print(f"[CAMBI] from={from_id} to={to_id} to_nome={to_nome} trovati {len(treni_a)} treni", flush=True)
            if not treni_a:
                send_json(self, [])
                return

            tutte = []
            for t in treni_a[:8]:
                num  = t.get('numeroTreno')
                ts   = t.get('orarioPartenza')
                dest = (t.get('destinazione') or '').upper()
                if not num or not ts:
                    continue
                print(f"[TRENO] {num} dest={dest}", flush=True)

                sid, snome = _get_int(dest)
                if sid and sid != from_id and sid != to_id:
                    arr = t.get('orarioArrivo') or ts
                    tutte.extend(_cerca_int(sid, snome, arr, t))

                if len(tutte) >= 3:
                    break

                cod = t.get('codOrigine')
                if cod:
                    fd = api(f'/andamentoTreno/{cod}/{num}/{ts}')
                    if fd and isinstance(fd, dict):
                        fermate = fd.get('fermate', [])
                        fkw = [w for w in from_nome.split() if len(w) > 3]
                        idx = 0
                        for i, fm in enumerate(fermate):
                            if any(k in (fm.get('stazione') or '').upper() for k in fkw):
                                idx = i
                                break
                        seen_int = {snome} if snome else set()
                        for fm in fermate[idx + 1:]:
                            nf = (fm.get('stazione') or '').upper()
                            si2, sn2 = _get_int(nf)
                            if not si2 or si2 == from_id or si2 == to_id:
                                continue
                            if sn2 in seen_int:
                                continue
                            seen_int.add(sn2)
                            am = fm.get('arrivo_teorico') or fm.get('programmata') or fm.get('partenza_teorica')
                            if not am:
                                continue
                            tutte.extend(_cerca_int(si2, sn2, am, t))
                            if len(tutte) >= 3:
                                break

            seen_s = set()
            uniche = []
            for s in tutte:
                k = (s['treno1'].get('numeroTreno'), s['stazioneCAMBIO'], s['treno2'].get('numeroTreno'))
                if k not in seen_s:
                    seen_s.add(k)
                    uniche.append(s)
            uniche.sort(key=lambda s: s.get('orarioPartenza') or 0)
            print(f"[CAMBI] Soluzioni trovate: {len(uniche)}", flush=True)
            send_json(self, uniche[:8])

"""

with open(FILENAME + '.bak', 'w', encoding='utf-8') as f:
    f.write(content)
print("Backup creato: treni.py.bak")

new_content = content[:start] + NEW_BLOCK + content[end:]

try:
    ast.parse(new_content)
    with open(FILENAME, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"OK! File modificato con successo.")
    print(f"Righe totali: {new_content.count(chr(10))}")
except SyntaxError as e:
    print(f"ERRORE di sintassi: {e}")
    with open(FILENAME, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Backup ripristinato!")
