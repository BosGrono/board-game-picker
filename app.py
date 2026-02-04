# --- ROBUST BGG FETCH WITH RETRIES ---
def get_bgg_image(bgg_id):
    if not bgg_id or pd.isna(bgg_id):
        return None
    
    # Clean the ID: Remove decimals or commas
    try:
        clean_id = str(int(float(bgg_id)))
    except:
        return None

    headers = {'User-Agent': 'BoardGamePickerApp/2.0'}
    url = f"https://boardgamegeek.com/xmlapi2/thing?id={clean_id}"
    
    # Attempt up to 3 times in case of BGG "202 Accepted" busy signal
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                # Check if the API actually returned an item
                item = root.find("item")
                if item is not None:
                    image_node = item.find("image")
                    if image_node is not None:
                        return image_node.text
                    thumb_node = item.find("thumbnail")
                    if thumb_node is not None:
                        return thumb_node.text
                return None # Item found but no image tags
            
            elif response.status_code == 202:
                # BGG is processing the request, wait and retry
                time.sleep(2)
                continue
            else:
                return None
        except Exception:
            time.sleep(1)
            continue
            
    return None
