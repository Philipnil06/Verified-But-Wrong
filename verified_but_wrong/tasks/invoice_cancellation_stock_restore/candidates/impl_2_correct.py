def cancel_invoice(invoice, inventory):
    if not invoice or invoice.get('status')=='paid': return {'status':'error','message':'invalid','invoice':invoice,'inventory':inventory}
    inv=invoice.copy(); inv['status']='cancelled'; stock={k:v.copy() for k,v in inventory.items()}
    for line in invoice.get('lines',[]):
        item=stock[line['sku']]; qty=line['qty']; item['available']+=qty; item['reserved']-=qty
    return {'status':'ok','message':'cancelled','invoice':inv,'inventory':stock}
