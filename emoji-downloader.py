import argparse
import asyncio
import base64
import os

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

downloadurl = "https://unicode.org/emoji/charts/full-emoji-list.html"
cachefile = "emoji/cache.html"
outdir = "emoji"

async def process_emoji(data, variantstr):
	filepath = os.path.join(outdir, variantstr, data[0] + ".png")
	async with aiofiles.open(filepath, "wb") as file:
		await file.write(base64.decodebytes(data[1]))

async def run(variant, force):
	print("Downloading emoji variant '{}'".format(variant))
	
	# Create output dir
	outdir_full = os.path.join(outdir, variant)
	if not os.path.isdir(outdir_full):
		os.makedirs(outdir_full)
	
	rawhtml = ""
	
	# Check cache, download if needed
	if force or not os.path.isfile(cachefile):
		if force:
			print("Forcing download of html")
		else:
			print("No cache found, downloading html")
			
		async with aiohttp.ClientSession() as session:
			async with session.get(downloadurl) as response:
				rawhtml = await response.text()
				print("Download done ({} bytes)".format(len(rawhtml)))
		
		print("Saving cache {}".format(cachefile))
		async with aiofiles.open(cachefile, "w", encoding="utf8") as file:
			await file.write(rawhtml)
	else:
		print("Loading from cache {}".format(cachefile))
		async with aiofiles.open(cachefile, "r", encoding="utf8") as file:
			rawhtml = await file.read()
	
	soup = BeautifulSoup(rawhtml, "lxml")
	
	# Parse variant column index
	table_headers = soup.select("table tr")[2].select("th a")
	header_index = -1
	for i, header in zip(range(len(table_headers)), table_headers):
		if header.get_text().strip().lower() == variant.lower():
			header_index = i
			break
	
	if header_index < 0:
		raise Exception("Invalid variant (not found in headers)")
	
	rows = soup.select("table tr")
	
	# Parse out emojis
	parsed_emojis = []
	print("Parsing...", end="\r", flush=True)
	
	count = 0
	for row in rows:
		cols = row.select("td")
		if len(cols) < 15:
			continue
		
		a = cols[1].select("a")[0]

		try:
			code = a["name"]
			
			if "miss" in cols[header_index].get("class"):
				print("Skipping missing {} ({})".format(code, cols[14].get_text()))
				continue
			
			data = cols[header_index].select("img")[0]["src"]
			data = data[data.find(",")+1:]
			
			parsed_emojis.append((code, bytearray(data, "utf8")))
			
			count = count + 1
		except IndexError as e:
			print("ERR for {} {}".format(code, row.get_text()))
			raise e
	
	print("Parsing...Done ({} emojis)".format(count))
	
	# Export emojis to PNGs
	print("Exporting...", end="\r", flush=True)
	await asyncio.gather(*[ process_emoji(data, variant) for data in parsed_emojis ])

	print("Exporting...Done")
			
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Downloads and extracts emoji images from {}".format(downloadurl))
	parser.add_argument("variant", metavar="variant", nargs=1, help="Variant to download (table column header text from {}".format(downloadurl))
	parser.add_argument("--forcefetch", action="store_true", help="Forces (re)download of html data, otherwise existing cache if found is used for extracting images.")
	args = parser.parse_args()
	asyncio.run(run(args.variant[0], args.forcefetch))
