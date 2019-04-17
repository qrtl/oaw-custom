# Copyright 2019 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import SUPERUSER_ID
from odoo import fields, osv
from odoo.tools import  DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _


class procurement_order(models.Model):
    _inherit = "procurement.order"
    _columns = {
        'quant_id': fields.many2one('stock.quant', string="Quant From Sale Line"),
        'lot_id': fields.many2one('stock.production.lot', string="Stock Production lot From Sale Line", help="From Sales Order Line"),
        'is_enforce_qty': fields.boolean('Is Enforce Quantity 1?')
    }
    
    def _run_move_create(self, cr, uid, procurement, context=None):
        """ move are create based on procurment """
        res = super(procurement_order,self)._run_move_create(cr, uid, procurement, context)
        res.update({'quant_id': procurement.quant_id.id, 'lot_id': procurement.lot_id.id}) #Add lot and quant ref on related stock move of procurement order.
        return res
    

    def check_vci_or_mto(self, cr, uid, procurement, context=None):
        model, res_id1 = self.pool['ir.model.data'].get_object_reference(cr,
            uid, 'stock', 'route_warehouse0_mto')
        model, res_id2 = self.pool['ir.model.data'].get_object_reference(cr,
            uid, 'vendor_consignment_stock', 'route_warehouse0_buy_vci')
        res = ''
        for route in procurement.route_ids:
            if route.id == res_id2:
                res = 'vci'
                break  # vci procurement has both vci and mto routes
            elif route.id == res_id1:
                res = 'mto'
        return res

    def _get_po_line_values_from_proc(self, cr, uid, procurement, partner, company, schedule_date, context=None):
        res = super(procurement_order, self)._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context=context)
        type = self.check_vci_or_mto(cr, uid, procurement, context=context)
        if type == 'vci':
            res.update({'lot_id': procurement.lot_id.id,
                        'vci': True,
                        'price_unit': procurement.move_dest_id.quant_id and
                                procurement.move_dest_id.quant_id.\
                                purchase_price_unit
                        })
        elif type == 'mto':
            res.update({'lot_id': procurement.lot_id.id,
                        'mto': True
                        })
        return res
    

    def _get_currency_id(self, cr, uid, type, procurement, partner, context=None):
        if type == 'vci' and procurement.move_dest_id.quant_id:
            res =  procurement.move_dest_id.quant_id.currency_id.id
        elif partner.property_product_pricelist_purchase:
            res = partner.property_product_pricelist_purchase.currency_id.id
        else:
            res = procurement.company_id.currency_id.id
        return res


    def make_po(self, cr, uid, ids, context=None):
        """ Resolve the purchase from procurement, which may result in a new PO creation, a new PO line creation or a quantity change on existing PO line.
        Note that some operations (as the PO creation) are made as SUPERUSER because the current user may not have rights to do it (mto product launched by a sale for example)

        @return: dictionary giving for each procurement its related resolving PO line.
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        po_obj = self.pool.get('purchase.order')
        po_line_obj = self.pool.get('purchase.order.line')
        seq_obj = self.pool.get('ir.sequence')
        pass_ids = []
        linked_po_ids = []
        sum_po_line_ids = []
        for procurement in self.browse(cr, uid, ids, context=context):
            partner = self._get_product_supplier(cr, uid, procurement, context=context)
            if not partner:
                self.message_post(cr, uid, [procurement.id], _('There is no supplier associated to product %s') % (procurement.product_id.name))
                res[procurement.id] = False
            else:
                schedule_date = self._get_purchase_schedule_date(cr, uid, procurement, company, context=context)
                purchase_date = self._get_purchase_order_date(cr, uid, procurement, company, schedule_date, context=context) 
                line_vals = self._get_po_line_values_from_proc(cr, uid, procurement, partner, company, schedule_date, context=context)
                #look for any other draft PO for the same supplier, to attach the new line on instead of creating a new draft one
                available_draft_po_ids = po_obj.search(cr, uid, [
                    ('partner_id', '=', partner.id),
                    ('state', '=', 'draft'),
                    ('picking_type_id', '=', procurement.rule_id.picking_type_id.id),
                    ('location_id', '=', procurement.location_id.id),
                    ('company_id', '=', procurement.company_id.id),
                    ('dest_address_id', '=', procurement.partner_dest_id.id),
                    ],context=context)

                # oscg.  prevent multiple procurements getting merged into one PO.
                # SO line and PO should be one to one relationship for
                # ‘Make To Order’ and ‘Buy VCI’ cases.
                type = self.check_vci_or_mto(cr, uid, procurement, context=context)  # add 160507
                if available_draft_po_ids and not type:  # mod 160507
                    po_id = available_draft_po_ids[0]
                    po_rec = po_obj.browse(cr, uid, po_id, context=context)
                    #if the product has to be ordered earlier those in the existing PO, we replace the purchase date on the order to avoid ordering it too late
                    if datetime.strptime(po_rec.date_order, DEFAULT_SERVER_DATETIME_FORMAT) > purchase_date:
                        po_obj.write(cr, uid, [po_id], {'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
                    #look for any other PO line in the selected PO with same product and UoM to sum quantities instead of creating a new po line
                    available_po_line_ids = po_line_obj.search(cr, uid, [
                        ('order_id', '=', po_id),
                        ('product_id', '=', line_vals['product_id']),
                        ('product_uom', '=', line_vals['product_uom'])
                        ], context=context)
                    if available_po_line_ids:
                        po_line = po_line_obj.browse(cr, uid, available_po_line_ids[0], context=context)
                        po_line_obj.write(cr, SUPERUSER_ID, po_line.id, {'product_qty': po_line.product_qty + line_vals['product_qty']}, context=context)
                        po_line_id = po_line.id
                        sum_po_line_ids.append(procurement.id)
                    else:
                        line_vals.update(order_id=po_id)
                        po_line_id = po_line_obj.create(cr, SUPERUSER_ID, line_vals, context=context)
                        linked_po_ids.append(procurement.id)
                else:  # in case type is vci or mto
                    name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % procurement.name
                    currency_id = self._get_currency_id(cr, uid, type, procurement, partner, context=context)  # oscg
                    po_vals = {
                        'name': name,
                        'is_mto': True if type == 'mto' else False,
                        'origin': procurement.origin,
                        'partner_id': partner.id,
                        'location_id': procurement.location_id.id,
                        'picking_type_id': procurement.rule_id.picking_type_id.id,
                        'pricelist_id': partner.property_product_pricelist_purchase.id,
                        # 'currency_id': partner.property_product_pricelist_purchase and partner.property_product_pricelist_purchase.currency_id.id or procurement.company_id.currency_id.id,
                        'currency_id': currency_id,  # oscg
                        'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'company_id': procurement.company_id.id,
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                        'payment_term_id': partner.property_supplier_payment_term.id or False,
                        'dest_address_id': procurement.partner_dest_id.id,
                    }
                    po_id = self.create_procurement_purchase_order(cr, SUPERUSER_ID, procurement, po_vals, line_vals, context=context)
                    po_line_id = po_obj.browse(cr, uid, po_id, context=context).order_line[0].id
                    pass_ids.append(procurement.id)
                res[procurement.id] = po_line_id
                self.write(cr, uid, [procurement.id], {'purchase_line_id': po_line_id}, context=context)
        if pass_ids:
            self.message_post(cr, uid, pass_ids, body=_("Draft Purchase Order created"), context=context)
        if linked_po_ids:
            self.message_post(cr, uid, linked_po_ids, body=_("Purchase line created and linked to an existing Purchase Order"), context=context)
        if sum_po_line_ids:
            self.message_post(cr, uid, sum_po_line_ids, body=_("Quantity added in existing Purchase Order Line"), context=context)
        return res
