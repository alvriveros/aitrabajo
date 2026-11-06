import sys
from playwright.sync_api import sync_playwright
def esperar(p):
    p.wait_for_timeout(700); p.wait_for_selector('[data-testid="stStatusWidget"]',state="detached",timeout=15000); p.wait_for_timeout(1500)
with sync_playwright() as pw:
    b=pw.chromium.launch(); print(b.version)
    p=b.new_page(viewport={"width":772,"height":923})
    p.goto("http://127.0.0.1:8502"); p.wait_for_selector('[data-testid="stMetricValue"]',timeout=30000)
    p.evaluate("""(t)=>{const f=new File([t],'oficina-00-06-prediccion.json',{type:'application/json'});const d=new DataTransfer();d.items.add(f);const i=document.querySelector('input[type=file]');i.files=d.files;i.dispatchEvent(new Event('change',{bubbles:true}));}""", open(sys.argv[1]).read()); esperar(p)
    p.locator('[role="slider"]').focus()
    for k,n,name in (("ArrowLeft",6,"0"),("ArrowRight",2,"2"),("ArrowRight",1,"2.16"),("ArrowRight",2,"4"),("ArrowRight",1,"4.6")):
        for _ in range(n): p.keyboard.press(k); esperar(p)
        p.locator('[data-testid="stVegaLiteChart"]').first.screenshot(path=f"/root/w/rep2-{name}.png")
        print(name,p.locator('[data-testid="stMetricValue"]').all_inner_texts())
