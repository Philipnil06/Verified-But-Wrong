def cancel_invoice(invoice, inventory):
    if not invoice or invoice.get('status')=='paid': return {'status':'error','message':'invalid','invoice':invoice,'inventory':inventory}
    inv=invoice.copy(); inv['status']='cancelled'; return {'status':'ok','message':'cancelled','invoice':inv,'inventory':{k:v.copy() for k,v in inventory.items()}}
