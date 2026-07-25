import sys
import io
import re
sys.stdout.reconfigure(encoding='utf-8')
file_path = 'C:/Users/parth/Downloads/Switch_craft-4264d7ed964f24831e81c39f4a65c48720d19677 (1)/Switch_craft-4264d7ed964f24831e81c39f4a65c48720d19677/custom-cart-sync.js'
with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

# We want to replace everything from `document.addEventListener('click', function(e) {` 
# up to the end of the file.

new_interceptors = """  // Intercept Next.js navigation for Cart Editing to force a hard reload to ROOT
  document.addEventListener('click', function(e) {
      const link = e.target.closest('a');
      if (link && link.href) {
          const url = new URL(link.href, window.location.origin);
          if (url.searchParams.has('cart')) {
              e.preventDefault();
              e.stopPropagation();
              const cartId = url.searchParams.get('cart');
              localStorage.setItem('sc_editing_item_id', cartId);
              window.location.href = '/?cart=' + cartId;
          }
      }
  }, true);

// Intercept Next.js router.push via history.pushState
const originalPushState = window.history.pushState;
window.history.pushState = function(state, unused, url) {
    if (url && typeof url === 'string') {
        try {
            const parsedUrl = new URL(url, window.location.origin);
            if (parsedUrl.searchParams.has('cart')) {
                const cartId = parsedUrl.searchParams.get('cart');
                localStorage.setItem('sc_editing_item_id', cartId);
                window.location.href = '/?cart=' + cartId;
                return; // abort SPA pushState
            }
        } catch (e) {
            console.error('[CartSync] Error intercepting pushState:', e);
        }
    }
    return originalPushState.apply(this, arguments);
};
"""

idx = code.find("document.addEventListener('click', function(e) {")
if idx != -1:
    code = code[:idx] + new_interceptors
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Replaced interceptors with hard-reload logic!")
else:
    print("Could not find start of interceptors.")
