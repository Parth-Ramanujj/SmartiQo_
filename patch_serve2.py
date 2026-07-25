import sys
import re

file_path = 'C:/Users/parth/Downloads/Switch_craft-4264d7ed964f24831e81c39f4a65c48720d19677 (1)/Switch_craft-4264d7ed964f24831e81c39f4a65c48720d19677/serve.py'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

new_inject_script = '''                # INJECT CART SYNC LOGIC INTO HEAD
                INJECT_SCRIPT = """<script>
// Global Fetch Interceptor to cache Dashboard Orders
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    const response = await originalFetch.apply(this, args);
    try {
        const url = args[0];
        if (typeof url === 'string' && url.includes('script.google.com') && url.includes('action=getOrders')) {
            const clone = response.clone();
            clone.json().then(data => {
                if (data && data.orders) {
                    localStorage.setItem('sc_fetched_dashboard_orders', JSON.stringify(data.orders));
                    console.log('[FetchInterceptor] Cached orders for edit hydration.');
                }
            }).catch(e => {});
        }
    } catch(e) {}
    return response;
};

(function forceRestoreCartItemToPersist() {
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const cartParamId = urlParams.get('cart');
    let editId = localStorage.getItem('sc_editing_item_id') || cartParamId;
    if (!editId) return;

    let item = null;
    let rawItemData = localStorage.getItem('sc_editing_item_data');
    if (rawItemData) {
      try { item = JSON.parse(rawItemData); } catch (e) {}
    }

    if (!item && cartParamId) {
      const possibleKeys = ['persist:root', 'persist:cartData', 'persist:cart'];
      let allItems = [];
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
    }
    
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
        } catch(e) {}
    }

    if (item) {
        localStorage.setItem('sc_editing_item_id', editId);
        localStorage.setItem('sc_editing_item_data', JSON.stringify(item));
    }

    if (!item || (!item.cartData && !item.rawCartData)) return;

    const keys = ['persist:root', 'persist:cartData', 'persist:cart'];
    for (const k of keys) {
      const raw = localStorage.getItem(k);
      if (!raw) continue;
      try {
          const parsed = JSON.parse(raw);
          if (parsed.cartData) {
            let cd = typeof parsed.cartData === 'string' ? JSON.parse(parsed.cartData) : parsed.cartData;
            
            const currentItemStr = JSON.stringify(cd.cartData);
            const newItemStr = JSON.stringify(item.rawCartData || item.cartData);
            
            if (currentItemStr !== newItemStr) {
                cd.cartData = item.rawCartData || item.cartData; // FIXED PROPERTY
                cd.droppedItems = item.rawDropped || item.dropped || [];
                cd.quantity = item.quantity || 1;
                cd.totalPrice = item.totalPrice || 0;
                parsed.cartData = typeof parsed.cartData === 'string' ? JSON.stringify(cd) : cd;
                localStorage.setItem(k, JSON.stringify(parsed));
                console.log('[CartSync] Head force-injected item into ' + k);
            }
            break;
          }
      } catch(e) {}
    }
  } catch (e) {
    console.error('[CartSync] Head force restore failed:', e);
  }
})();
</script>"""'''

code = re.sub(r'# INJECT CART SYNC LOGIC INTO HEAD\n                INJECT_SCRIPT = """<script>.*?</script>"""', new_inject_script, code, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Patched serve.py with correct INJECT_SCRIPT')
