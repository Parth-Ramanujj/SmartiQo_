import glob
import os

INJECT_SCRIPT = """
<script id="sc-early-hydrate">
  // SWITCHCRAFT: Early Hydration for Cart Editing
  (function() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const cartParamId = urlParams.get('cart');
      if (!cartParamId) return;
      
      let item = null;
      let allItems = [];
      
      const possibleKeys = ['persist:root'];
      for (const k of possibleKeys) {
        const raw = localStorage.getItem(k);
        if (!raw) continue;
        try {
            const parsed = JSON.parse(raw);
            if (parsed.cartData) {
              const cd = typeof parsed.cartData === 'string' ? JSON.parse(parsed.cartData) : parsed.cartData;
              if (cd.cartItems && cd.cartItems.length > 0) { allItems = cd.cartItems; break; }
            }
            if (parsed.cartItems && parsed.cartItems.length > 0) { allItems = parsed.cartItems; break; }
        } catch(e){}
      }
      item = allItems.find(i => i.id === cartParamId || i.productSequence === cartParamId);
    
    // Fallbacks for Dashboard Edit
    if (!item && cartParamId) {
        try {
            let localOrders = JSON.parse(localStorage.getItem('sc_local_orders') || '[]');
            let match = localOrders.find(i => i.payload && (i.payload.orderId === cartParamId));
            if (match && match.rawCartData) {
                item = {
                    cartData: match.rawCartData,
                    dropped: match.rawDropped || []
                };
            }
        } catch(e){}
    }

      if (item) {
        const persistStr = localStorage.getItem('persist:root');
        if (persistStr) {
           const persist = JSON.parse(persistStr);
           let cartDataState = persist.cartData ? JSON.parse(persist.cartData) : {};
           cartDataState.cartData = item.cartData || item.rawCartData || item;
           persist.cartData = JSON.stringify(cartDataState);
           localStorage.setItem('persist:root', JSON.stringify(persist));
           console.log('[Early Hydrate] Injected cart item', cartParamId, 'into persist:root');
        }
      }
    } catch (e) {
      console.error('[Early Hydrate Error]', e);
    }
  })();
</script>
"""

loader_html = """
<style>
  /* Global loader styles */
  #sc-global-loader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: #000000;
    z-index: 999999;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: opacity 0.5s ease-out;
  }
  .sc-spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255, 255, 255, 0.1);
    border-top-color: #00a8ff;
    border-radius: 50%;
    animation: sc-spin 1s linear infinite;
  }
  @keyframes sc-spin {
    to { transform: rotate(360deg); }
  }
  .sc-loader-text {
    margin-top: 20px;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    letter-spacing: 1px;
  }
</style>
<div id="sc-global-loader">
  <div class="sc-spinner"></div>
  <div class="sc-loader-text">Loading SmartiQo...</div>
</div>
<script>
  window.addEventListener('load', function() {
    const loader = document.getElementById('sc-global-loader');
    if (loader) {
      loader.style.opacity = '0';
      setTimeout(() => loader.remove(), 500);
    }
  });
</script>
"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html_text = f.read()

    changed = False
    
    if "<script id=\"sc-early-hydrate\">" not in html_text and "<head>" in html_text:
        html_text = html_text.replace("<head>", "<head>\\n" + INJECT_SCRIPT, 1)
        changed = True
        
    if "sc-global-loader" not in html_text and "<body>" in html_text:
        html_text = html_text.replace("<body>", "<body>\\n" + loader_html, 1)
        changed = True
        
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_text)
        print(f"Modified: {filepath}")

if __name__ == '__main__':
    html_files = glob.glob('*.html') + glob.glob('pages/*.html')
    for f in html_files:
        process_file(f)
    print("Done statically injecting into all HTML files.")
