#!/usr/bin/env python3
# author: Jen Hammond (@frinjee)
# class | assignment: CYFI-330/700 | Belkasoft 7
# ref source page 1: view-source:https://belkasoft.com/belkactf7/chall/whoami [additional comments below]
# all challenge pages seem similar & stable to use just the first challenge pg source as reference for divs, slugs, etc to refer ->
# regex, pull from
# screenshots within repository for additional reference [pgsrc_chall-list.png, pgsrc_divspanrefer.png]

import requests
import argparse
import re, sys, html

BASE_URL = 'https://belkasoft.com/belkactf7/chall'

# map arg input to site slug
CHALLS = {
	1: 'whoami',
	2: 'locker',
	3: 'sample',
	4: 'infection',
	5: 'cnc',
	6: 'apikey',
	7: 'puppetmaster',
	8: 'android',
	9: 'workspace',
	10: 'banking',
	11: 'junkmsgs',
	12: 'search',
	13: 'partyvan',
	14: 'newname',
	15: 'metamorphosis',
	16: 'bonus',
	17: 'throughttrap',
	18: 'vehicle',
	19: 'radars',
	20: 'foofighter',
	21: 'flyby',
	22: 'inside',
	23: 'salvation',
	24: 'congrats',
}

# turn selected html into just plain text
def tags(st: str) -> str:
	st = re.sub(r'(?is)<br\s*/?>', '\n', st) # <br> -> newline for self closing tags
	st = re.sub(r'(?is)</p\s*>', '\n', st) # </p> -> handle paragrpah breaks
	st = re.sub(r'(?is)<[^>]+>', '', st) # to strip garbage html tags
	st = html.unescape(st) # handles spaces, etc
	st = st.replace('\xa0', ' ') # \xa0 is a non breaking space and as far I understand using replace() here vs re.() cleaner/easier for one char
	st = re.sub(r'\r', '', st) # handle return stripping
	st = re.sub(r'\n{3,}', '\n\n', st) # catch any excessive newlines
	return st.strip()

def part_extraction(text: str, start: str, end: str) -> str | None:
	m = re.search(start + r'(.*?)' + end, text, flags=re.I | re.S) # grab 1st block between the two markers very loose with it as it stops at a first match
	return m.group(1) if m else None

def page_parser(raw: str) -> str:
	raw = html.unescape(raw)

	ctg = ''
	pts = ''
	desc = ''
	solved = ''

	# the stable fields in page header to use in extracting
	m = re.search(r'<span class="cat">([^<]+)</span>', raw, re.I)
	if m:
		ctg = m.group(1).strip()

	m = re.search(r'<span class="cost">([^<]+)</span>', raw, re.I)
	if m:
		pts = m.group(1).strip()

	m = re.search(r'<span class="desc">([^<]+)</span>', raw, re.I)
	if m:
		desc = m.group(1).strip()

	m = re.search(r'<span class="author">([^<]+)</span>', raw, re.I)
	if m:
		solved = m.group(1).strip()

	# give pref to a dedicated full description block but catch later in case
	pieces = part_extraction(raw, r'<div class="fullDesc">', r'</div>')
	fill_desc = tags(pieces) if pieces else ''

	# fallback best option i think to try to scan flattened page text to look for the question -> description area
	if not fill_desc:
		t = tags(raw)
		lines = [x.strip() for x in t.splitlines() if x.strip()]

		for i, line in enumerate(lines):
			if 'Format:' in line or ('What is' in line and i > 0):
				start = max(0, i - 1)
				fill_desc = '\n'.join(lines[start:start + 4]).strip()
				break

	header = ' | '.join(x for x in [
		desc,
		f'{ctg} {pts}'.strip(),
		solved
	] if x)

	sepr = '=' * len(header)
	return f'{header}\n{sepr}\n{fill_desc}\n'

def fetch_desc(slug: str) -> str:
	url = f'{BASE_URL}/{slug}'
	req = requests.get(url, timeout=20)
	req.raise_for_status()
	return page_parser(req.text)

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('--challenge', required=False, help='specify chall #/slug')
	ap.add_argument('--list', action='store_true')
	args = ap.parse_args()

	if args.list:
		for n, slug in CHALLS.items():
			print(f'{n:2d}: {slug}')
		return

	if not args.challenge:
		ap.error('--challenge #/slug or --list')

	val = args.challenge.strip().lower()

	if val.isdigit():
		slug = CHALLS.get(int(val))
		if not slug:
			print(f'unknown challenge #: {val}', file=sys.stderr)
			sys.exit(2)
	else:
		slug = val

	try:
		print(fetch_desc(slug))
	except Exception as e:
		print(f'error: {e}', file=sys.stderr)
		sys.exit(1)

if __name__ == '__main__':
	main()