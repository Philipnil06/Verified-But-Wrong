def invoice(status='open'): return {'invoice_id':'inv1','status':status,'lines':[{'sku':'sku1','qty':2}]}
def inventory(): return {'sku1':{'available':5,'reserved':2}}
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def run_tests(fn):
    tests=[]; out=fn(invoice(),inventory()); tests.append(res('open_cancel_ok', out['status']=='ok' and out['invoice']['status']=='cancelled','ok',str(out)))
    out=fn(invoice('paid'),inventory()); tests.append(res('paid_invoice_fails', out['status']=='error','error',str(out)))
    fails=[t for t in tests if not t['passed']]; return {'passed':not fails,'passed_count':len(tests)-len(fails),'failed_count':len(fails),'failures':[f"{t['name']}: expected {t['expected']}, got {t['actual']}" for t in fails],'tests':tests}
