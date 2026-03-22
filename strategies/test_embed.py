from playwright.sync_api import sync_playwright

def get_embed():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://tw.tradingview.com/script/PwVoxMSo-Machine-Learning-Pivot-Points-KNN-SS/')
        
        # Check for iframes
        iframes = page.query_selector_all('iframe')
        print(f'Found {len(iframes)} iframes')
        for frame in iframes:
            try:
                print('Iframe SRC:', frame.get_attribute('src'))
            except Exception as e:
                print(e)
                
        # Check for Canvas
        canvases = page.query_selector_all('canvas')
        print(f'Found {len(canvases)} canvases')
        
        # Check for any specific chart container
        js_embeds = page.query_selector_all('.tv-chart-view__widget')
        print(f'Found {len(js_embeds)} widget containers')
        
        browser.close()

if __name__ == '__main__':
    get_embed()
