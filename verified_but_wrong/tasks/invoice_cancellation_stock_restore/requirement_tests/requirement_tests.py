def invoice(status='open'): return {'invoice_id':'inv1','status':status,'lines':[{'sku':'sku1','qty':2}]}
def inventory(): return {'sku1':{'available':5,'reserved':2}}
def res(name, passed, expected, actual): return {'name':name,'passed':bool(passed),'expected':expected,'actual':actual}
def valid(fn):
    out=fn(invoice(),inventory()); return res('Valid cancellation succeeds', out['status']=='ok','ok',str(out))
def restore(fn):
    out=fn(invoice(),inventory()); return res('Reserved inventory must be restored when invoice is cancelled', out['inventory']['sku1']['available']==7,'restored',str(out))
def status(fn):
    out=fn(invoice(),inventory()); return res('Invoice status must update to cancelled', out['invoice']['status']=='cancelled','cancelled',str(out))
def paid(fn):
    out=fn(invoice('paid'),inventory()); return res('Paid invoices cannot be cancelled', out['status']=='error','error',str(out))
def reserved(fn):
    out=fn(invoice(),inventory()); return res('Inventory reserved count must decrease', out['inventory']['sku1']['reserved']==0,'reserved 0',str(out))
REQUIREMENT_TESTS={'Valid cancellation succeeds':valid,'Reserved inventory must be restored when invoice is cancelled':restore,'Invoice status must update to cancelled':status,'Paid invoices cannot be cancelled':paid,'Inventory reserved count must decrease':reserved}
